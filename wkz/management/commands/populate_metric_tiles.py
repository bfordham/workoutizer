from django.core.management.base import BaseCommand
from wkz.models import MetricTile


class Command(BaseCommand):
    help = 'Populate database with default metric tiles'

    def handle(self, *args, **options):
        tiles_data = [
            # Basic activity metrics
            {
                'name': 'Total Distance',
                'key': 'total_distance',
                'title': 'Distance',
                'description': 'Total distance covered',
                'icon': 'fa-road',
                'color': '#4ECDC4',
                'metric_type': 'total',
                'data_field': 'distance',
                'unit': 'km',
                'format_type': 'decimal',
                'decimal_places': 2,
                'applicable_to': 'all'
            },
            {
                'name': 'Total Duration',
                'key': 'total_duration',
                'title': 'Duration',
                'description': 'Total time spent on activities',
                'icon': 'fa-clock',
                'color': '#FF6B6B',
                'metric_type': 'total',
                'data_field': 'duration',
                'unit': 'hours',
                'format_type': 'duration',
                'decimal_places': 0,
                'applicable_to': 'all'
            },
            {
                'name': 'Activity Count',
                'key': 'activity_count',
                'title': 'Activities',
                'description': 'Number of activities',
                'icon': 'fa-hashtag',
                'color': '#45B7D1',
                'metric_type': 'count',
                'data_field': 'id',
                'unit': '',
                'format_type': 'number',
                'decimal_places': 0,
                'applicable_to': 'all'
            },
            {
                'name': 'Total Calories',
                'key': 'total_calories',
                'title': 'Calories',
                'description': 'Total calories burned',
                'icon': 'fa-fire',
                'color': '#FF8C42',
                'metric_type': 'total',
                'data_field': 'calories',
                'unit': 'kcal',
                'format_type': 'number',
                'decimal_places': 0,
                'applicable_to': 'all'
            },
            
            # Average metrics
            {
                'name': 'Average Distance',
                'key': 'avg_distance',
                'title': 'Avg Distance',
                'description': 'Average distance per activity',
                'icon': 'fa-route',
                'color': '#96CEB4',
                'metric_type': 'average',
                'data_field': 'distance',
                'unit': 'km',
                'format_type': 'decimal',
                'decimal_places': 2,
                'applicable_to': 'all'
            },
            {
                'name': 'Average Duration',
                'key': 'avg_duration',
                'title': 'Avg Duration',
                'description': 'Average duration per activity',
                'icon': 'fa-stopwatch',
                'color': '#FFEAA7',
                'metric_type': 'average',
                'data_field': 'duration',
                'unit': 'minutes',
                'format_type': 'duration',
                'decimal_places': 0,
                'applicable_to': 'all'
            },
            {
                'name': 'Average Heart Rate',
                'key': 'avg_heart_rate',
                'title': 'Avg Heart Rate',
                'description': 'Average heart rate',
                'icon': 'fa-heartbeat',
                'color': '#E17055',
                'metric_type': 'average',
                'data_field': 'average_heart_rate',
                'unit': 'bpm',
                'format_type': 'number',
                'decimal_places': 0,
                'applicable_to': 'all'
            },
            
            # Sport-specific metrics
            {
                'name': 'Max Heart Rate',
                'key': 'max_heart_rate',
                'title': 'Max Heart Rate',
                'description': 'Maximum heart rate achieved',
                'icon': 'fa-heartbeat',
                'color': '#D63031',
                'metric_type': 'max',
                'data_field': 'max_heart_rate',
                'unit': 'bpm',
                'format_type': 'number',
                'decimal_places': 0,
                'applicable_to': 'sport'
            },
            {
                'name': 'Longest Activity',
                'key': 'longest_activity',
                'title': 'Longest',
                'description': 'Longest single activity',
                'icon': 'fa-trophy',
                'color': '#FDCB6E',
                'metric_type': 'max',
                'data_field': 'distance',
                'unit': 'km',
                'format_type': 'decimal',
                'decimal_places': 2,
                'applicable_to': 'sport'
            },
            {
                'name': 'Weekly Trend',
                'key': 'weekly_trend',
                'title': '7-Day Trend',
                'description': 'Activity trend over the last 7 days',
                'icon': 'fa-chart-line',
                'color': '#74B9FF',
                'metric_type': 'trend',
                'data_field': 'duration',
                'unit': 'hours',
                'format_type': 'duration',
                'decimal_places': 1,
                'applicable_to': 'all'
            },
            
            # Strength training specific
            {
                'name': 'Total Weight Lifted',
                'key': 'total_weight',
                'title': 'Weight Lifted',
                'description': 'Total weight lifted across all sessions',
                'icon': 'fa-dumbbell',
                'color': '#D63031',
                'metric_type': 'custom',
                'data_field': 'notes',  # This would need custom calculation
                'unit': 'kg',
                'format_type': 'number',
                'decimal_places': 0,
                'applicable_to': 'category'
            },
            
            # Running specific
            {
                'name': 'Average Pace',
                'key': 'avg_pace',
                'title': 'Avg Pace',
                'description': 'Average pace across all runs',
                'icon': 'fa-running',
                'color': '#00B894',
                'metric_type': 'custom',
                'data_field': 'duration,distance',  # Custom calculation needed
                'unit': 'min/km',
                'format_type': 'custom',
                'decimal_places': 0,
                'applicable_to': 'sport'
            }
        ]

        created_count = 0
        updated_count = 0

        for tile_data in tiles_data:
            tile, created = MetricTile.objects.get_or_create(
                key=tile_data['key'],
                defaults=tile_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"Created tile: {tile.name}")
            else:
                # Update existing tile with new data
                for key, value in tile_data.items():
                    setattr(tile, key, value)
                tile.save()
                updated_count += 1
                self.stdout.write(f"Updated tile: {tile.name}")

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated metric tiles. '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )