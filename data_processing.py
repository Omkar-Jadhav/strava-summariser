from tabulate import tabulate
        
def convert_seconds_in_hhmmss(seconds):
    hours = int(seconds//3600)
    minutes = int((seconds%3600)//60)
    seconds = int(seconds % 60)
    return str(hours).zfill(2) +':' + str(minutes).zfill(2) +':'+ str(seconds).zfill(2)

def calculate_speed(moving_time, distance):
    mov_speed_min, mov_speed_sec = map(int,divmod(moving_time/distance, 60))
    return str(mov_speed_min) + ':' + str(mov_speed_sec) + ' min/Km'


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
    result_table = f"\n------- Four-Week Rolling Overall Yoga Summary -------\n{overall_yoga_summary_table}\n\n ------- Stats created using StravaAPI by Omkar ------"
    
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
    result_table = f"\n------- Four-Week Rolling Swim Summary -------\n{overall_swim_summary_table}\n\n ------- Stats created using StravaAPI by Omkar ------"
    
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
    total_road_runs_month =0 
    tot_road_distance = 0
    tot_elevation_gain_road = 0
    moving_time_road = 0
    avg_elapsed_speed_trail = 0
    tot_elapsed_time = 0
    tot_moving_time = 0
    
    for activity in run_activities:
        tot_elapsed_time += activity['elapsed_time']
        tot_moving_time += activity['moving_time']
        
        moving_time_hhmm = convert_seconds_in_hhmmss(tot_moving_time)
        elapsed_time_hhmm = convert_seconds_in_hhmmss(tot_elapsed_time)
        
        # For All runs 
        total_runs_month+=1
        tot_distance_ran_month +=round(activity['distance']/1000,2)
        avg_distance_per_run = round(tot_distance_ran_month/total_runs_month,2)

        tot_elevation_gain += int(activity['total_elevation_gain'])
        avg_elevation_gain = round(tot_elevation_gain/total_runs_month,2)
        
        avg_mov_speed = calculate_speed(tot_moving_time, tot_distance_ran_month)
        avg_elapsed_speed = calculate_speed(tot_elapsed_time, tot_distance_ran_month)
        
        # For Road runs
        if(activity['sport_type']=='Run'):
            total_road_runs_month +=1
            tot_road_distance += round(activity['distance']/1000,2) #In km
            avg_road_distance = round(tot_road_distance/ total_road_runs_month,2)
            tot_elevation_gain_road += int(activity['total_elevation_gain'])
            avg_elevation_gain_road = round(tot_elevation_gain_road/total_road_runs_month,2)
            
            moving_time_road += activity['moving_time']
            avg_mov_speed_road =calculate_speed(moving_time_road, tot_road_distance)
        
        
        # For Trail runs
        if(activity['sport_type']=='TrailRun'):
            total_trail_runs_month +=1
            tot_trail_distance += round(activity['distance']/1000,2) #In km
            avg_trail_distance = round(tot_trail_distance/ total_trail_runs_month,2)
            tot_elevation_gain_trail += int(activity['total_elevation_gain'])
            avg_elevation_gain_trail = round(tot_elevation_gain_trail/total_trail_runs_month,2)
            
            moving_time_trail += activity['moving_time']
            elapsed_time_trail += activity['moving_time']
            avg_mov_speed_trail = calculate_speed(moving_time_trail,tot_trail_distance)
            avg_elapsed_speed_trail = calculate_speed(elapsed_time_trail,tot_trail_distance)
            
        

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

    # Data for road runs summary
    road_runs_summary_data = [
        ["Total road runs: ", f"{total_road_runs_month}"],
        ["Total distance on road: ", f"{tot_road_distance} Km"],
        ["Avg distance on road: ", f"{avg_road_distance} km/run"],
        ["Total elevation gain on road: ", f"{tot_elevation_gain_road} m"],
        ["Avg elevation gain on road: ", f"{avg_elevation_gain_road} m/run"],
        ["Avg pace on roads: ", f"{avg_mov_speed_road}"]
    ]

    # Data for trail runs summary
    trail_runs_summary_data = [
        ["Total trail runs: ", f"{total_trail_runs_month}"],
        ["Total distance on trails: ", f"{tot_trail_distance} Km"],
        ["Avg distance on trails: ", f"{avg_trail_distance} km/run"],
        ["Total elevation gain on trails: ", f"{tot_elevation_gain_trail} m"],
        ["Avg elevation gain on trails: ", f"{avg_elevation_gain_trail} m/run"],
        ["Avg moving pace on trails: ", f"{avg_mov_speed_trail}"],
        ["Avg elapsed time pace on trails: ", f"{avg_elapsed_speed_trail}"]
    ]



    # Store tables in variables with headers
    header_table = tabulate([], headers= 'Overall summary')
    overall_summary_table = tabulate(overall_summary_data, tablefmt="plain")
    road_runs_summary_table = tabulate(road_runs_summary_data, tablefmt="plain")
    trail_runs_summary_table = tabulate(trail_runs_summary_data, tablefmt="plain")

    # Combine tables and print
    result_table = f"\n------- Four-Week Rolling Overall Run Summary -------\n{overall_summary_table}\n\n  ------- Four-Week Rolling Road Run Summary -------\n {road_runs_summary_table}\n\n------- Four-Week Rolling Trail Run Summary -------\n{trail_runs_summary_table} \n \nStats created using StravaAPI by Omkar"
    print(result_table)
    
    return result_table
        