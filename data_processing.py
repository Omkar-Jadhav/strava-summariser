from tabulate import tabulate
import utils
from utils import convert_seconds_in_hhmmss, calculate_speed_in_kmph, calculate_speed
footer = "\n \nSubscribe on strava-summariser \nStats generated using StravaAPI by Omkar Jadhav"

def give_weighttraining_summary(WeightTraining_activities):
    total_strength_training_time = 0
    total_sessions = 0
    for activity in WeightTraining_activities:
        total_strength_training_time += activity["moving_time"]
        total_sessions += 1
    
    avg_strength_training_session = utils.convert_seconds_in_hhmmss(round(total_strength_training_time/total_sessions, 2))
    total_strength_training_time = utils.convert_seconds_in_hhmmss(total_strength_training_time)
    
    overall_strength_training_summary_data =[
        ["Total strength training sessions:", f"{total_sessions}"],
        ["Avg strength training session:", f"{avg_strength_training_session}"],
        ["Total strength training time:", f"{total_strength_training_time}"],
        
    ]
    overall_strength_training_summary_table = tabulate(overall_strength_training_summary_data, tablefmt="plain")
    result_table = f"\n Four Week strength training Summary \n{overall_strength_training_summary_table}" +footer
    
    print(result_table)
    return result_table

def give_yoga_summary(yoga_activities):
    total_yoga_time = 0
    total_sessions = 0
    for activity in yoga_activities:
        total_yoga_time += activity["elapsed_time"]
        total_sessions += 1
    
    avg_yoga_session = utils.convert_seconds_in_hhmmss(round(total_yoga_time/total_sessions, 2))
    total_yoga_time = utils.convert_seconds_in_hhmmss(total_yoga_time)
    
    overall_yoga_summary_data =[
        ["Total yoga sessions:", f"{total_sessions}"],
        ["Avg yoga session:", f"{avg_yoga_session}"],
        ["Total yoga time:", f"{total_yoga_time}"],
        
    ]
    overall_yoga_summary_table = tabulate(overall_yoga_summary_data, tablefmt="plain")
    result_table = f"\n Four-Week Rolling Yoga Summary \n{overall_yoga_summary_table}" +footer
    
    print(result_table)
    return result_table

def give_swim_summary(swim_activities):
    total_swim_time = 0
    total_swim_sessions = 0
    for activity in swim_activities:
        total_swim_time += activity["elapsed_time"]
        total_swim_sessions += 1
    avg_swim_session = utils.convert_seconds_in_hhmmss(round(total_swim_time/total_swim_sessions, 2))
    total_swim_time = utils.convert_seconds_in_hhmmss(total_swim_time)
    total_swim_time = convert_seconds_in_hhmmss(total_swim_time)
    
    overall_swim_summary_data =[
        ["Total swim sessions:", f"{total_swim_sessions}"],
        ["Avg swim session:", f"{avg_swim_session}"],
        ["Total swim time:", f"{total_swim_time}"],
        
    ]
    overall_swim_summary_table = tabulate(overall_swim_summary_data, tablefmt="plain")
    result_table = f"\nFour-Week Rolling Swim Summary \n{overall_swim_summary_table}" + footer
    
    print(result_table)
    return result_table

def give_ride_summary(ride_activities):
    total_ride_time = 0
    total_ride_time_hhmmss = 0
    total_ride_sessions = 0
    total_ride_distance = 0
    total_elevation_gain = 0
    
    for activity in ride_activities:
        total_ride_time += activity['moving_time']
        total_ride_sessions += 1
        total_ride_distance += activity['distance']
        total_elevation_gain += activity['total_elevation_gain']
    avg_ride_time = utils.convert_seconds_in_hhmmss(round(total_ride_time / total_ride_sessions, 2))
    total_ride_time_hhmmss = utils.convert_seconds_in_hhmmss(total_ride_time)
    avg_ride_distance = round(total_ride_distance / total_ride_sessions / 1000, 2)
    avg_elevation_gain = round(total_elevation_gain / total_ride_sessions, 2)
    avg_ride_speed = utils.calculate_speed_in_kmph(total_ride_time, total_ride_distance)
    avg_ride_speed = calculate_speed_in_kmph(total_ride_time, total_ride_distance)
    
    overall_ride_summary_data = [
        ["Total ride sessions:", f"{total_ride_sessions}"],
        ["Avg ride time:", f"{avg_ride_time}"],
        ["Total ride time:", f"{total_ride_time_hhmmss}"],
        ["Total ride distance:", f"{total_ride_distance / 1000} Km"],
        ["Avg ride distance:", f"{avg_ride_distance:.2f} Km"],
        ["Total elevation gain:", f"{total_elevation_gain:.2f} m"],
        ["Avg elevation gain:", f"{avg_elevation_gain:.2f} m/ride"],
        ["Avg ride speed:", f"{avg_ride_speed}"]
    ]

    overall_ride_summary_table = tabulate(overall_ride_summary_data, tablefmt="plain")
    result_table = f"\nFour-Week Rolling Ride Summary\n{overall_ride_summary_table}" + footer
    
    
    print(result_table)
    return result_table

