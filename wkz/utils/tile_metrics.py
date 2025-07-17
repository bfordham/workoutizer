from django.db.models import Sum, Avg, Count, Max, Min
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from typing import Dict, Any, Optional, Union
from wkz.models import Activity, Sport, MetricTile, SportTileConfiguration, SportTileOrder


class TileMetricCalculator:
    """Calculates metrics for configurable tiles"""
    
    def __init__(self, user=None, sport=None, days_limit=None):
        self.user = user
        self.sport = sport
        self.days_limit = days_limit
        
    def get_activity_queryset(self):
        """Get filtered activity queryset based on user, sport, and days limit"""
        queryset = Activity.objects.all()
        
        if self.user:
            queryset = queryset.filter(user=self.user)
        
        if self.sport:
            queryset = queryset.filter(sport=self.sport)
        
        if self.days_limit:
            cutoff_date = timezone.now() - timedelta(days=self.days_limit)
            queryset = queryset.filter(date__gte=cutoff_date)
        
        return queryset
    
    def calculate_tile_metric(self, tile: MetricTile) -> Dict[str, Any]:
        """Calculate the metric value for a given tile"""
        queryset = self.get_activity_queryset()
        
        # Handle different metric types
        if tile.metric_type == 'total':
            return self._calculate_total(queryset, tile)
        elif tile.metric_type == 'average':
            return self._calculate_average(queryset, tile)
        elif tile.metric_type == 'count':
            return self._calculate_count(queryset, tile)
        elif tile.metric_type == 'max':
            return self._calculate_max(queryset, tile)
        elif tile.metric_type == 'min':
            return self._calculate_min(queryset, tile)
        elif tile.metric_type == 'trend':
            return self._calculate_trend(queryset, tile)
        elif tile.metric_type == 'custom':
            return self._calculate_custom(queryset, tile)
        else:
            return self._default_result(tile)
    
    def _calculate_total(self, queryset, tile: MetricTile) -> Dict[str, Any]:
        """Calculate total (sum) metric"""
        field_name = tile.data_field
        
        # Handle special cases
        if field_name == 'duration':
            total_seconds = sum(
                (activity.duration.total_seconds() if activity.duration else 0)
                for activity in queryset
            )
            value = total_seconds / 3600  # Convert to hours
        elif field_name == 'distance':
            result = queryset.aggregate(total=Sum(field_name))
            value = result['total'] or 0
        else:
            # Generic sum
            result = queryset.aggregate(total=Sum(field_name))
            value = result['total'] or 0
        
        return {
            'value': value,
            'formatted_value': self._format_value(value, tile),
            'raw_value': value,
            'tile': tile
        }
    
    def _calculate_average(self, queryset, tile: MetricTile) -> Dict[str, Any]:
        """Calculate average metric"""
        field_name = tile.data_field
        
        if field_name == 'duration':
            # Calculate average duration manually
            durations = [
                activity.duration.total_seconds() if activity.duration else 0
                for activity in queryset
            ]
            if durations:
                value = sum(durations) / len(durations) / 60  # Convert to minutes
            else:
                value = 0
        else:
            # Generic average
            result = queryset.aggregate(avg=Avg(field_name))
            value = result['avg'] or 0
        
        return {
            'value': value,
            'formatted_value': self._format_value(value, tile),
            'raw_value': value,
            'tile': tile
        }
    
    def _calculate_count(self, queryset, tile: MetricTile) -> Dict[str, Any]:
        """Calculate count metric"""
        value = queryset.count()
        
        return {
            'value': value,
            'formatted_value': self._format_value(value, tile),
            'raw_value': value,
            'tile': tile
        }
    
    def _calculate_max(self, queryset, tile: MetricTile) -> Dict[str, Any]:
        """Calculate maximum metric"""
        field_name = tile.data_field
        
        if field_name == 'duration':
            # Handle duration specially
            max_duration = max(
                (activity.duration.total_seconds() if activity.duration else 0
                 for activity in queryset),
                default=0
            )
            value = max_duration / 3600  # Convert to hours
        else:
            result = queryset.aggregate(max_val=Max(field_name))
            value = result['max_val'] or 0
        
        return {
            'value': value,
            'formatted_value': self._format_value(value, tile),
            'raw_value': value,
            'tile': tile
        }
    
    def _calculate_min(self, queryset, tile: MetricTile) -> Dict[str, Any]:
        """Calculate minimum metric"""
        field_name = tile.data_field
        
        result = queryset.aggregate(min_val=Min(field_name))
        value = result['min_val'] or 0
        
        return {
            'value': value,
            'formatted_value': self._format_value(value, tile),
            'raw_value': value,
            'tile': tile
        }
    
    def _calculate_trend(self, queryset, tile: MetricTile) -> Dict[str, Any]:
        """Calculate 7-day trend metric"""
        # Get last 7 days
        week_ago = timezone.now() - timedelta(days=7)
        recent_activities = queryset.filter(date__gte=week_ago)
        
        if tile.data_field == 'duration':
            value = sum(
                (activity.duration.total_seconds() if activity.duration else 0)
                for activity in recent_activities
            ) / 3600  # Convert to hours
        else:
            result = recent_activities.aggregate(total=Sum(tile.data_field))
            value = result['total'] or 0
        
        return {
            'value': value,
            'formatted_value': self._format_value(value, tile),
            'raw_value': value,
            'tile': tile
        }
    
    def _calculate_custom(self, queryset, tile: MetricTile) -> Dict[str, Any]:
        """Calculate custom metrics"""
        if tile.key == 'avg_pace':
            # Calculate average pace (min/km)
            total_distance = queryset.aggregate(dist=Sum('distance'))['dist'] or 0
            total_duration = sum(
                (activity.duration.total_seconds() if activity.duration else 0)
                for activity in queryset
            )
            
            if total_distance > 0 and total_duration > 0:
                # Pace in minutes per km
                value = (total_duration / 60) / total_distance
            else:
                value = 0
        else:
            # Default to 0 for unimplemented custom metrics
            value = 0
        
        return {
            'value': value,
            'formatted_value': self._format_value(value, tile),
            'raw_value': value,
            'tile': tile
        }
    
    def _format_value(self, value: Union[int, float], tile: MetricTile) -> str:
        """Format the value according to the tile's format type"""
        if value is None:
            return "0"
        
        if tile.format_type == 'number':
            return f"{int(value)}"
        elif tile.format_type == 'decimal':
            return f"{value:.{tile.decimal_places}f}"
        elif tile.format_type == 'duration':
            if tile.unit == 'hours':
                hours = int(value)
                minutes = int((value - hours) * 60)
                return f"{hours}h {minutes}m"
            elif tile.unit == 'minutes':
                return f"{int(value)}m"
            else:
                return f"{value:.1f}"
        elif tile.format_type == 'custom':
            if tile.key == 'avg_pace':
                # Format pace as MM:SS
                minutes = int(value)
                seconds = int((value - minutes) * 60)
                return f"{minutes}:{seconds:02d}"
            else:
                return str(value)
        else:
            return str(value)
    
    def _default_result(self, tile: MetricTile) -> Dict[str, Any]:
        """Return default result for unknown metric types"""
        return {
            'value': 0,
            'formatted_value': "0",
            'raw_value': 0,
            'tile': tile
        }


