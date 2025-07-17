import datetime
import logging
import os
from pathlib import Path

from colorfield.fields import ColorField
from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone

from wkz.io.file_importer import run_importer
from wkz.tools import sse
from workoutizer import settings as django_settings

log = logging.getLogger(__name__)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    days_choices = [
        (9999, "all"),
        (1095, "3 years"),
        (730, "2 years"),
        (365, "1 year"),
        (180, "180 days"),
        (90, "90 days"),
        (30, "30 days"),
        (10, "10 days"),
    ]
    
    path_to_trace_dir = models.CharField(
        max_length=200, default=django_settings.TRACKS_DIR, verbose_name="Path to Traces Directory"
    )
    path_to_garmin_device = models.CharField(
        max_length=200,
        default="",
        verbose_name="Path to Garmin Device",
        blank=True,
    )
    number_of_days = models.IntegerField(choices=days_choices, default=30)
    delete_files_after_import = models.BooleanField(verbose_name="Delete fit Files after Copying ", default=False)
    public_profile = models.BooleanField(verbose_name="Make Profile Public", default=False, 
                                       help_text="Allow others to view your activities at /users/<username>")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    __original_path_to_trace_dir = None

    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)
        self.__original_path_to_trace_dir = self.path_to_trace_dir
        self.__original_path_to_garmin_device = self.path_to_garmin_device

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        super(UserProfile, self).save(force_insert, force_update, *args, **kwargs)
        # whenever a path changes, check if it is a valid dir and retrigger watchdog
        if self.path_to_trace_dir != self.__original_path_to_trace_dir:
            from wkz import models

            if Path(self.path_to_trace_dir).is_dir():
                run_importer(models)
            else:
                sse.send(f"<code>{self.path_to_trace_dir}</code> is not a valid path.", "red", "WARNING")
        self.__original_path_to_trace_dir = self.path_to_trace_dir

        if self.path_to_garmin_device != self.__original_path_to_garmin_device:
            if self.path_to_garmin_device == "":
                sse.send("Disabled device watchdog.", "green", log_level="INFO")
            elif Path(self.path_to_garmin_device).is_dir():
                sse.send(f"<b>Device watchdog</b> now monitors <code>{self.path_to_garmin_device}</code>", "green")
            else:
                sse.send(f"<code>{self.path_to_garmin_device}</code> is not a valid path.", "red", "WARNING")
        self.__original_path_to_garmin_device = self.path_to_garmin_device

    def __str__(self):
        return f"{self.user.username} Profile"


class Sport(models.Model):
    def __str__(self):
        return self.name

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50, verbose_name="Sport Name")
    mapping_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mapping Name")
    icon = models.CharField(max_length=50, verbose_name="Icon")
    slug = models.SlugField(max_length=100, blank=True)
    color = ColorField(default="#42FF71", verbose_name="Color")
    evaluates_for_awards = models.BooleanField(verbose_name="Consider Sport for Awards", default=True)
    
    # Enhanced fields for better categorization
    category = models.CharField(max_length=50, blank=True, null=True, verbose_name="Category",
                               help_text="e.g., 'Cardio', 'Strength', 'Flexibility', 'Sports', 'Water'")
    has_distance = models.BooleanField(default=True, verbose_name="Distance-based Activity",
                                     help_text="Whether this sport typically tracks distance")
    external_mappings = models.TextField(blank=True, null=True, verbose_name="External Mappings",
                                       help_text="JSON mapping of external service activity types")
    is_system_sport = models.BooleanField(default=False, verbose_name="System Sport",
                                        help_text="Created by system, available to all users")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'name']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Sport, self).save(*args, **kwargs)


