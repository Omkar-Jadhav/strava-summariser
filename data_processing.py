from tabulate import tabulate

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
    result_table = f"\n------- Four-Week Rolling Overall Yoga Summary -------\n{overall_yoga_summary_table}\n\n ------- Stats created using StravaAPI by Omkar Jadhav ------\n -- Subscribe on https://strava-summariser.vercel.app/ --"
    
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
    result_table = f"\n------- Four-Week Rolling Swim Summary -------\n{overall_swim_summary_table}\n\n ------- Stats created using StravaAPI by Omkar Jadhav ------\n -- Subscribe on https://strava-summariser.vercel.app/ --"
    
    print(result_table)
    return result_table

def give_ride_summar(ride_activities):
    total_ride_time = 0
    total_ride_sessions = 0
    total_ride_distance = 0
    total_elevation_gain = 0
    
    for activity in ride_activities:
        total_ride_time += activity['elapsed_time']
        total_ride_sessions += 1
        total_ride_distance += activity['distance']
        total_elevation_gain += activity['total_elevation_gain']
    
    avg_ride_time = convert_seconds_in_hhmmss(round(total_ride_time / total_ride_sessions, 2))
    total_ride_time = convert_seconds_in_hhmmss(total_ride_time)
    avg_ride_distance = round(total_ride_distance / total_ride_sessions / 1000, 2)
    avg_elevation_gain = round(total_elevation_gain / total_ride_sessions, 2)
    avg_ride_speed = calculate_speed_in_kmph(total_ride_time, total_ride_distance)
    
    overall_ride_summary_data = [
        ["Total ride sessions:", f"{total_ride_sessions}"],
        ["Avg ride time:", f"{avg_ride_time}"],
        ["Total ride time:", f"{total_ride_time}"],
        ["Total ride distance:", f"{total_ride_distance / 1000} Km"],
        ["Avg ride distance:", f"{avg_ride_distance} Km"],
        ["Total elevation gain:", f"{total_elevation_gain} m"],
        ["Avg elevation gain:", f"{avg_elevation_gain} m/ride"],
        ["Avg ride speed:", f"{avg_ride_speed}"]
    ]

    overall_ride_summary_table = tabulate(overall_ride_summary_data, tablefmt="plain")
    result_table = f"\n------- Four-Week Rolling Ride Summary -------\n{overall_ride_summary_table}\n\n ------- Stats created using StravaAPI by Omkar Jadhav ------\n -- Subscribe on https://strava-summariser.vercel.app/ --"
    
    print(result_table)
    return result_table

