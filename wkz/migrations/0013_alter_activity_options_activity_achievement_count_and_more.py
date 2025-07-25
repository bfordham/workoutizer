# Generated by Django 4.2.16 on 2025-07-16 02:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("wkz", "0012_userprofile_public_profile"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="activity",
            options={"verbose_name_plural": "Activities"},
        ),
        migrations.AddField(
            model_name="activity",
            name="achievement_count",
            field=models.IntegerField(blank=True, null=True, verbose_name="Achievements"),
        ),
        migrations.AddField(
            model_name="activity",
            name="activity_type",
            field=models.CharField(
                blank=True,
                help_text="Specific activity type from external source",
                max_length=100,
                null=True,
                verbose_name="Activity Type",
            ),
        ),
        migrations.AddField(
            model_name="activity",
            name="average_heart_rate",
            field=models.IntegerField(blank=True, null=True, verbose_name="Average Heart Rate"),
        ),
        migrations.AddField(
            model_name="activity",
            name="calories",
            field=models.IntegerField(blank=True, null=True, verbose_name="Calories"),
        ),
        migrations.AddField(
            model_name="activity",
            name="external_id",
            field=models.CharField(
                blank=True,
                help_text="ID from external service (e.g., Strava)",
                max_length=100,
                null=True,
                verbose_name="External ID",
            ),
        ),
        migrations.AddField(
            model_name="activity",
            name="external_source",
            field=models.CharField(
                blank=True,
                help_text="Source of import (e.g., 'strava', 'garmin')",
                max_length=50,
                null=True,
                verbose_name="External Source",
            ),
        ),
        migrations.AddField(
            model_name="activity",
            name="kudos_count",
            field=models.IntegerField(blank=True, null=True, verbose_name="Kudos/Likes"),
        ),
        migrations.AddField(
            model_name="activity",
            name="max_heart_rate",
            field=models.IntegerField(blank=True, null=True, verbose_name="Max Heart Rate"),
        ),
        migrations.AddField(
            model_name="activity",
            name="notes",
            field=models.TextField(
                blank=True, help_text="Additional notes or detailed description", null=True, verbose_name="Notes"
            ),
        ),
        migrations.AlterField(
            model_name="activity",
            name="description",
            field=models.TextField(blank=True, null=True, verbose_name="Description"),
        ),
        migrations.AlterField(
            model_name="activity",
            name="distance",
            field=models.FloatField(blank=True, null=True, verbose_name="Distance"),
        ),
        migrations.AlterUniqueTogether(
            name="activity",
            unique_together={("external_id", "external_source", "user")},
        ),
        migrations.CreateModel(
            name="ActivityPhoto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to="activity_photos/%Y/%m/", verbose_name="Photo")),
                ("caption", models.CharField(blank=True, max_length=200, null=True, verbose_name="Caption")),
                (
                    "external_photo_id",
                    models.CharField(blank=True, max_length=100, null=True, verbose_name="External Photo ID"),
                ),
                ("upload_date", models.DateTimeField(auto_now_add=True)),
                (
                    "activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="photos", to="wkz.activity"
                    ),
                ),
            ],
            options={
                "ordering": ["upload_date"],
            },
        ),
    ]