class Traces(models.Model):
    def __str__(self):
        return self.file_name

    path_to_file = models.CharField(max_length=200)
    file_name = models.CharField(max_length=100, editable=False)
    md5sum = models.CharField(max_length=32, unique=True)
    calories = models.IntegerField(null=True, blank=True)
    # coordinates
    latitude_list = models.CharField(max_length=10000000000, default="[]")
    longitude_list = models.CharField(max_length=10000000000, default="[]")
    # distance
    distance_list = models.CharField(max_length=10000000000, default="[]")
    # elevation
    altitude_list = models.CharField(max_length=10000000000, default="[]")
    max_altitude = models.FloatField(blank=True, null=True)
    min_altitude = models.FloatField(blank=True, null=True)
    # heart rate
    heart_rate_list = models.CharField(max_length=10000000000, default="[]")
    avg_heart_rate = models.IntegerField(null=True, blank=True)
    max_heart_rate = models.IntegerField(null=True, blank=True)
    min_heart_rate = models.IntegerField(null=True, blank=True)
    # cadence
    cadence_list = models.CharField(max_length=10000000000, default="[]")
    avg_cadence = models.IntegerField(null=True, blank=True)
    max_cadence = models.IntegerField(null=True, blank=True)
    min_cadence = models.IntegerField(null=True, blank=True)
    # speed
    speed_list = models.CharField(max_length=10000000000, default="[]")
    avg_speed = models.FloatField(null=True, blank=True)
    max_speed = models.FloatField(null=True, blank=True)
    min_speed = models.FloatField(null=True, blank=True)
    # temperature
    temperature_list = models.CharField(max_length=10000000000, default="[]")
    avg_temperature = models.FloatField(null=True, blank=True)
    max_temperature = models.FloatField(null=True, blank=True)
    min_temperature = models.FloatField(null=True, blank=True)
    # training effect
    aerobic_training_effect = models.FloatField(blank=True, null=True)
    anaerobic_training_effect = models.FloatField(blank=True, null=True)
    # timestamps
    timestamps_list = models.CharField(max_length=10000000000, default="[]")
    # total ascent/descent
    total_ascent = models.IntegerField(null=True, blank=True)
    total_descent = models.IntegerField(null=True, blank=True)
    # other
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.file_name = os.path.basename(self.path_to_file)
        super(Traces, self).save()


def default_sport(return_pk: bool = True):
    # Return None to handle in model field default
    return None


class Activity(models.Model):
    def __str__(self):
        return f"{self.name} ({self.sport})"

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, verbose_name="Activity Name", default="unknown")
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Sport")
    date = models.DateTimeField(blank=False, default=timezone.now, verbose_name="Date")
    duration = models.DurationField(verbose_name="Duration", default=datetime.timedelta(minutes=30))
    distance = models.FloatField(blank=True, null=True, verbose_name="Distance")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    trace_file = models.ForeignKey(Traces, on_delete=models.CASCADE, blank=True, null=True)
    is_demo_activity = models.BooleanField(verbose_name="Is this a Demo Activity", default=False)
    evaluates_for_awards = models.BooleanField(verbose_name="Consider Activity for Awards", default=True)
    
    # Enhanced fields for Strava import and richer data
    external_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="External ID", 
                                  help_text="ID from external service (e.g., Strava)")
    external_source = models.CharField(max_length=50, blank=True, null=True, verbose_name="External Source",
                                      help_text="Source of import (e.g., 'strava', 'garmin')")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes",
                            help_text="Additional notes or detailed description")
    activity_type = models.CharField(max_length=100, blank=True, null=True, verbose_name="Activity Type",
                                   help_text="Specific activity type from external source")
    
    # Metrics for non-distance activities
    calories = models.IntegerField(blank=True, null=True, verbose_name="Calories")
    average_heart_rate = models.IntegerField(blank=True, null=True, verbose_name="Average Heart Rate")
    max_heart_rate = models.IntegerField(blank=True, null=True, verbose_name="Max Heart Rate")
    
    # Achievement tracking
    kudos_count = models.IntegerField(blank=True, null=True, verbose_name="Kudos/Likes")
    achievement_count = models.IntegerField(blank=True, null=True, verbose_name="Achievements")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        if self.trace_file:
            self.trace_file.delete()
            log.debug(f"deleted trace object {self.trace_file}")
            if os.path.isfile(self.trace_file.path_to_file):
                os.remove(self.trace_file.path_to_file)
                log.debug(f"deleted trace file also: {self.name}")
        super(Activity, self).delete(*args, **kwargs)
        log.debug(f"deleted activity: {self.name}")

    @property
    def has_distance(self):
        """Check if this activity has meaningful distance data"""
        return self.distance is not None and self.distance > 0

    @property 
    def display_distance(self):
        """Return formatted distance or '-' if no distance"""
        if self.has_distance:
            return f"{self.distance:.2f} km"
        return "-"

    class Meta:
        verbose_name_plural = "Activities"
        unique_together = ['external_id', 'external_source', 'user']  # Prevent duplicate imports


