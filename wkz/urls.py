import django_eventstream
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path

from wkz import activity_views, api, auth_views as custom_auth_views, awards_views, sport_views, views

urlpatterns = [
    # Authentication
    path("login/", auth_views.LoginView.as_view(template_name='auth/login.html'), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", custom_auth_views.signup_view, name="signup"),
    path("profile/", custom_auth_views.profile_view, name="profile"),
    path("profile/edit/", custom_auth_views.edit_profile_view, name="edit-profile"),
    # Public profiles
    path("users/<str:username>/", custom_auth_views.public_profile_view, name="public-profile"),
    # home Dashboard
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("set_number_of_days/<slug:number_of_days>", views.set_number_of_days, name="set-number-of-days"),
    path("activities_page/<slug:page>", views.get_bulk_of_rows_for_next_page, name="activities-page"),
    # Settings
    path("settings/", views.settings_view, name="settings"),
    path("settings/form", views.settings_form, name="settings-form"),
    path("settings/delete-demo-data/", activity_views.DemoActivityDeleteView.as_view(), name="delete-demo-data"),
    # Help
    path("help/", views.HelpView.as_view(), name="help"),
    # Activities
    path("activity/<slug:activity_id>", activity_views.ActivityView.as_view(), name="activity"),
    path("activity/<slug:activity_id>/edit/", activity_views.edit_activity_view, name="edit-activity"),
    path("activity/<slug:activity_id>/download/", activity_views.download_activity, name="download-activity"),
    path("add-activity/", activity_views.add_activity_view, name="add-activity"),
    re_path(r"^activity/(?P<pk>\d+)/delete/$", activity_views.ActivityDeleteView.as_view(), name="delete-activity"),
    # Test tiles
    path("test-tiles/", views.test_tiles, name="test-tiles"),
    # Sports
    path("sport/<slug:sports_name_slug>", sport_views.SportView.as_view(), name="sport"),
    path("sports/", sport_views.SportsView.as_view(), name="sports"),
    path("add-sport/", sport_views.add_sport_view, name="add-sport"),
    path("sport/<slug:sports_name_slug>/edit/", sport_views.edit_sport_view, name="edit-sport"),
    re_path(r"^sport/(?P<slug>[a-zA-Z0-9-]+)/delete/$", sport_views.SportDeleteView.as_view(), name="delete-sport"),
    # Best Sections
    path("awards/", awards_views.AwardsViews.as_view(), name="awards"),
    # Rest API endpoints
    path("mount-device/", api.mount_device_endpoint),
    path("stop/", api.stop_django_server),
    # events channel
    path("events/", include(django_eventstream.urls), {"channels": ["event"]}),
]
