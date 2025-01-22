# workout_classifier.py (Complete Verified Version)
import logging
import numpy as np
import requests
from collections import defaultdict
from utils import calculate_pace_minKm
import utils

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class WorkoutClassifier:
    def __init__(self, activities, headers):
        self.activities = activities if activities else []
        self.headers = headers if headers else {}
        self._validate_inputs()
        
        # Initialize components with error handling
        try:
            self.stats = self._calculate_statistical_baselines()
            self.sport_profiles = self._create_sport_profiles()
            self.athlete_baselines = self._calculate_athlete_baselines()
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            raise

    def _validate_inputs(self):
        """Validate all input parameters"""
        if not isinstance(self.activities, list):
            raise ValueError("Activities must be a list")
        if not isinstance(self.headers, dict):
            raise ValueError("Headers must be a dictionary")
        if not all(isinstance(a, dict) for a in self.activities):
            raise ValueError("All activities must be dictionaries")

    def _calculate_statistical_baselines(self):
        """Calculate statistical baselines with full validation"""
        try:
            distances = [a.get('distance', 0)/1000 for a in self.activities]
            speeds = [a.get('average_speed', 0)*3.6 for a in self.activities]
            hrs = [a.get('average_heartrate', 0) for a in self.activities]

            return {
                'distance_mean': float(np.nanmean(distances)),
                'distance_std': float(np.nanstd(distances)),
                'speed_mean': float(np.nanmean(speeds)),
                'speed_std': float(np.nanstd(speeds)),
                'hr_mean': float(np.nanmean(hrs)),
                'hr_std': float(np.nanstd(hrs))
            }
        except Exception as e:
            logger.error(f"Statistical baseline calculation failed: {str(e)}")
            return {}

    def _create_sport_profiles(self):
        """Create sport profiles with complete error checking"""
        profiles = defaultdict(lambda: {
            'durations': [],
            'speeds': [],
            'elevations': [],
            'variabilities': []
        })

        for idx, activity in enumerate(self.activities):
            try:
                if not isinstance(activity, dict):
                    raise ValueError(f"Activity {idx} is not a dictionary")
                
                sport = activity.get('sport_type', 'Run')
                features = self._extract_features(activity)
                
                # Validate feature structure
                required_features = ['duration', 'speed', 'elevation_ratio', 'speed_variability']
                if not all(key in features for key in required_features):
                    missing = [key for key in required_features if key not in features]
                    raise KeyError(f"Missing features {missing} in activity {idx}")
                
                # Store validated features
                profiles[sport]['durations'].append(features['duration'])
                profiles[sport]['speeds'].append(features['speed'])
                profiles[sport]['elevations'].append(features['elevation_ratio'])
                profiles[sport]['variabilities'].append(features['speed_variability'])
                
            except Exception as e:
                logger.warning(f"Skipping activity {idx}: {str(e)}")
                continue
                
        return profiles

    def _extract_features(self, activity):
        """Robust feature extraction with full validation"""
        try:
            # Validate numeric values
            duration = float(activity.get('moving_time', 0)) / 60
            distance_km = float(activity.get('distance', 0)) / 1000
            avg_speed = float(activity.get('average_speed', 0))
            max_speed = float(activity.get('max_speed', avg_speed))
            elev_gain = float(activity.get('total_elevation_gain', 0))
            avg_hr = activity.get('average_heartrate', 0)
            max_hr = float(activity.get('max_heartrate', 0))
            
            # Calculate derived features
            speed = avg_speed * 3.6  # m/s → km/h
            max_speed_kmh = max_speed * 3.6
            elev_ratio = elev_gain / max(1, distance_km)  # Avoid division by zero
            speed_variability = (max_speed_kmh - speed) / speed if speed > 0 else 0

            return {
                'duration': duration,
                'distance_km': distance_km,
                'speed': speed,
                'max_speed': max_speed_kmh,
                'elevation_ratio': elev_ratio,
                'speed_variability': speed_variability,
                'avg_hr': avg_hr,   
                'max_hr': max_hr
            }
        except (TypeError, ValueError) as e:
            logger.error(f"Feature extraction failed: {str(e)}")
            return {
                'duration': 0,
                'distance_km': 0,
                'speed': 0,
                'max_speed': 0,
                'elevation_ratio': 0,
                'speed_variability': 0
            }

    def _calculate_athlete_baselines(self):
        """Calculate athlete baselines with percentile validation"""
        baselines = {}
        try:
            for sport, data in self.sport_profiles.items():
                baselines[sport] = {
                    'endurance_threshold': np.percentile(data['durations'], 75) if data['durations'] else 60,
                    'intensity_cutoff': np.percentile(data['speeds'], 90) if data['speeds'] else 15,
                    'hill_threshold': np.percentile(data['elevations'], 85) if data['elevations'] else 15,
                    'variability_cutoff': np.percentile(data['variabilities'], 90) if data['variabilities'] else 1.2
                }
            return baselines
        except Exception as e:
            logger.error(f"Athlete baseline calculation failed: {str(e)}")
            return {}

    def classify_workout(self, activity):
        """Main classification method with full validation"""
        try:
            if not isinstance(activity, dict):
                raise ValueError("Activity must be a dictionary")
            
            # Special cases first
            if activity.get('workout_type') == 1:
                return self._format_race(activity)
                
            if activity.get('sport_type') == 'TrailRun':
                return self._format_trail_run(activity)

            features = self._extract_features(activity)
            sport = activity.get('sport_type', 'Run')
            baseline = self.athlete_baselines.get(sport, {})

            if features['distance_km'] > (self.stats['distance_mean'] + self.stats['distance_std']):
                return self._format_long_run(activity)
                
            if self.stats['distance_mean'] - self.stats['distance_std'] <= features['distance_km'] <= self.stats['distance_mean'] + self.stats['distance_std']:
                if features['avg_hr'] == 0:
                    if features['speed'] >= self.stats['speed_mean'] + 0.25 * self.stats['speed_std']:
                        return "Tempo Workout"
                else:
                    if features['avg_hr'] >= self.stats['hr_mean'] + 0.7 * self.stats['hr_std'] and features['speed'] >= self.stats['speed_mean'] + 0.25 * self.stats['speed_std']:
                        return "Tempo Workout"
                
            if features['elevation_ratio'] > baseline.get('hill_threshold', 15):
                return "Hill Workout"
                
            if features['speed'] < (self.stats['speed_mean'] - 0.2*self.stats['speed_std']):
                return "Recovery Run"
                
            if (features['speed'] < (self.stats['speed_mean'] + 0.5*self.stats['speed_std'])) and \
               (activity.get('average_heartrate', 0) < (self.stats['hr_mean'] + 0.4*self.stats['hr_std'])) and \
                (activity.get('max_heartrate',0) <= self.stats['hr_mean']+1.1*self.stats['hr_std']):
                return "Easy Run"
            
            # Priority-based classification
            activity_complete = self.fetch_complete_activity_detail(activity['id'])
            if 'laps' in activity_complete:
                interval_result = self._detect_interval_type(activity_complete)
                if "Intervals" in interval_result or "Fartlek" in interval_result:
                    return interval_result

            return "Base Training"
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            return "Unclassified"
        
        
    def _format_race(self, activity):
        """Format race activities with detailed metrics"""
        pace = calculate_pace_minKm(activity['moving_time'], activity['distance'])
        return f"Race\n{activity['distance']/1000:.2f} km at {pace} | ↗️{activity['total_elevation_gain']}m"

    def _format_trail_run(self, activity):
        """Format trail runs with elevation details"""
        return f"Trail Run\n{activity['distance']/1000:.2f} km | ↗️{activity['total_elevation_gain']}m"

    def _format_long_run(self, activity):
        """Format long runs with pace information"""
        pace = calculate_pace_minKm(activity['moving_time'], activity['distance'])
        return f"Long Run\n{activity['distance']/1000:.2f} km at {pace} and {activity.get('total_elevation_gain', 0)}m"
    
    def fetch_complete_activity_detail(self, activity_id):
        """Fetch complete activity details."""
        activity_url = f"https://www.strava.com/api/v3/activities/{activity_id}"
        response = requests.get(activity_url, headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def _detect_interval_type(self, detailed_activity):
        """Safe interval detection with key checks"""
        if not detailed_activity:
            return "Variable Pace Run"
        
        interval_candidates = []
        for data_type in ['laps', 'segment_efforts']:
            for item in detailed_activity.get(data_type, []):
                if 'average_speed' in item:  # Explicit check
                    interval_candidates.append(item)
        
        if len(interval_candidates) >= 3:
            speeds = []
            for lap in interval_candidates:
                avg_speed = lap.get('average_speed', 0)
                if avg_speed and avg_speed > 0:
                    speeds.append(avg_speed * 3.6)
            
            if len(speeds) >= 2:  # Require at least 2 valid speed measurements
                speed_ratio = max(speeds)/min(speeds) if min(speeds) > 0 else 0
                cv = np.std(speeds)/np.mean(speeds) if len(speeds) > 0 else 0
                
                if speed_ratio > 1.6 or cv > 0.22:
                    return self._format_interval_run(interval_candidates)
        
        return "Variable Pace Run"

    def _format_interval_run(self, laps):
        """Safe lap formatting with key validation"""
        lap_details = []
        interval_count = 0
        recovery_count = 0
        
        for i, lap in enumerate(laps):
            distance = lap.get('distance', 0)/1000
            moving_time = lap.get('moving_time', 0)
            lap_distance = lap.get('distance', 1)  # Avoid division by zero
            
            pace = calculate_pace_minKm(moving_time, lap_distance)
            
            # Safe speed calculation
            avg_speed = lap.get('average_speed', 0)
            speed = avg_speed * 3.6 if avg_speed else 0
            
            pace_changes = [lap['average_speed'] for lap in laps]
            if len(pace_changes) >= 3 and (max(pace_changes) / min(pace_changes)) > 1.5:
                
                return "Intervals\n" + "\n".join(self.get_interval_run_details(laps))
            
            lap_details.append(f"{i+1}: {distance:.2f} km @ {pace}")

        # Rest of the method remains unchanged...
        if interval_count >= 4 and recovery_count >= 3:
            return f"Structured Intervals ({len(laps)} segments)\n" + "\n".join(lap_details)
        elif interval_count >= 3:
            return f"Fartlek Session ({len(laps)} segments)\n" + "\n".join(lap_details)
        
        return "Variable Pace Run\n" + "\n".join(lap_details)
    
    def get_interval_run_details(self, laps):
        """Get interval run details."""
        lap_speeds = [round(((1000/lap['average_speed'])/60),2) for lap in laps] # Avg speed in m/s converting it to min/Km
        lap_distances = [lap['distance']/1000 for lap in laps]
        
        lap_details =[f"Lap {i+1}: {lap_distances[i]:.2f} km at {lap_speeds[i]} min/Km" for i in range(len(lap_speeds))]    
        return lap_details
    
def get_run_type(activities, headers):
    """Public API with complete validation"""
    try:
        if not activities or not headers:
            logger.error("Invalid input: empty activities or headers")
            return []
            
        if not isinstance(activities, list) or not isinstance(headers, dict):
            logger.error("Invalid input types")
            return []
            
        classifier = WorkoutClassifier(activities, headers)
        return [classifier.classify_workout(a) for a in activities]
    except Exception as e:
        logger.critical(f"Critical error in get_run_type: {str(e)}")
        return []