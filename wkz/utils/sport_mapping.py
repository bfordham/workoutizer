import json
from typing import Optional
from wkz.models import Sport


class SportMapper:
    """Utility class for mapping external activity types to internal sports"""
    
    @staticmethod
    def find_sport_by_strava_type(strava_activity_type: str, user=None) -> Optional[Sport]:
        """
        Find a sport based on Strava activity type
        
        Args:
            strava_activity_type: The activity type from Strava (e.g., 'Run', 'Ride', 'WeightTraining')
            user: User to search user-specific sports first, then system sports
            
        Returns:
            Sport object if found, None otherwise
        """
        # First check user's custom sports if user provided
        if user:
            user_sports = Sport.objects.filter(user=user)
            for sport in user_sports:
                if sport.external_mappings:
                    try:
                        mappings = json.loads(sport.external_mappings)
                        strava_types = mappings.get('strava', [])
                        if strava_activity_type in strava_types:
                            return sport
                    except (json.JSONDecodeError, KeyError):
                        continue
        
        # Then check system sports
        system_sports = Sport.objects.filter(is_system_sport=True)
        for sport in system_sports:
            if sport.external_mappings:
                try:
                    mappings = json.loads(sport.external_mappings)
                    strava_types = mappings.get('strava', [])
                    if strava_activity_type in strava_types:
                        return sport
                except (json.JSONDecodeError, KeyError):
                    continue
        
        # Fallback: try to find by name similarity
        return SportMapper._find_by_name_similarity(strava_activity_type, user)
    
    @staticmethod
    def _find_by_name_similarity(activity_type: str, user=None) -> Optional[Sport]:
        """Find sport by name similarity as fallback"""
        # Simple mapping for common cases
        name_mappings = {
            'Run': 'Running',
            'Ride': 'Cycling', 
            'Swim': 'Swimming',
            'Walk': 'Walking',
            'Hike': 'Hiking',
            'WeightTraining': 'Weight Training',
            'Workout': 'Other',
            'Yoga': 'Yoga',
            'Soccer': 'Soccer',
            'Basketball': 'Basketball',
            'Tennis': 'Tennis',
            'Golf': 'Golf',
        }
        
        mapped_name = name_mappings.get(activity_type)
        if mapped_name:
            # Try user's sports first
            if user:
                sport = Sport.objects.filter(user=user, name=mapped_name).first()
                if sport:
                    return sport
            
            # Try system sports
            return Sport.objects.filter(is_system_sport=True, name=mapped_name).first()
        
        return None
    
    @staticmethod
    def get_or_create_sport_for_user(strava_activity_type: str, user) -> Sport:
        """
        Get or create a sport for a user based on Strava activity type
        
        Returns:
            Sport object (either existing or newly created)
        """
        # First try to find existing sport
        sport = SportMapper.find_sport_by_strava_type(strava_activity_type, user)
        if sport:
            # If it's a system sport, create a copy for the user
            if sport.is_system_sport:
                user_sport, created = Sport.objects.get_or_create(
                    user=user,
                    name=sport.name,
                    defaults={
                        'category': sport.category,
                        'icon': sport.icon,
                        'color': sport.color,
                        'has_distance': sport.has_distance,
                        'evaluates_for_awards': sport.evaluates_for_awards,
                        'external_mappings': sport.external_mappings,
                        'mapping_name': sport.mapping_name,
                    }
                )
                return user_sport
            return sport
        
        # Create a new sport if nothing found
        sport_name = strava_activity_type.replace('_', ' ').title()
        
        # Determine if it's likely distance-based
        distance_activities = ['run', 'ride', 'swim', 'walk', 'hike', 'ski', 'skate']
        has_distance = any(activity in strava_activity_type.lower() for activity in distance_activities)
        
        sport, created = Sport.objects.get_or_create(
            user=user,
            name=sport_name,
            defaults={
                'category': 'Other',
                'icon': 'fa-question-circle',
                'color': '#9E9E9E',
                'has_distance': has_distance,
                'evaluates_for_awards': has_distance,  # Only distance activities for awards by default
                'external_mappings': json.dumps({'strava': [strava_activity_type]}),
                'mapping_name': sport_name.lower().replace(' ', '_'),
            }
        )
        
        return sport