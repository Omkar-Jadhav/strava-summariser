# utils.py
from decimal import ROUND_HALF_UP, Decimal
import decimal
from tabulate import tabulate

class TimeConverter:
    @staticmethod
    def seconds_to_hhmmss(seconds):
        hours = int(seconds//3600)
        minutes = int((seconds%3600)//60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

class SpeedCalculator:
    @staticmethod
    def pace_per_km(moving_time, distance):
        # Using Decimal for precise division
        try:
            pace = Decimal(str(moving_time)) / Decimal(str(distance))
            mov_speed_min, mov_speed_sec = divmod(float(pace), 60)
            return f"{int(mov_speed_min):02d}:{int(mov_speed_sec):02d} min/Km"
        except (ZeroDivisionError, decimal.InvalidOperation):
            return "0:00 min/Km"
    
    @staticmethod
    def speed_kmph(moving_time, distance):
        try:
            # Convert to Decimal for precise calculation
            moving_time_dec = Decimal(str(moving_time))
            distance_dec = Decimal(str(distance))
            hours = moving_time_dec / Decimal('3600')
            km = distance_dec / Decimal('1000')
            speed = km / hours
            # Round to 2 decimal places
            return f"{float(speed.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))} km/hr"
        except (ZeroDivisionError, decimal.InvalidOperation):
            return "0.00 km/hr"


class ActivitySummaryBase:
    def __init__(self):
        self.footer = "\n \n Subscribe on https://strava-summariser.vercel.app/ \nStats created using StravaAPI by Omkar Jadhav"
    
    def create_summary_table(self, title, data):
        table = tabulate(data, tablefmt="plain")
        return f"\n{title}\n{table}{self.footer}"
    
    def format_with_precision(self, value, precision=2):
        """
        Format a number with specified precision using Decimal for accurate rounding
        """
        try:
            # Convert to Decimal and round
            dec_value = Decimal(str(value))
            rounded = dec_value.quantize(Decimal(f'0.{"0" * precision}'), rounding=ROUND_HALF_UP)
            return f"{float(rounded):.{precision}f}"
        except (decimal.InvalidOperation, TypeError):
            return f"0.{'0' * precision}"


class TimedActivitySummary(ActivitySummaryBase):
    def calculate_basic_stats(self, activities, time_field='moving_time'):
        total_time = sum(activity[time_field] for activity in activities)
        total_sessions = len(activities)
        avg_session = total_time / total_sessions if total_sessions else 0
        
        return {
            'total_sessions': total_sessions,
            'total_time': TimeConverter.seconds_to_hhmmss(total_time),
            'avg_session': TimeConverter.seconds_to_hhmmss(round(avg_session, 2))
        }
class DistanceActivitySummary(ActivitySummaryBase):
    def calculate_distance_stats(self, activities):
        total_distance = Decimal('0')
        total_elevation = Decimal('0')
        total_sessions = len(activities)

        # Calculate totals using Decimal
        for activity in activities:
            total_distance += Decimal(str(activity['distance'])) / Decimal('1000')
            total_elevation += Decimal(str(activity['total_elevation_gain']))

        # Calculate averages and format results
        avg_distance = total_distance / Decimal(str(total_sessions)) if total_sessions else Decimal('0')
        avg_elevation = total_elevation / Decimal(str(total_sessions)) if total_sessions else Decimal('0')

        return {
            'total_sessions': total_sessions,
            'total_distance': self.format_with_precision(total_distance),
            'avg_distance': self.format_with_precision(avg_distance),
            'total_elevation': self.format_with_precision(total_elevation),
            'avg_elevation': self.format_with_precision(avg_elevation)
        }
        
        # activity_summaries.py
class WeightTrainingSummary(TimedActivitySummary):
    def generate_summary(self, activities):
        stats = self.calculate_basic_stats(activities)
        data = [
            ["Total strength_training sessions:", f"{stats['total_sessions']}"],
            ["Avg strength_training session:", f"{stats['avg_session']}"],
            ["Total strength_training time:", f"{stats['total_time']}"],
        ]
        return self.create_summary_table("Four Week Overall strength training Summary", data)

class YogaSummary(TimedActivitySummary):
    def generate_summary(self, activities):
        stats = self.calculate_basic_stats(activities, 'elapsed_time')
        data = [
            ["Total yoga sessions:", f"{stats['total_sessions']}"],
            ["Avg yoga session:", f"{stats['avg_session']}"],
            ["Total yoga time:", f"{stats['total_time']}"],
        ]
        return self.create_summary_table("Four-Week Rolling Overall Yoga Summary", data)

class SwimSummary(TimedActivitySummary):
    def generate_summary(self, activities):
        stats = self.calculate_basic_stats(activities, 'elapsed_time')
        data = [
            ["Total swim sessions:", f"{stats['total_sessions']}"],
            ["Avg swim session:", f"{stats['avg_session']}"],
            ["Total swim time:", f"{stats['total_time']}"],
        ]
        return self.create_summary_table("Four-Week Rolling Swim Summary", data)

class RideSummary(DistanceActivitySummary):
    def generate_summary(self, activities):
        stats = self.calculate_distance_stats(activities)
        total_time = sum(activity['moving_time'] for activity in activities)
        total_distance = float(stats['total_distance'])
        
        data = [
            ["Total ride sessions:", f"{stats['total_sessions']}"],
            ["Avg ride time:", f"{stats['avg_session']}"],
            ["Total ride time:", f"{stats['total_time']}"],
            ["Total ride distance:", f"{stats['total_distance']} Km"],
            ["Avg ride distance:", f"{stats['avg_distance']} Km"],
            ["Total elevation gain:", f"{stats['total_elevation']} m"],
            ["Avg elevation gain:", f"{stats['avg_elevation']} m/ride"],
            ["Avg ride speed:", SpeedCalculator.speed_kmph(total_time, total_distance * 1000)]
        ]
        return self.create_summary_table("Four-Week Rolling Ride Summary", data)

class RunSummary(DistanceActivitySummary):
    def _split_activities_by_type(self, activities):
        road_runs = [a for a in activities if a['sport_type'] == 'Run']
        trail_runs = [a for a in activities if a['sport_type'] == 'TrailRun']
        return road_runs, trail_runs

    def generate_summary(self, activities):
        overall_stats = self.calculate_distance_stats(activities)
        road_runs, trail_runs = self._split_activities_by_type(activities)
        
        total_moving_time = sum(a['moving_time'] for a in activities)
        total_elapsed_time = sum(a['elapsed_time'] for a in activities)
        total_distance = float(overall_stats['total_distance'])
        
        result = self.create_overall_summary(activities, overall_stats, total_moving_time, total_elapsed_time)
        
        if road_runs:
            result += self.create_road_summary(road_runs)
        if trail_runs:
            result += self.create_trail_summary(trail_runs)
            
        return result
    
    def create_overall_summary(self, activities, stats, total_moving_time, total_elapsed_time):
        total_distance = float(stats['total_distance'])
        data = [
            ["Total runs:", stats['total_sessions']],
            ["Total distance:", f"{stats['total_distance']} Km"],
            ["Average distance:", f"{stats['avg_distance']} Km/run"],
            ["Average pace:", SpeedCalculator.pace_per_km(total_moving_time, total_distance)],
            ["Total elevation gain:", f"{stats['total_elevation']} m"],
            ["Average elevation gain:", f"{stats['avg_elevation']} m/run"],
            ["Total moving time:", TimeConverter.seconds_to_hhmmss(total_moving_time)],
            ["Total elapsed time:", TimeConverter.seconds_to_hhmmss(total_elapsed_time)],
            ["Average elapsed speed:", SpeedCalculator.pace_per_km(total_elapsed_time, total_distance)]
        ]
        return self.create_summary_table("Four-Week Rolling Overall Run Summary", data)

class WalkSummary(DistanceActivitySummary):
    def generate_summary(self, activities):
        stats = self.calculate_distance_stats(activities)
        total_moving_time = sum(a['moving_time'] for a in activities)
        total_elapsed_time = sum(a['elapsed_time'] for a in activities)
        total_distance = float(stats['total_distance'])
        
        data = [
            ["Total walks: ", f"{stats['total_sessions']}"],
            ["Total distance: ", f"{stats['total_distance']} Km"],
            ["Average distance:", f"{stats['avg_distance']} Km/walk"],
            ["Average moving pace: ", SpeedCalculator.pace_per_km(total_moving_time, total_distance)],
            ["Total moving time: ", TimeConverter.seconds_to_hhmmss(total_moving_time)],
            ["Total elapsed time: ", TimeConverter.seconds_to_hhmmss(total_elapsed_time)],
        ]
        return self.create_summary_table("Four-Week Rolling Walk Summary", data)

# main.py
def give_weighttraining_summary(activities):
    return WeightTrainingSummary().generate_summary(activities)

def give_yoga_summary(activities):
    return YogaSummary().generate_summary(activities)

def give_swim_summary(activities):
    return SwimSummary().generate_summary(activities)

def give_ride_summary(activities):
    return RideSummary().generate_summary(activities)

def give_run_summary(activities):
    return RunSummary().generate_summary(activities)

def give_walk_summary(activities):
    return WalkSummary().generate_summary(activities)