def get_tiles_for_sport(sport: Sport, user=None, applies_to='all') -> list:
    """Get configured tiles for a specific sport"""
    try:
        # Try to get user-specific configuration first
        if user:
            config = SportTileConfiguration.objects.filter(
                sport=sport,
                user=user,
                applies_to=applies_to
            ).first()
        
        # Fall back to global configuration
        if not user or not config:
            config = SportTileConfiguration.objects.filter(
                sport=sport,
                user=None,
                applies_to=applies_to
            ).first()
        
        if config:
            # Get tiles in the configured order
            tile_orders = SportTileOrder.objects.filter(
                sport_config=config,
                is_visible=True
            ).order_by('order')
            
            return [
                {
                    'tile': tile_order.tile,
                    'order': tile_order.order,
                    'custom_title': tile_order.custom_title,
                    'custom_color': tile_order.custom_color
                }
                for tile_order in tile_orders
            ]
        else:
            # Return default tiles if no configuration exists
            return _get_default_tiles()
    
    except Exception:
        return _get_default_tiles()


def _get_default_tiles() -> list:
    """Get default tiles when no configuration exists"""
    default_tile_keys = ['total_distance', 'total_duration', 'activity_count', 'total_calories']
    
    tiles = []
    for i, key in enumerate(default_tile_keys):
        try:
            tile = MetricTile.objects.get(key=key, is_active=True)
            tiles.append({
                'tile': tile,
                'order': i,
                'custom_title': None,
                'custom_color': None
            })
        except MetricTile.DoesNotExist:
            continue
    
    return tiles


def calculate_tiles_for_sport(sport: Sport, user=None, applies_to='all', days_limit=None) -> list:
    """Calculate metrics for all tiles configured for a sport"""
    tile_configs = get_tiles_for_sport(sport, user, applies_to)
    calculator = TileMetricCalculator(user=user, sport=sport, days_limit=days_limit)
    
    results = []
    for config in tile_configs:
        tile = config['tile']
        metric_result = calculator.calculate_tile_metric(tile)
        
        # Apply custom overrides
        if config['custom_title']:
            metric_result['custom_title'] = config['custom_title']
        if config['custom_color']:
            metric_result['custom_color'] = config['custom_color']
        
        results.append(metric_result)
    
    return results