def give_run_summary(run_activities):
    tot_distance_ran_month = 0
    avg_distance_per_run = 0
    tot_elevation_gain = 0
    avg_elevation_gain = 0
    tot_trail_distance = 0
    total_runs_month = 0
    total_trail_runs_month = 0
    total_road_runs_month = 0
    tot_road_distance = 0
    tot_elevation_gain_road = 0
    avg_trail_distance = 0
    avg_mov_speed_trail = 0
    avg_elapsed_speed_trail = 0
    tot_elevation_gain_trail=0
    avg_elevation_gain_trail=0
    
    tot_elapsed_time = 0
    tot_moving_time = 0
    tot_moving_time_road = 0
    tot_moving_time_trail = 0
    
    road_runs_available = False
    trail_runs_available = False

    for activity in run_activities:
        tot_elapsed_time += activity['elapsed_time']
        tot_moving_time += activity['moving_time']
        moving_time_hhmm = utils.convert_seconds_in_hhmmss(tot_moving_time)
        elapsed_time_hhmm = utils.convert_seconds_in_hhmmss(tot_elapsed_time)
        elapsed_time_hhmm = convert_seconds_in_hhmmss(tot_elapsed_time)
        
        # For All runs 
        total_runs_month += 1
        tot_distance_ran_month += activity['distance'] / 1000  # Convert meters to Km directly
        tot_elevation_gain += activity['total_elevation_gain']
        
        # For Road runs
        if activity['sport_type'] == 'Run':
            road_runs_available = True
            total_road_runs_month += 1
            tot_road_distance += activity['distance'] / 1000
            tot_elevation_gain_road += activity['total_elevation_gain']
            tot_moving_time_road+= activity['moving_time']
        
        # For Trail runs
        elif activity['sport_type'] == 'TrailRun':
            trail_runs_available = True
            total_trail_runs_month += 1
            tot_trail_distance += activity['distance'] / 1000
            tot_elevation_gain_trail += activity['total_elevation_gain']
            tot_moving_time_trail += activity['moving_time']
            
    
    # Calculate Averages
    avg_distance_per_run = tot_distance_ran_month / total_runs_month if total_runs_month else 0
    avg_elevation_gain = tot_elevation_gain / total_runs_month if total_runs_month else 0
    avg_road_distance = tot_road_distance / total_road_runs_month if total_road_runs_month else 0
    avg_trail_distance=tot_trail_distance/total_trail_runs_month if total_trail_runs_month else 0
    avg_elevation_gain_road = tot_elevation_gain_road / total_road_runs_month if total_road_runs_month else 0
    avg_elevation_gain_trail = tot_elevation_gain_trail / total_trail_runs_month if total_trail_runs_month else 0
    avg_mov_speed = utils.calculate_speed(tot_moving_time, tot_distance_ran_month)
    avg_mov_speed_road = utils.calculate_speed(tot_moving_time_road, tot_road_distance)
    avg_mov_speed_trail = utils.calculate_speed(tot_moving_time_trail, tot_trail_distance)
    # Formatting with two decimal places
    tot_distance_ran_month = f"{tot_distance_ran_month:.2f}"
    avg_distance_per_run = f"{avg_distance_per_run:.2f}"
    tot_road_distance = f"{tot_road_distance:.2f}"
    avg_road_distance = f"{avg_road_distance:.2f}"
    tot_trail_distance = f"{tot_trail_distance:.2f}"
    avg_trail_distance = f"{avg_trail_distance:.2f}"
    tot_elevation_gain = f"{tot_elevation_gain:.2f}"
    avg_elevation_gain = f"{avg_elevation_gain:.2f}"
    tot_elevation_gain_road = f"{tot_elevation_gain_road:.2f}"
    avg_elevation_gain_road = f"{avg_elevation_gain_road:.2f}"
    
    tot_elevation_gain_trail = f"{tot_elevation_gain_trail:.2f}"
    avg_elevation_gain_trail = f"{avg_elevation_gain_trail:.2f}"

    # Overall summary
    overall_summary_data = [
        ["Total runs:", total_runs_month],
        ["Total distance:", f"{tot_distance_ran_month} Km"],
        ["Average distance:", f"{avg_distance_per_run} Km/run"],
        ["Average pace:", avg_mov_speed],
        ["Total elevation gain:", f"{tot_elevation_gain} m"],
        ["Total moving time:", moving_time_hhmm],
        ["Total elapsed time:", elapsed_time_hhmm],
    ]
    
    if road_runs_available:
        road_runs_summary_data = [
            ["Total road runs:", total_road_runs_month],
            ["Total distance on road:", f"{tot_road_distance} Km"],
            ["Average distance on road:", f"{avg_road_distance} Km/run"],
            ["Total elevation gain on road:", f"{tot_elevation_gain_road} m"],
            ["Average moving pace on roads:", avg_mov_speed_road]
        ]
        
    # Trail runs summary
    if trail_runs_available:
        trail_runs_summary_data = [
            ["Total trail runs:", total_trail_runs_month],
            ["Total distance on trails:", f"{tot_trail_distance} Km"],
            ["Average distance on trails:", f"{avg_trail_distance} Km/run"],
            ["Total elevation gain on trails:", f"{tot_elevation_gain_trail} m"],
            ["Average elevation gain on trails:", f"{avg_elevation_gain_trail} m/run"],
            ["Average moving pace on trails:", avg_mov_speed_trail]
        ]
    
    if not trail_runs_available or not road_runs_available:        
        result_table = "\n\nFour-Week Rolling Run Summary\n"
        # result_table += tabulate(overall_summary_data, tablefmt="plain")r
        formatted_table = format_as_simple_markdown_table(overall_summary_data)
        result_table += formatted_table
    
    if trail_runs_available and road_runs_available:
        result_table = "\nFour-Week Rolling Run Summary\n"
        result_table += tabulate(overall_summary_data[0:3], tablefmt="plain")    
        result_table += "\n\nRoad Runs:\n"
        result_table += tabulate(road_runs_summary_data, tablefmt="plain")
        result_table += "\n\nTrail Runs:\n"
        result_table += tabulate(trail_runs_summary_data, tablefmt="plain")
    
    result_table += footer
        
    print(result_table)

    return result_table


