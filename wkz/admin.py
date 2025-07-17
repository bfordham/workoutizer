from django.contrib import admin

from wkz import models


class SportTileOrderInline(admin.TabularInline):
    model = models.SportTileOrder
    extra = 1
    fields = ('tile', 'order', 'custom_title', 'custom_color', 'is_visible')
    ordering = ('order',)


@admin.register(models.MetricTile)
class MetricTileAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'title', 'metric_type', 'data_field', 'unit', 'is_active')
    list_filter = ('metric_type', 'format_type', 'applicable_to', 'is_active')
    search_fields = ('name', 'key', 'title', 'description')
    readonly_fields = ('created', 'updated')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'key', 'title', 'description', 'is_active')
        }),
        ('Display Properties', {
            'fields': ('icon', 'color')
        }),
        ('Metric Configuration', {
            'fields': ('metric_type', 'data_field', 'applicable_to')
        }),
        ('Formatting', {
            'fields': ('unit', 'format_type', 'decimal_places')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        })
    )


@admin.register(models.SportTileConfiguration)
class SportTileConfigurationAdmin(admin.ModelAdmin):
    list_display = ('sport', 'user', 'applies_to', 'tiles_per_row', 'get_tiles_count')
    list_filter = ('applies_to', 'tiles_per_row', 'sport__category')
    search_fields = ('sport__name', 'user__username')
    readonly_fields = ('created', 'updated')
    inlines = [SportTileOrderInline]
    
    def get_tiles_count(self, obj):
        return obj.tiles.count()
    get_tiles_count.short_description = 'Number of Tiles'
    
    fieldsets = (
        ('Configuration', {
            'fields': ('sport', 'user', 'applies_to')
        }),
        ('Layout Settings', {
            'fields': ('tiles_per_row',)
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        })
    )


@admin.register(models.SportTileOrder)
class SportTileOrderAdmin(admin.ModelAdmin):
    list_display = ('sport_config', 'tile', 'order', 'is_visible', 'custom_title')
    list_filter = ('is_visible', 'sport_config__sport', 'sport_config__applies_to')
    search_fields = ('sport_config__sport__name', 'tile__name', 'custom_title')
    ordering = ('sport_config', 'order')


admin.site.register(models.Sport)
admin.site.register(models.Activity)
admin.site.register(models.Settings)
admin.site.register(models.Traces)
admin.site.register(models.Lap)
admin.site.register(models.BestSection)
