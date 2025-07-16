import json
from django.core.management.base import BaseCommand
from wkz.models import Sport


class Command(BaseCommand):
    help = 'Populate database with comprehensive sports from Strava and other sources'

    def handle(self, *args, **options):
        sports_data = [
            # Cardio/Running
            {
                'name': 'Running', 'category': 'Cardio', 'icon': 'fa-running', 'color': '#FF6B6B',
                'has_distance': True, 'evaluates_for_awards': True,
                'external_mappings': json.dumps({
                    'strava': ['Run', 'VirtualRun', 'TrailRun']
                })
            },
            {
                'name': 'Trail Running', 'category': 'Cardio', 'icon': 'fa-mountain', 'color': '#8B4513',
                'has_distance': True, 'evaluates_for_awards': True,
                'external_mappings': json.dumps({'strava': ['TrailRun']})
            },
            {
                'name': 'Walking', 'category': 'Cardio', 'icon': 'fa-walking', 'color': '#98D8C8',
                'has_distance': True, 'evaluates_for_awards': True,
                'external_mappings': json.dumps({'strava': ['Walk', 'Hike']})
            },
            {
                'name': 'Hiking', 'category': 'Cardio', 'icon': 'fa-hiking', 'color': '#67B26F',
                'has_distance': True, 'evaluates_for_awards': True,
                'external_mappings': json.dumps({'strava': ['Hike']})
            },

            # Cycling
            {
                'name': 'Cycling', 'category': 'Cardio', 'icon': 'fa-bicycle', 'color': '#4ECDC4',
                'has_distance': True, 'evaluates_for_awards': True,
                'external_mappings': json.dumps({
                    'strava': ['Ride', 'VirtualRide', 'EBikeRide', 'Handcycle']
                })
            },
            {
                'name': 'Mountain Biking', 'category': 'Cardio', 'icon': 'fa-mountain', 'color': '#8B4513',
                'has_distance': True, 'evaluates_for_awards': True,
                'external_mappings': json.dumps({'strava': ['MountainBikeRide']})
            },
            {
                'name': 'Indoor Cycling', 'category': 'Cardio', 'icon': 'fa-bicycle', 'color': '#FF8C42',
                'has_distance': False, 'evaluates_for_awards': False,
                'external_mappings': json.dumps({'strava': ['VirtualRide']})
            },

            # Water Sports
            {
                'name': 'Swimming', 'category': 'Water', 'icon': 'fa-swimmer', 'color': '#0077BE',
                'has_distance': True, 'evaluates_for_awards': True,
                'external_mappings': json.dumps({'strava': ['Swim']})
            },
            {
                'name': 'Open Water Swimming', 'category': 'Water', 'icon': 'fa-water', 'color': '#006994',
                'has_distance': True, 'evaluates_for_awards': True,
                'external_mappings': json.dumps({'strava': ['Swim']})
            },
            {
                'name': 'Kayaking', 'category': 'Water', 'icon': 'fa-ship', 'color': '#2E86AB',
                'has_distance': True, 'evaluates_for_awards': True,
                'external_mappings': json.dumps({'strava': ['Kayaking', 'Canoeing']})
            },
            {
                'name': 'Rowing', 'category': 'Water', 'icon': 'fa-ship', 'color': '#A23B72',
                'has_distance': True, 'evaluates_for_awards': True,
                'external_mappings': json.dumps({'strava': ['Rowing']})
            },
            {
                'name': 'Stand Up Paddleboarding', 'category': 'Water', 'icon': 'fa-water', 'color': '#F18F01',
                'has_distance': True, 'evaluates_for_awards': True,
                'external_mappings': json.dumps({'strava': ['StandUpPaddling']})
            },
            {
                'name': 'Surfing', 'category': 'Water', 'icon': 'fa-water', 'color': '#00A8CC',
                'has_distance': False, 'evaluates_for_awards': False,
                'external_mappings': json.dumps({'strava': ['Surfing']})
            },

            # Strength & Fitness
            {
                'name': 'Weight Training', 'category': 'Strength', 'icon': 'fa-dumbbell', 'color': '#D64545',
                'has_distance': False, 'evaluates_for_awards': False,
                'external_mappings': json.dumps({'strava': ['WeightTraining', 'Workout']})
            },
            {
                'name': 'Crossfit', 'category': 'Strength', 'icon': 'fa-dumbbell', 'color': '#FF6B35',
                'has_distance': False, 'evaluates_for_awards': False,
                'external_mappings': json.dumps({'strava': ['Crossfit', 'Workout']})
            },
            {
                'name': 'Yoga', 'category': 'Flexibility', 'icon': 'fa-leaf', 'color': '#7209B7',
                'has_distance': False, 'evaluates_for_awards': False,
                'external_mappings': json.dumps({'strava': ['Yoga']})
            },
            {
                'name': 'Pilates', 'category': 'Flexibility', 'icon': 'fa-leaf', 'color': '#A663CC',
                'has_distance': False, 'evaluates_for_awards': False,
                'external_mappings': json.dumps({'strava': ['Pilates', 'Workout']})
            },

            # Winter Sports
            {
                'name': 'Skiing', 'category': 'Winter', 'icon': 'fa-skiing', 'color': '#E8F4F8',
                'has_distance': True, 'evaluates_for_awards': True,
                'external_mappings': json.dumps({'strava': ['AlpineSki', 'BackcountrySki']})
            },
            {
                'name': 'Snowboarding', 'category': 'Winter', 'icon': 'fa-snowboarding', 'color': '#FFD23F',
                'has_distance': True, 'evaluates_for_awards': True,
                'external_mappings': json.dumps({'strava': ['Snowboard']})
            },
            {
                'name': 'Cross Country Skiing', 'category': 'Winter', 'icon': 'fa-skiing-nordic', 'color': '#B8860B',
                'has_distance': True, 'evaluates_for_awards': True,
                'external_mappings': json.dumps({'strava': ['NordicSki']})
            },
            {
                'name': 'Ice Skating', 'category': 'Winter', 'icon': 'fa-skating', 'color': '#87CEEB',
                'has_distance': True, 'evaluates_for_awards': True,
                'external_mappings': json.dumps({'strava': ['IceSkate']})
            },

            # Team Sports
            {
                'name': 'Soccer', 'category': 'Sports', 'icon': 'fa-futbol', 'color': '#228B22',
                'has_distance': False, 'evaluates_for_awards': False,
                'external_mappings': json.dumps({'strava': ['Soccer', 'Football']})
            },
            {
                'name': 'Basketball', 'category': 'Sports', 'icon': 'fa-basketball-ball', 'color': '#FF8C00',
                'has_distance': False, 'evaluates_for_awards': False,
                'external_mappings': json.dumps({'strava': ['Basketball']})
            },
            {
                'name': 'Tennis', 'category': 'Sports', 'icon': 'fa-table-tennis', 'color': '#FFFF00',
                'has_distance': False, 'evaluates_for_awards': False,
                'external_mappings': json.dumps({'strava': ['Tennis']})
            },
            {
                'name': 'Golf', 'category': 'Sports', 'icon': 'fa-golf-ball', 'color': '#7CB342',
                'has_distance': False, 'evaluates_for_awards': False,
                'external_mappings': json.dumps({'strava': ['Golf']})
            },

            # Other Activities
            {
                'name': 'Rock Climbing', 'category': 'Adventure', 'icon': 'fa-mountain', 'color': '#8D6E63',
                'has_distance': False, 'evaluates_for_awards': False,
                'external_mappings': json.dumps({'strava': ['RockClimbing']})
            },
            {
                'name': 'Elliptical', 'category': 'Cardio', 'icon': 'fa-running', 'color': '#9C27B0',
                'has_distance': False, 'evaluates_for_awards': False,
                'external_mappings': json.dumps({'strava': ['Elliptical']})
            },
            {
                'name': 'Stretching', 'category': 'Flexibility', 'icon': 'fa-leaf', 'color': '#4CAF50',
                'has_distance': False, 'evaluates_for_awards': False,
                'external_mappings': json.dumps({'strava': ['Workout']})
            },
            {
                'name': 'Other', 'category': 'Other', 'icon': 'fa-question-circle', 'color': '#9E9E9E',
                'has_distance': False, 'evaluates_for_awards': False,
                'external_mappings': json.dumps({'strava': ['Workout']})
            },
        ]

        created_count = 0
        updated_count = 0

        for sport_data in sports_data:
            sport, created = Sport.objects.get_or_create(
                name=sport_data['name'],
                user=None,  # System sports
                defaults={
                    **sport_data,
                    'is_system_sport': True,
                    'mapping_name': sport_data['name'].lower().replace(' ', '_')
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"Created sport: {sport.name}")
            else:
                # Update existing sport with new data
                for key, value in sport_data.items():
                    setattr(sport, key, value)
                sport.is_system_sport = True
                sport.save()
                updated_count += 1
                self.stdout.write(f"Updated sport: {sport.name}")

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated sports database. '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )