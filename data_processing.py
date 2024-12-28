from tabulate import tabulate
footer = "\n \n Subscribe on https://strava-summariser.vercel.app/ \nStats created using StravaAPI by Omkar Jadhav"

def convert_seconds_in_hhmmss(seconds):
    hours = int(seconds//3600)
    minutes = int((seconds%3600)//60)
    seconds = int(seconds % 60)
    return str(hours).zfill(2) +':' + str(minutes).zfill(2) +':'+ str(seconds).zfill(2)

def calculate_speed(moving_time, distance):
    mov_speed_min, mov_speed_sec = map(int,divmod(moving_time/distance, 60))
    return f"{int(mov_speed_min):02d}:{int(mov_speed_sec):02d} min/Km"

def calculate_speed_in_kmph(moving_time, distance):
    speed_kph = (distance / 1000) / (moving_time / 3600)
    return f"{speed_kph:.2f} km/hr"

def give_weighttraining_summary(WeightTraining_activities):
    total_strength_training_time = 0
    total_sessions = 0
    for activity in WeightTraining_activities:
        total_strength_training_time += activity["moving_time"]
        total_sessions += 1
    
    avg_strength_training_session = convert_seconds_in_hhmmss(round(total_strength_training_time/total_sessions, 2))
    total_strength_training_time = convert_seconds_in_hhmmss(total_strength_training_time)
    
    overall_strength_training_summary_data =[
        ["Total strength_training sessions:", f"{total_sessions}"],
        ["Avg strength_training session:", f"{avg_strength_training_session}"],
        ["Total strength_training time:", f"{total_strength_training_time}"],
        
    ]
    overall_strength_training_summary_table = tabulate(overall_strength_training_summary_data, tablefmt="plain")
    result_table = f"\n Four Week Overall strength training Summary \n{overall_strength_training_summary_table}" +footer
    
    print(result_table)
    return result_table

def give_yoga_summary(yoga_activities):
    total_yoga_time = 0
    total_sessions = 0
    for activity in yoga_activities:
        total_yoga_time += activity["elapsed_time"]
        total_sessions += 1
    
    avg_yoga_session = convert_seconds_in_hhmmss(round(total_yoga_time/total_sessions, 2))
    total_yoga_time = convert_seconds_in_hhmmss(total_yoga_time)
    
    overall_yoga_summary_data =[
        ["Total yoga sessions:", f"{total_sessions}"],
        ["Avg yoga session:", f"{avg_yoga_session}"],
        ["Total yoga time:", f"{total_yoga_time}"],
        
    ]
    overall_yoga_summary_table = tabulate(overall_yoga_summary_data, tablefmt="plain")
    result_table = f"\n Four-Week Rolling Overall Yoga Summary \n{overall_yoga_summary_table}" +footer
    
    print(result_table)
    return result_table

def give_swim_summary(swim_activities):
    total_swim_time = 0
    total_swim_sessions = 0
    for activity in swim_activities:
        total_swim_time += activity["elapsed_time"]
        total_swim_sessions += 1
    
    avg_swim_session = convert_seconds_in_hhmmss(round(total_swim_time/total_swim_sessions, 2))
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
    
    avg_ride_time = convert_seconds_in_hhmmss(round(total_ride_time / total_ride_sessions, 2))
    total_ride_time_hhmmss = convert_seconds_in_hhmmss(total_ride_time)
    avg_ride_distance = round(total_ride_distance / total_ride_sessions / 1000, 2)
    avg_elevation_gain = round(total_elevation_gain / total_ride_sessions, 2)
    avg_ride_speed = calculate_speed_in_kmph(total_ride_time, total_ride_distance)
    
    overall_ride_summary_data = [
        ["Total ride sessions:", f"{total_ride_sessions}"],
        ["Avg ride time:", f"{avg_ride_time}"],
        ["Total ride time:", f"{total_ride_time_hhmmss}"],
        ["Total ride distance:", f"{total_ride_distance / 1000} Km"],
        ["Avg ride distance:", f"{avg_ride_distance} Km"],
        ["Total elevation gain:", f"{total_elevation_gain} m"],
        ["Avg elevation gain:", f"{avg_elevation_gain} m/ride"],
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
    
    tot_elapsed_time = 0
    tot_moving_time = 0
    
    road_runs_available = False
    trail_runs_available = False

    for activity in run_activities:
        tot_elapsed_time += activity['elapsed_time']
        tot_moving_time += activity['moving_time']
        
        moving_time_hhmm = convert_seconds_in_hhmmss(tot_moving_time)
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
        
        # For Trail runs
        elif activity['sport_type'] == 'TrailRun':
            trail_runs_available = True
            total_trail_runs_month += 1
            tot_trail_distance += activity['distance'] / 1000
    
    # Calculate Averages
    avg_distance_per_run = tot_distance_ran_month / total_runs_month if total_runs_month else 0
    avg_elevation_gain = tot_elevation_gain / total_runs_month if total_runs_month else 0
    avg_road_distance = tot_road_distance / total_road_runs_month if total_road_runs_month else 0
    avg_elevation_gain_road = tot_elevation_gain_road / total_road_runs_month if total_road_runs_month else 0
    avg_trail_distance = tot_trail_distance / total_trail_runs_month if total_trail_runs_month else 0
    avg_mov_speed = calculate_speed(tot_moving_time, tot_distance_ran_month)
    avg_elapsed_speed = calculate_speed(tot_elapsed_time, tot_distance_ran_month)

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

    # Overall summary
    overall_summary_data = [
        ["Total runs:", total_runs_month],
        ["Total distance:", f"{tot_distance_ran_month} Km"],
        ["Average distance:", f"{avg_distance_per_run} Km/run"],
        ["Average pace:", avg_mov_speed],
        ["Total elevation gain:", f"{tot_elevation_gain} m"],
        ["Average elevation gain:", f"{avg_elevation_gain} m/run"],
        ["Total moving time:", moving_time_hhmm],
        ["Total elapsed time:", elapsed_time_hhmm],
        ["Average elapsed speed:", avg_elapsed_speed]
    ]
    
    result_table = "\nFour-Week Rolling Overall Run Summary\n"
    result_table += tabulate(overall_summary_data, tablefmt="plain")

    # Road runs summary
    if road_runs_available:
        road_runs_summary_data = [
            ["Total road runs:", total_road_runs_month],
            ["Total distance on road:", f"{tot_road_distance} Km"],
            ["Average distance on road:", f"{avg_road_distance} Km/run"],
            ["Total elevation gain on road:", f"{tot_elevation_gain_road} m"],
            ["Average elevation gain on road:", f"{avg_elevation_gain_road} m/run"],
            ["Average moving pace on roads:", avg_mov_speed]
        ]
        result_table += "\n\nFour-Week Rolling Road Run Summary\n"
        result_table += tabulate(road_runs_summary_data, tablefmt="plain")

    # Trail runs summary
    if trail_runs_available:
        trail_runs_summary_data = [
            ["Total trail runs:", total_trail_runs_month],
            ["Total distance on trails:", f"{tot_trail_distance} Km"],
            ["Average distance on trails:", f"{avg_trail_distance} Km/run"],
            ["Total elevation gain on trails:", f"{tot_elevation_gain} m"],
            ["Average elevation gain on trails:", f"{avg_elevation_gain} m/run"],
            ["Average moving pace on trails:", avg_mov_speed]
        ]
        result_table += "\n\nFour-Week Rolling Trail Run Summary\n"
        result_table += tabulate(trail_runs_summary_data, tablefmt="plain")

    print(result_table)

    return result_table

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
    avg_elevation_gain = round(tot_elevation_gain / len(walk_activities), 2)
    avg_mov_speed = calculate_speed(tot_moving_time, tot_distance_walked_month)
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
