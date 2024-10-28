from tabulate import tabulate

# Constants
FOOTER = "\n\nSubscribe on https://strava-summariser.vercel.app/ \nStats created using StravaAPI by Omkar Jadhav"

# Utility Functions
def convert_seconds_in_hhmmss(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def calculate_speed(moving_time, distance):
    minutes, seconds = divmod(moving_time / distance, 60)
    return f"{int(minutes):02}:{int(seconds):02} min/Km" if distance > 0 else "00:00 min/Km"

def calculate_speed_in_kmph(moving_time, distance):
    return f"{(distance / 1000) / (moving_time / 3600):.2f} km/hr" if distance > 0 else "0.00 km/hr"

# Core Summary Function
def generate_summary(activity_type, activities, time_key="moving_time", distance_key=None, type_key=None, specific_type=None):
    total_time = sum(activity[time_key] for activity in activities if not specific_type or activity.get(type_key) == specific_type)
    total_sessions = len([activity for activity in activities if not specific_type or activity.get(type_key) == specific_type])
    
    avg_time = convert_seconds_in_hhmmss(round(total_time / total_sessions, 2)) if total_sessions > 0 else "00:00:00"
    total_time_hhmmss = convert_seconds_in_hhmmss(total_time)

    summary_data = [
        [f"Total {activity_type} sessions:", total_sessions],
        [f"Avg {activity_type} session time:", avg_time],
        [f"Total {activity_type} time:", total_time_hhmmss]
    ]

    # Only include distance-related fields if distance data is provided
    if distance_key:
        total_distance = sum(activity.get(distance_key, 0) for activity in activities if not specific_type or activity.get(type_key) == specific_type)
        avg_distance = round(total_distance / total_sessions / 1000, 2) if total_sessions > 0 else 0
        summary_data.extend([
            [f"Total {activity_type} distance:", f"{total_distance / 1000:.2f} Km"],
            [f"Avg {activity_type} distance:", f"{avg_distance:.2f} Km/session"]
        ])

        if activity_type == "run" and specific_type:
            avg_speed = calculate_speed(total_time, total_distance)
            summary_data.append([f"Avg {specific_type.lower()} pace:", avg_speed])

    # Generate Result Table
    summary_table = tabulate(summary_data, tablefmt="plain")
    result_table = f"\nFour-Week Rolling {specific_type.capitalize() if specific_type else activity_type.capitalize()} Summary\n{summary_table}{FOOTER}"
    
    print(result_table)
    return result_table

# Specific Summary Functions
def give_run_summary(run_activities):
    # Overall run summary
    overall_summary = generate_summary("run", run_activities, time_key="moving_time", distance_key="distance")
    
    # Road and Trail runs summary if available
    road_summary = generate_summary("road run", run_activities, time_key="moving_time", distance_key="distance", type_key="sport_type", specific_type="Run")
    trail_summary = generate_summary("trail run", run_activities, time_key="moving_time", distance_key="distance", type_key="sport_type", specific_type="TrailRun")
    
    return f"{overall_summary}\n\n{road_summary}\n\n{trail_summary}"

# Example for other activity types without specific types
def give_weighttraining_summary(WeightTraining_activities):
    return generate_summary("strength training", WeightTraining_activities, time_key="moving_time")

def give_yoga_summary(yoga_activities):
    return generate_summary("yoga", yoga_activities, time_key="elapsed_time")

def give_swim_summary(swim_activities):
    return generate_summary("swim", swim_activities, time_key="elapsed_time")

def give_ride_summary(ride_activities):
    return generate_summary("ride", ride_activities, time_key="moving_time", distance_key="distance")

def give_walk_summary(walk_activities):
    return generate_summary("walk", walk_activities, time_key="moving_time", distance_key="distance")
