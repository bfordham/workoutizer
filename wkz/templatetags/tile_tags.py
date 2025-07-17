from django import template
from wkz.utils.tile_metrics import calculate_tiles_for_sport
from wkz.models import Sport

register = template.Library()


@register.inclusion_tag('lib/configurable_tiles.html')
def show_sport_tiles(sport, user=None, applies_to='all', days_limit=None):
    """Display configurable tiles for a sport"""
    if isinstance(sport, str):
        try:
            # First try to get by slug, then by name for backward compatibility
            sport = Sport.objects.get(slug=sport)
        except Sport.DoesNotExist:
            try:
                sport = Sport.objects.get(name=sport)
            except Sport.DoesNotExist:
                return {'tiles': []}
    
    tiles = calculate_tiles_for_sport(
        sport=sport,
        user=user,
        applies_to=applies_to,
        days_limit=days_limit
    )
    
    return {
        'tiles': tiles,
        'sport': sport,
        'user': user
    }


@register.inclusion_tag('lib/configurable_tiles.html')
def show_default_tiles(user=None, days_limit=None):
    """Display default tiles for all activities"""
    from wkz.utils.tile_metrics import TileMetricCalculator
    from wkz.models import MetricTile
    
    # Get default tiles
    default_tiles = MetricTile.objects.filter(
        key__in=['total_distance', 'total_duration', 'activity_count', 'total_calories'],
        is_active=True
    ).order_by('key')
    
    calculator = TileMetricCalculator(user=user, days_limit=days_limit)
    
    tiles = []
    for tile in default_tiles:
        metric_result = calculator.calculate_tile_metric(tile)
        tiles.append(metric_result)
    
    return {
        'tiles': tiles,
        'user': user
    }


@register.simple_tag
def get_tile_metric_value(tile_key, sport=None, user=None, days_limit=None):
    """Get a single tile metric value"""
    try:
        from wkz.models import MetricTile
        from wkz.utils.tile_metrics import TileMetricCalculator
        
        tile = MetricTile.objects.get(key=tile_key, is_active=True)
        calculator = TileMetricCalculator(user=user, sport=sport, days_limit=days_limit)
        result = calculator.calculate_tile_metric(tile)
        
        return result['formatted_value']
    except Exception:
        return "0"


@register.filter
def get_tile_color(tile_config):
    """Get the color for a tile, considering custom overrides"""
    if hasattr(tile_config, 'custom_color') and tile_config.custom_color:
        return tile_config.custom_color
    elif hasattr(tile_config, 'tile') and tile_config.tile:
        return tile_config.tile.color
    else:
        return '#42FF71'  # Default color


@register.filter
def get_tile_title(tile_config):
    """Get the title for a tile, considering custom overrides"""
    if hasattr(tile_config, 'custom_title') and tile_config.custom_title:
        return tile_config.custom_title
    elif hasattr(tile_config, 'tile') and tile_config.tile:
        return tile_config.tile.title
    else:
        return 'Unknown'
