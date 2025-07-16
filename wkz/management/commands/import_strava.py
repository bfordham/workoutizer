import csv
import json
import os
import shutil
import gzip
import tempfile
from datetime import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files import File
from django.utils.dateparse import parse_datetime
from wkz.models import Activity, Sport, ActivityPhoto, Traces
from wkz.utils.sport_mapping import SportMapper
from wkz.io.file_importer import _parse_single_file, _save_single_parsed_file_to_db
from wkz.tools.utils import calc_md5
from pathlib import Path
from wkz import models


class Command(BaseCommand):
    help = 'Import activities from Strava export data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='Username to import activities for'
        )
        parser.add_argument(
            '--strava-dir',
            type=str,
            default='strava',
            help='Directory containing Strava export data (default: strava)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing'
        )
        parser.add_argument(
            '--process-gps',
            action='store_true',
            help='Process GPS files for existing activities that don\'t have GPS data'
        )

    def handle(self, *args, **options):
        username = options['username']
        strava_dir = options['strava_dir']
        dry_run = options['dry_run']
        process_gps = options['process_gps']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist')
            )
            return

        activities_csv = os.path.join(strava_dir, 'activities.csv')
        if not os.path.exists(activities_csv):
            self.stdout.write(
                self.style.ERROR(f'Activities CSV not found at {activities_csv}')
            )
            return

        activities_dir = os.path.join(strava_dir, 'activities')
        media_dir = os.path.join(strava_dir, 'media')

        self.stdout.write(f'Importing Strava data for user: {username}')
        self.stdout.write(f'Source directory: {strava_dir}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be imported'))

        imported_count = 0
        skipped_count = 0
        error_count = 0
        gps_processed_count = 0

        with open(activities_csv, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                try:
                    result = self._import_activity(user, row, strava_dir, dry_run, process_gps)
                    if result == 'imported':
                        imported_count += 1
                    elif result == 'skipped':
                        skipped_count += 1
                    elif result == 'gps_processed':
                        gps_processed_count += 1
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'Error importing activity {row.get("Activity ID", "Unknown")}: {str(e)}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Import complete. Imported: {imported_count}, '
                f'Skipped: {skipped_count}, GPS Processed: {gps_processed_count}, Errors: {error_count}'
            )
        )

    def _import_activity(self, user, row, strava_dir, dry_run, process_gps=False):
        """Import a single activity from CSV row"""
        activity_id = row.get('Activity ID')
        if not activity_id:
            raise ValueError('Missing Activity ID')

        # Check if activity already exists
        existing = Activity.objects.filter(
            user=user,
            external_id=activity_id,
            external_source='strava'
        ).first()
        
        if existing:
            if process_gps and not existing.trace_file:
                # Process GPS file for existing activity without GPS data
                self.stdout.write(f'Processing GPS for existing activity: {activity_id}')
                
                # Import GPS file if it exists
                self._import_gps_file(existing, row, strava_dir)
                
                return 'gps_processed'
            else:
                self.stdout.write(f'Skipping existing activity: {activity_id}')
                return 'skipped'

        # Parse date
        date_str = row.get('Activity Date')
        if not date_str:
            raise ValueError('Missing Activity Date')
        
        # Strava exports use format like "Dec 15, 2023, 10:30:00 AM"
        try:
            # Try parsing as ISO format first
            date = parse_datetime(date_str)
            if not date:
                # Try parsing Strava's format
                date = datetime.strptime(date_str, "%b %d, %Y, %I:%M:%S %p")
        except ValueError:
            raise ValueError(f'Could not parse date: {date_str}')

        # Map sport
        activity_type = row.get('Activity Type', 'Workout')
        sport = SportMapper.get_or_create_sport_for_user(activity_type, user)

        # Parse numeric fields
        # NOTE: CSV has duplicate Distance columns - we want the km value, not meters
        # Since csv.DictReader only keeps the last duplicate, we need to parse manually
        distance_km = self._parse_distance_from_row(row)
        duration = self._parse_duration(row.get('Moving Time') or row.get('Elapsed Time'))
        elevation_gain = self._parse_decimal(row.get('Elevation Gain'))
        average_heart_rate = self._parse_int(row.get('Average Heart Rate'))
        max_heart_rate = self._parse_int(row.get('Max Heart Rate'))
        calories = self._parse_int(row.get('Calories'))

        if dry_run:
            self.stdout.write(
                f'Would import: {row.get("Activity Name", "Unnamed")} '
                f'({activity_type}) on {date.strftime("%Y-%m-%d")}'
            )
            return 'imported'

        # Create activity
        activity = Activity.objects.create(
            user=user,
            name=row.get('Activity Name', 'Imported Activity'),
            sport=sport,
            date=date,
            duration=duration,
            distance=distance_km,
            description=row.get('Activity Description', ''),
            notes=self._build_notes(row),
            external_id=activity_id,
            external_source='strava',
            activity_type=activity_type,
            average_heart_rate=average_heart_rate,
            max_heart_rate=max_heart_rate,
            calories=calories,
        )

        self.stdout.write(
            f'Imported activity: {activity.name} ({activity_type}) - {activity.date.strftime("%Y-%m-%d")}'
        )

        # Import photos if they exist
        self._import_photos(activity, activity_id, strava_dir)

        # Import GPS file if it exists
        self._import_gps_file(activity, row, strava_dir)

        return 'imported'

    def _parse_distance_from_row(self, row):
        """Parse distance from CSV row, handling duplicate column names"""
        # The CSV has two Distance columns - the first is km, second is meters
        # csv.DictReader only keeps the last one, so we need to be smarter
        
        # Try to get a reasonable distance value
        # Look for values that make sense as km (typically 0.1 to 200 km for most activities)
        distance_str = row.get('Distance', '')
        if not distance_str or distance_str == '--':
            return None
            
        try:
            distance_val = float(str(distance_str).replace(',', ''))
            
            # If the value is very large (>500), it's probably in meters, convert to km
            if distance_val > 500:
                return Decimal(distance_val / 1000)  # Convert meters to km
            else:
                return Decimal(distance_val)  # Already in km
        except (ValueError, TypeError):
            return None

    def _parse_decimal(self, value):
        """Parse decimal value, handling various formats"""
        if not value or value == '--':
            return None
        try:
            # Remove units and convert
            value = str(value).replace(',', '').replace(' km', '').replace(' mi', '').replace(' m', '')
            return Decimal(value) if value else None
        except (ValueError, TypeError):
            return None

    def _parse_duration(self, value):
        """Parse duration in seconds from various formats and return timedelta"""
        if not value or value == '--':
            return None
        try:
            # Handle format like "1:23:45" or "23:45" or just seconds
            if ':' in str(value):
                parts = str(value).split(':')
                if len(parts) == 3:  # H:M:S
                    total_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                elif len(parts) == 2:  # M:S
                    total_seconds = int(parts[0]) * 60 + int(parts[1])
                else:
                    total_seconds = int(float(value))
            else:
                total_seconds = int(float(value))
            
            # Return timedelta object
            from datetime import timedelta
            return timedelta(seconds=total_seconds)
        except (ValueError, TypeError):
            return None

    def _parse_int(self, value):
        """Parse integer value"""
        if not value or value == '--':
            return None
        try:
            return int(float(str(value).replace(',', '')))
        except (ValueError, TypeError):
            return None

    def _build_notes(self, row):
        """Build notes field from various CSV columns"""
        notes_parts = []
        
        # Add description if different from activity description
        description = row.get('Activity Description', '')
        if description and description.strip():
            notes_parts.append(f"Description: {description}")

        # Add gear info
        gear = row.get('Activity Gear', '')
        if gear and gear.strip():
            notes_parts.append(f"Gear: {gear}")

        # Add any other interesting fields
        filename = row.get('Filename', '')
        if filename and filename.strip():
            notes_parts.append(f"Original file: {filename}")

        return '\n'.join(notes_parts) if notes_parts else None

    def _import_photos(self, activity, activity_id, strava_dir):
        """Import photos for an activity"""
        media_dir = os.path.join(strava_dir, 'media')
        if not os.path.exists(media_dir):
            return

        # Look for photos with this activity ID
        photo_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        photo_count = 0
        
        for filename in os.listdir(media_dir):
            if activity_id in filename and any(filename.lower().endswith(ext) for ext in photo_extensions):
                source_path = os.path.join(media_dir, filename)
                try:
                    with open(source_path, 'rb') as photo_file:
                        django_file = File(photo_file)
                        ActivityPhoto.objects.create(
                            activity=activity,
                            image=django_file,
                            caption=f'Imported from Strava'
                        )
                        photo_count += 1
                        self.stdout.write(f'  Added photo: {filename}')
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'  Could not import photo {filename}: {str(e)}')
                    )

        if photo_count > 0:
            self.stdout.write(f'  Imported {photo_count} photos')

    def _import_gps_file(self, activity, row, strava_dir):
        """Import GPS file for an activity"""
        filename = row.get('Filename', '')
        if not filename:
            return

        # Handle both absolute paths and relative paths
        if filename.startswith('activities/'):
            gps_file_path = os.path.join(strava_dir, filename)
        else:
            gps_file_path = os.path.join(strava_dir, 'activities', filename)

        if not os.path.exists(gps_file_path):
            self.stdout.write(f'  GPS file not found: {gps_file_path}')
            return

        temp_file_path = None
        try:
            # Handle compressed files
            if filename.endswith('.gz'):
                # Get the file extension without .gz
                base_name = os.path.basename(filename[:-3])
                
                # Decompress file to a temporary location
                with tempfile.NamedTemporaryFile(suffix=f'_{base_name}', delete=False) as temp_file:
                    with gzip.open(gps_file_path, 'rb') as gz_file:
                        temp_file.write(gz_file.read())
                    temp_file_path = temp_file.name
            else:
                temp_file_path = gps_file_path

            # Parse the GPS file using existing parser
            file_path = Path(temp_file_path)
            md5sum = calc_md5(file_path)
            parsed_data = _parse_single_file(file_path, Path(strava_dir), md5sum)
            
            if parsed_data:
                # Save parsed data to database (this handles traces, laps, and activities)
                _save_single_parsed_file_to_db(parsed_data, models, False, False)
                
                # Find the trace that was just created
                trace = models.Traces.objects.get(md5sum=parsed_data.md5sum)
                
                # Link the trace to the activity
                activity.trace_file = trace
                activity.save()
                
                self.stdout.write(f'  Imported GPS data: {filename}')
            else:
                self.stdout.write(f'  Failed to parse GPS file: {filename}')

        except Exception as e:
            self.stdout.write(f'  Error importing GPS file {filename}: {str(e)}')
        finally:
            # Clean up temporary file if created
            if filename.endswith('.gz') and temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)