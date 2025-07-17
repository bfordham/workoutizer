from django.core.management.base import BaseCommand
from wkz.models import Sport, MetricTile, SportTileConfiguration, SportTileOrder


class Command(BaseCommand):
    help = 'Setup default sport tile configurations'

    def handle(self, *args, **options):
        # Get running sport
        try:
            running_sport = Sport.objects.get(name='Running', is_system_sport=True)
        except Sport.DoesNotExist:
            self.stdout.write(self.style.ERROR('Running sport not found. Run populate_sports first.'))
            return
        
        # Create default running configuration
        config, created = SportTileConfiguration.objects.get_or_create(
            sport=running_sport,
            user=None,  # Global configuration
            applies_to='all',
            defaults={
                'tiles_per_row': 4
            }
        )
        
        if created:
            self.stdout.write(f'Created configuration for {running_sport.name}')
            
            # Add tiles for running
            running_tiles = [
                ('total_distance', 1),
                ('total_duration', 2),
                ('activity_count', 3),
                ('avg_pace', 4),
                ('longest_activity', 5),
                ('avg_heart_rate', 6),
            ]
            
            for tile_key, order in running_tiles:
                try:
                    tile = MetricTile.objects.get(key=tile_key, is_active=True)
                    SportTileOrder.objects.create(
                        sport_config=config,
                        tile=tile,
                        order=order,
                        is_visible=True
                    )
                    self.stdout.write(f'  Added tile: {tile.name}')
                except MetricTile.DoesNotExist:
                    self.stdout.write(f'  Tile {tile_key} not found, skipping')
        else:
            self.stdout.write(f'Configuration for {running_sport.name} already exists')
        
        # Create default Weight Training configuration
        try:
            weight_training_sport = Sport.objects.get(name='Weight Training', is_system_sport=True)
            
            config, created = SportTileConfiguration.objects.get_or_create(
                sport=weight_training_sport,
                user=None,  # Global configuration
                applies_to='all',
                defaults={
                    'tiles_per_row': 4
                }
            )
            
            if created:
                self.stdout.write(f'Created configuration for {weight_training_sport.name}')
                
                # Add tiles for weight training
                weight_tiles = [
                    ('total_duration', 1),
                    ('activity_count', 2),
                    ('total_calories', 3),
                    ('avg_duration', 4),
                ]
                
                for tile_key, order in weight_tiles:
                    try:
                        tile = MetricTile.objects.get(key=tile_key, is_active=True)
                        SportTileOrder.objects.create(
                            sport_config=config,
                            tile=tile,
                            order=order,
                            is_visible=True
                        )
                        self.stdout.write(f'  Added tile: {tile.name}')
                    except MetricTile.DoesNotExist:
                        self.stdout.write(f'  Tile {tile_key} not found, skipping')
            else:
                self.stdout.write(f'Configuration for {weight_training_sport.name} already exists')
        
        except Sport.DoesNotExist:
            self.stdout.write(self.style.WARNING('Weight Training sport not found, skipping'))
        
        # Create default Yoga configuration
        try:
            yoga_sport = Sport.objects.get(name='Yoga', is_system_sport=True)
            
            config, created = SportTileConfiguration.objects.get_or_create(
                sport=yoga_sport,
                user=None,  # Global configuration
                applies_to='all',
                defaults={
                    'tiles_per_row': 4
                }
            )
            
            if created:
                self.stdout.write(f'Created configuration for {yoga_sport.name}')
                
                # Add tiles for yoga (no distance)
                yoga_tiles = [
                    ('total_duration', 1),
                    ('activity_count', 2),
                    ('avg_duration', 3),
                    ('weekly_trend', 4),
                ]
                
                for tile_key, order in yoga_tiles:
                    try:
                        tile = MetricTile.objects.get(key=tile_key, is_active=True)
                        SportTileOrder.objects.create(
                            sport_config=config,
                            tile=tile,
                            order=order,
                            is_visible=True
                        )
                        self.stdout.write(f'  Added tile: {tile.name}')
                    except MetricTile.DoesNotExist:
                        self.stdout.write(f'  Tile {tile_key} not found, skipping')
            else:
                self.stdout.write(f'Configuration for {yoga_sport.name} already exists')
        
        except Sport.DoesNotExist:
            self.stdout.write(self.style.WARNING('Yoga sport not found, skipping'))
        
        self.stdout.write(self.style.SUCCESS('Default sport tile configurations setup complete!'))