class ActivityPhoto(models.Model):
    """Model for storing activity photos"""
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='activity_photos/%Y/%m/', verbose_name="Photo")
    caption = models.CharField(max_length=200, blank=True, null=True, verbose_name="Caption")
    external_photo_id = models.CharField(max_length=100, blank=True, null=True, 
                                       verbose_name="External Photo ID")
    upload_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Photo for {self.activity.name}"

    class Meta:
        ordering = ['upload_date']


class Lap(models.Model):
    start_time = models.DateTimeField(blank=False)
    end_time = models.DateTimeField(blank=False)
    elapsed_time = models.DurationField(blank=False)
    trigger = models.CharField(max_length=120, blank=False)
    start_lat = models.FloatField(blank=True, null=True)
    start_long = models.FloatField(blank=True, null=True)
    end_lat = models.FloatField(blank=True, null=True)
    end_long = models.FloatField(blank=True, null=True)
    distance = models.FloatField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    trace = models.ForeignKey(Traces, on_delete=models.CASCADE, blank=False)
    label = models.CharField(max_length=100, blank=True, null=True, verbose_name="Label")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class BestSection(models.Model):
    """
    Contains all best sections of all activities. Best sections could be e.g. the fastest 5km of an activity. This model
    stores the start and end of each section, which is used to render the sections in the activity view.
    """

    def __str__(self):
        return f"{self.kind} {self.distance}m: {self.max_value}"

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, blank=False)
    kind = models.CharField(max_length=120, blank=False)
    distance = models.IntegerField(blank=False)
    start = models.IntegerField(blank=False)
    end = models.IntegerField(blank=False)
    max_value = models.FloatField(blank=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Settings(models.Model):
    days_choices = [
        (9999, "all"),
        (1095, "3 years"),
        (730, "2 years"),
        (365, "1 year"),
        (180, "180 days"),
        (90, "90 days"),
        (30, "30 days"),
        (10, "10 days"),
    ]

    path_to_trace_dir = models.CharField(
        max_length=200, default=django_settings.TRACKS_DIR, verbose_name="Path to Traces Directory"
    )
    path_to_garmin_device = models.CharField(
        max_length=200,
        default="",
        verbose_name="Path to Garmin Device",
        blank=True,
    )
    number_of_days = models.IntegerField(choices=days_choices, default=30)
    delete_files_after_import = models.BooleanField(verbose_name="Delete fit Files after Copying ", default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    __original_path_to_trace_dir = None

    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        self.__original_path_to_trace_dir = self.path_to_trace_dir
        self.__original_path_to_garmin_device = self.path_to_garmin_device

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        super(Settings, self).save(force_insert, force_update, *args, **kwargs)
        # whenever a path changes, check if it is a valid dir and retrigger watchdog
        if self.path_to_trace_dir != self.__original_path_to_trace_dir:
            from wkz import models

            if Path(self.path_to_trace_dir).is_dir():
                run_importer(models)
            else:
                sse.send(f"<code>{self.path_to_trace_dir}</code> is not a valid path.", "red", "WARNING")
        self.__original_path_to_trace_dir = self.path_to_trace_dir

        if self.path_to_garmin_device != self.__original_path_to_garmin_device:
            if self.path_to_garmin_device == "":
                sse.send("Disabled device watchdog.", "green", log_level="INFO")
            elif Path(self.path_to_garmin_device).is_dir():
                sse.send(f"<b>Device watchdog</b> now monitors <code>{self.path_to_garmin_device}</code>", "green")
            else:
                sse.send(f"<code>{self.path_to_garmin_device}</code> is not a valid path.", "red", "WARNING")
        self.__original_path_to_garmin_device = self.path_to_garmin_device


def get_settings(user=None):
    if user:
        profile, created = UserProfile.objects.get_or_create(user=user)
        return profile
    else:
        # For backward compatibility, return the old Settings object
        return Settings.objects.get_or_create(pk=1)[0]


def get_user_profile(user):
    profile, created = UserProfile.objects.get_or_create(user=user)
    return profile


class MetricTile(models.Model):
    """Defines a metric tile that can be displayed on dashboards"""
    
    # Tile identification
    name = models.CharField(max_length=100, verbose_name="Tile Name")
    key = models.CharField(max_length=50, unique=True, verbose_name="Tile Key",
                          help_text="Unique identifier for this tile (e.g., 'total_distance')")
    
    # Display properties
    title = models.CharField(max_length=100, verbose_name="Display Title")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    icon = models.CharField(max_length=50, verbose_name="FontAwesome Icon Class",
                           help_text="FontAwesome class (e.g., 'fa-road', 'fa-stopwatch')")
    color = ColorField(default="#42FF71", verbose_name="Icon Color")
    
    # Metric configuration
    metric_type = models.CharField(max_length=50, choices=[
        ('total', 'Total (Sum)'),
        ('average', 'Average'),
        ('count', 'Count'),
        ('max', 'Maximum'),
        ('min', 'Minimum'),
        ('trend', 'Trend (7-day)'),
        ('custom', 'Custom Calculation'),
    ], verbose_name="Metric Type")
    
    data_field = models.CharField(max_length=100, verbose_name="Data Field",
                                 help_text="Field name from Activity or Traces model (e.g., 'distance', 'duration')")
    
    # Formatting
    unit = models.CharField(max_length=20, blank=True, null=True, verbose_name="Unit",
                           help_text="Display unit (e.g., 'km', 'hours', 'kcal')")
    format_type = models.CharField(max_length=20, choices=[
        ('number', 'Number'),
        ('decimal', 'Decimal'),
        ('duration', 'Duration'),
        ('date', 'Date'),
        ('custom', 'Custom Format'),
    ], default='number', verbose_name="Format Type")
    
    decimal_places = models.IntegerField(default=0, verbose_name="Decimal Places")
    
    # Applicability
    applicable_to = models.CharField(max_length=20, choices=[
        ('all', 'All Activities'),
        ('sport', 'Specific Sports'),
        ('category', 'Sport Categories'),
    ], default='all', verbose_name="Applicable To")
    
    # Ordering and display
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Metric Tile"
        verbose_name_plural = "Metric Tiles"
    
    def __str__(self):
        return f"{self.name} ({self.key})"


class SportTileConfiguration(models.Model):
    """Configures which tiles are displayed for specific sports"""
    
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, verbose_name="Sport")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                           verbose_name="User", help_text="Leave blank for global configuration")
    
    # Tile configuration
    tiles = models.ManyToManyField(MetricTile, through='SportTileOrder', verbose_name="Tiles")
    
    # Layout settings
    tiles_per_row = models.IntegerField(default=4, verbose_name="Tiles per Row",
                                       help_text="Number of tiles to display per row")
    
    # Scope
    applies_to = models.CharField(max_length=20, choices=[
        ('dashboard', 'Dashboard'),
        ('sport_page', 'Sport Page'),
        ('public_profile', 'Public Profile'),
        ('all', 'All Views'),
    ], default='all', verbose_name="Applies To")
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['sport', 'user', 'applies_to']
        verbose_name = "Sport Tile Configuration"
        verbose_name_plural = "Sport Tile Configurations"
    
    def __str__(self):
        user_str = f" for {self.user.username}" if self.user else " (Global)"
        return f"{self.sport.name} - {self.applies_to}{user_str}"


class SportTileOrder(models.Model):
    """Defines the order of tiles for a sport configuration"""
    
    sport_config = models.ForeignKey(SportTileConfiguration, on_delete=models.CASCADE)
    tile = models.ForeignKey(MetricTile, on_delete=models.CASCADE)
    order = models.IntegerField(default=0, verbose_name="Display Order")
    
    # Tile-specific overrides
    custom_title = models.CharField(max_length=100, blank=True, null=True,
                                   verbose_name="Custom Title",
                                   help_text="Override the default tile title")
    custom_color = ColorField(blank=True, null=True, verbose_name="Custom Color",
                             help_text="Override the default tile color")
    is_visible = models.BooleanField(default=True, verbose_name="Visible")
    
    class Meta:
        ordering = ['order']
        unique_together = ['sport_config', 'tile']
        verbose_name = "Sport Tile Order"
        verbose_name_plural = "Sport Tile Orders"
    
    def __str__(self):
        return f"{self.sport_config.sport.name} - {self.tile.name} ({self.order})"