def format_as_simple_markdown_table(data):
     # Find the maximum length of the labels (left column)
    max_label_length = max(len(label) for label, _ in data)

    # Create each row, aligning the values to the right of the longest label
    formatted_lines = [
        f"{label.ljust(max_label_length)}: {value}"
        for label, value in data  
    ]

    # Join all lines together with newline characters
    return "\n".join(formatted_lines)


def give_walk_summary(walk_activities):
  tot_distance_walked_month = 0
  avg_distance_per_walk = 0
  tot_elevation_gain = 0
  avg_elevation_gain = 0
  tot_moving_time = 0
  avg_mov_speed = 0
  tot_elapsed_time = 0
  avg_elapsed_speed = 0

  for activity in walk_activities:
    tot_elapsed_time += activity['elapsed_time']
    tot_moving_time += activity['moving_time']

    # Calculate averages in meters or km based on preference
    tot_distance_walked_month += round(activity['distance'] / 1000, 2)  # In km
    avg_distance_per_walk = round(tot_distance_walked_month / len(walk_activities), 2)
    tot_elevation_gain += round(int(activity['total_elevation_gain']), 2)
    avg_mov_speed = utils.calculate_speed(tot_moving_time, tot_distance_walked_month)
    avg_elapsed_speed = utils.calculate_speed(tot_elapsed_time, tot_distance_walked_month)
    avg_elapsed_speed = calculate_speed(tot_elapsed_time, tot_distance_walked_month)

  result_table = ""

  # Overall walk summary
  walk_summary_data = [
    ["Total walks: ", f"{len(walk_activities)}"],
    ["Total distance: ", f"{tot_distance_walked_month} Km"],
    ["Average distance:", f"{avg_distance_per_walk} Km/walk"],
    ["Average moving pace: ", f"{avg_mov_speed}"],
    ["Total moving time: ", f"{convert_seconds_in_hhmmss(tot_moving_time)}"],
    ["Total elapsed time: ", f"{convert_seconds_in_hhmmss(tot_elapsed_time)}"],
 
  ]

  result_table += "\nFour-Week Rolling Walk Summary \n"
  result_table += tabulate(walk_summary_data, tablefmt="plain")

  result_table += footer

  print(result_table)

  return result_table