def give_run_summary(run_activities):
    tot_distance_ran_year = 0
    tot_distance_ran_month = 0
    avg_distance_per_run = 0
    avg_distance_per_week = 0
    tot_elevation_gain = 0
    avg_elevation_gain = 0
    tot_elevation_gain_trail = 0
    avg_elevation_gain_trail = 0
    tot_trail_distance = 0
    moving_time_trail = 0
    elapsed_time_trail = 0
    total_runs_month = 0
    total_trail_runs_month = 0
    total_road_runs_month = 0
    tot_road_distance = 0
    tot_elevation_gain_road = 0
    moving_time_road = 0
    avg_elapsed_speed_trail = 0
    tot_elapsed_time = 0
    tot_moving_time = 0
    avg_trail_distance = 0
    avg_mov_speed_trail = 0
    
    road_runs_available = False
    trail_runs_available = False

    for activity in run_activities:
        tot_elapsed_time += activity['elapsed_time']
        tot_moving_time += activity['moving_time']
        
        moving_time_hhmm = convert_seconds_in_hhmmss(tot_moving_time)
        elapsed_time_hhmm = convert_seconds_in_hhmmss(tot_elapsed_time)
        
        # For All runs 
        total_runs_month += 1
        tot_distance_ran_month += round(activity['distance']/1000, 2)
        avg_distance_per_run = round(tot_distance_ran_month/total_runs_month, 2)

        tot_elevation_gain += round(int(activity['total_elevation_gain']), 2)
        avg_elevation_gain = round(tot_elevation_gain/total_runs_month, 2)
        
        avg_mov_speed = calculate_speed(tot_moving_time, tot_distance_ran_month)
        avg_elapsed_speed = calculate_speed(tot_elapsed_time, tot_distance_ran_month)
        
        # For Road runs
        if activity['sport_type'] == 'Run':
            road_runs_available = True
            total_road_runs_month += 1
            tot_road_distance += round(activity['distance']/1000, 2)  # In km
            avg_road_distance = round(tot_road_distance / total_road_runs_month, 2)
            tot_elevation_gain_road += int(activity['total_elevation_gain'])
            avg_elevation_gain_road = round(tot_elevation_gain_road / total_road_runs_month, 2)
            
            moving_time_road += activity['moving_time']
            avg_mov_speed_road = calculate_speed(moving_time_road, tot_road_distance)
        
        
        # For Trail runs
        if activity['sport_type'] == 'TrailRun':
            trail_runs_available = True
            total_trail_runs_month += 1
            tot_trail_distance += round(activity['distance']/1000, 2)  # In km
            avg_trail_distance = round(tot_trail_distance / total_trail_runs_month, 2)
            tot_elevation_gain_trail += int(activity['total_elevation_gain'])
            avg_elevation_gain_trail = round(tot_elevation_gain_trail / total_trail_runs_month, 2)
            
            moving_time_trail += activity['moving_time']
            elapsed_time_trail += activity['moving_time']
            avg_mov_speed_trail = calculate_speed(moving_time_trail, tot_trail_distance)
            avg_elapsed_speed_trail = calculate_speed(elapsed_time_trail, tot_trail_distance)
            
    result_table = ""
    
    # Overall summary
    if road_runs_available and trail_runs_available:
        overall_summary_data = [
            ["Total runs: ", f"{total_runs_month}"],
            ["Total distance: ", f"{tot_distance_ran_month} Km"],
            ["Average distance:", f"{avg_distance_per_run} Km/run"],
            ["Average pace: ", f"{avg_mov_speed}"],
            ["Total elevation gained: ", f"{tot_elevation_gain} m"],
            ["Avg elevation gain: ", f"{avg_elevation_gain} m/run"],
            ["Total moving time: ", f"{moving_time_hhmm}"],
            ["Total elapsed time: ", f"{elapsed_time_hhmm}"],
            ["Avg pace: ", f"{avg_mov_speed}"]
        ]
        
        result_table += "\n------- Four-Week Rolling Overall Run Summary -------\n"
        result_table += tabulate(overall_summary_data, tablefmt="plain")

    # Road runs summary
    if road_runs_available:
        road_runs_summary_data = [
            ["Total road runs: ", f"{total_road_runs_month}"],
            ["Total distance on road: ", f"{tot_road_distance} Km"],
            ["Avg distance on road: ", f"{avg_road_distance} km/run"],
            ["Total elevation gain on road: ", f"{tot_elevation_gain_road} m"],
            ["Avg elevation gain on road: ", f"{avg_elevation_gain_road} m/run"],
            ["Avg pace on roads: ", f"{avg_mov_speed_road}"]
        ]
        result_table += "\n\n------- Four-Week Rolling Road Run Summary -------\n"
        result_table += tabulate(road_runs_summary_data, tablefmt="plain")

    # Trail runs summary
    if trail_runs_available:
        trail_runs_summary_data = [
            ["Total trail runs: ", f"{total_trail_runs_month}"],
            ["Total distance on trails: ", f"{tot_trail_distance} Km"],
            ["Avg distance on trails: ", f"{avg_trail_distance} km/run"],
            ["Total elevation gain on trails: ", f"{tot_elevation_gain_trail} m"],
            ["Avg elevation gain on trails: ", f"{avg_elevation_gain_trail} m/run"],
            ["Avg moving pace on trails: ", f"{avg_mov_speed_trail}"],
            ["Avg elapsed time pace on trails: ", f"{avg_elapsed_speed_trail}"]
        ]
        result_table += "\n\n------- Four-Week Rolling Trail Run Summary -------\n"
        result_table += tabulate(trail_runs_summary_data, tablefmt="plain")

    result_table += "\n -- Subscribe on https://strava-summariser.vercel.app/ --\nStats created using StravaAPI by Omkar Jadhav"
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

  result_table += "\n------- Four-Week Rolling Walk Summary -------\n"
  result_table += tabulate(walk_summary_data, tablefmt="plain")

  result_table += "\n -- Subscribe on https://strava-summariser.vercel.app/ --\n"
  result_table += "Stats created using StravaAPI by Omkar Jadhav"

  print(result_table)

  return result_table
