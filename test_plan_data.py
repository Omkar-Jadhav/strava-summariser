athlete_goals= """    Athlete goal is to train for 100Km ultra trail with 5000m elevation by 2025-03-09.
    The Athlete is currently at a fitness level of intermediate and  can commit 1.5hr per day for training on weekdays.
    In past 3 months, longest 3 runs of the Athlete are 1. Distance: 100.3 km, Pace: 11:38 min/Km min/km, Elevation Gain: 3342.0 m with moving time:19:27:15
2. Distance: 42.61 km, Pace: 05:20 min/Km min/km, Elevation Gain: 108.5 m with moving time:03:47:58
3. Distance: 41.86 km, Pace: 14:30 min/Km min/km, Elevation Gain: 2544.0 m with moving time:10:07:03
.
    Athlete has recently performed 100Km ultra trail 3380D+ in 19:30, marathon in 3:45, and race performances from strava are 1. Name: Morning Run, Distance: 42.61 km, Moving Time: 03:47:58, Pace: 05:20 min/Km min/km, Elevation Gain: 108.5 m
2. Name: SRTL 100, Distance: 100.3 km, Moving Time: 19:27:15, Pace: 11:38 min/Km min/km, Elevation Gain: 3342.0 m
. 
    He/she can train for 5 days in a week and can do 4 strength sessions per week.
    The Athlete has  and  that you need to consider while creating the plan.
    The Athlete prefers Long runs and long trails on weekends only and has  that you need to consider while creating the plan."""
    
athlete_baseline_stats ={'distance_mean': 10.817176923076925, 'distance_std': 9.89218258180545, 'speed_mean': 2.615576923076923, 'speed_std': 0.5707811228804667, 'hr_mean': 141.81153846153845, 'hr_std': 13.701188239404555, 'max_distance': 42.612, 'max_pace': 3.402}
athlete_id = 64768690
past_3m_summarised =""" **Summary of Athlete's Past 3 Months Running History**

The athlete has a diverse and extensive running history over the past 3 months, consisting of various types of runs, including long runs, tempo runs, easy runs, recovery runs, intervals, trail runs, and hill workouts.

**Total Distance and Elevation Gain**

The total distance covered by the athlete over the past 3 months is approximately 734.14 km, with a total elevation gain of 10,341.2 meters.

**Types of Runs and Frequency**

1. **Long Runs**: 4 long runs, with distances ranging from 22.33 km to 30.33 km, and average paces between 05:25 min/km and 06:09 min/km.
2. **Tempo Runs**: 5 tempo runs, with distances ranging from 1.74 km to 15.23 km, and average paces between 04:57 min/km and 05:54 min/km.
3. **Easy Runs**: 11 easy runs, with distances ranging from 3.07 km to 11.03 km, and average paces between 06:00 min/km and 06:27 min/km.
4. **Recovery Runs**: 13 recovery runs, with no specific distance or pace data available.
5. **Intervals**: 5 interval workouts, with varying lap distances and paces, and a mix of fast and slow laps.
6. **Trail Runs**: 7 trail runs, with distances ranging from 4.44 km to 41.86 km, and significant elevation gains in some cases.
7. **Hill Workouts**: 5 hill workouts, with distances ranging from 6.05 km to 18.02 km, and average paces between 05:16 min/km and 06:52 min/km.

**Performance Trends and Insights**

1. The athlete's average pace for long runs has been relatively consistent, ranging from 05:25 min/km to 06:09 min/km.
2. Tempo runs have shown a mix of fast and slow paces, with some runs having average paces under 05:00 min/km.
3. Easy runs have been completed at a relatively consistent pace, ranging from 06:00 min/km to 06:27 min/km.
4. Intervals have shown a mix of fast and slow laps, with some laps having paces under 04:00 min/km.
5. Trail runs have been completed with significant elevation gains, indicating the athlete's ability to handle challenging terrain.
6. Hill workouts have been completed at a relatively consistent pace, ranging from 05:16 min/km to 06:52 min/km.

**Racing Performance**

The athlete has completed 2 races, one of 42.61 km and another of 100.30 km, with average paces of 05:20 min/km and 11:38 min/km, respectively. The athlete's performance in these races suggests a strong endurance base and ability to handle long distances."""


past_month_run_details = """
print(past_month_runs_details)
1. Day 0: Trail Run
14.40 km | ↗️1017.0m
2. Day 2: Trail Run
4.77 km | ↗️202.0m
3. Day 2:Base Training of 8.10 km at 05:24 min/Km | ↗️12.0m
4. Day 4: Recovery Run
5. Day 5: Trail Run
4.44 km | ↗️102.0m
6. Day 7: Race
42.61 km at 05:20 min/Km | ↗️108.5m
7. Day 7: Tempo Workout of 1.74 km at 04:57 min/Km | ↗️0.0m
8. Day 8: Easy Run of 3.07 km at 06:00 min/Km | ↗️7.0m 
9. Day 9: Intervals
Lap 1: 1.00 km at 5.71 min/Km
Lap 2: 1.00 km at 5.52 min/Km
Lap 3: 1.00 km at 4.84 min/Km
Lap 4: 1.00 km at 4.76 min/Km
Lap 5: 1.00 km at 4.52 min/Km
Lap 6: 0.18 km at 4.34 min/Km
Lap 7: 0.10 km at 11.66 min/Km
Lap 8: 0.12 km at 3.75 min/Km
Lap 9: 0.13 km at 11.74 min/Km
Lap 10: 0.14 km at 3.86 min/Km
Lap 11: 1.00 km at 6.56 min/Km
Lap 12: 0.65 km at 6.27 min/Km
10. Day 11: Easy Run of 11.03 km at 06:09 min/Km | ↗️42.9m 
11. Day 11: Recovery Run
12. Day 14: Recovery Run
13. Day 14: Long Run
30.05 km at 05:25 min/Km and 182.7m
14. Day 14: Intervals
Lap 1: 1.00 km at 5.81 min/Km
Lap 2: 1.00 km at 5.56 min/Km
Lap 3: 1.00 km at 5.52 min/Km
Lap 4: 1.00 km at 5.27 min/Km
Lap 5: 0.11 km at 6.06 min/Km
Lap 6: 0.20 km at 3.15 min/Km
Lap 7: 0.10 km at 10.35 min/Km
Lap 8: 0.20 km at 3.13 min/Km
Lap 9: 0.10 km at 11.26 min/Km
Lap 10: 0.21 km at 3.1 min/Km
Lap 11: 0.09 km at 12.08 min/Km
Lap 12: 0.22 km at 3.36 min/Km
Lap 13: 0.10 km at 11.26 min/Km
15. Day 16:Base Training of 10.21 km at 05:29 min/Km | ↗️40.8m
16. Day 17: Recovery Run
17. Day 17: Intervals
Lap 1: 3.02 km at 5.61 min/Km
Lap 2: 1.61 km at 4.08 min/Km
Lap 3: 0.80 km at 11.74 min/Km
Lap 4: 1.61 km at 3.85 min/Km
Lap 5: 0.80 km at 11.34 min/Km
Lap 6: 1.61 km at 4.22 min/Km
Lap 7: 0.80 km at 10.29 min/Km
Lap 8: 0.06 km at 9.31 min/Km
18. Day 17: Intervals
Lap 1: 1.00 km at 5.57 min/Km
Lap 2: 1.00 km at 5.43 min/Km
Lap 3: 1.00 km at 5.29 min/Km
Lap 4: 1.00 km at 5.38 min/Km
Lap 5: 1.00 km at 5.5 min/Km
Lap 6: 1.00 km at 5.26 min/Km
Lap 7: 1.00 km at 5.13 min/Km
Lap 8: 1.00 km at 5.11 min/Km
Lap 9: 0.09 km at 5.18 min/Km
Lap 10: 0.11 km at 3.59 min/Km
Lap 11: 0.13 km at 11.9 min/Km
Lap 12: 0.16 km at 3.44 min/Km
Lap 13: 0.11 km at 11.82 min/Km
Lap 14: 0.16 km at 3.12 min/Km
Lap 15: 0.25 km at 6.59 min/Km
19. Day 17:Base Training of 1.51 km at 04:53 min/Km | ↗️3.0m
20. Day 18:Base Training of 13.51 km at 05:27 min/Km | ↗️23.0m
21. Day 20: Easy Run of 5.02 km at 06:18 min/Km | ↗️5.0m 
22. Day 20: Long Run
22.33 km at 06:09 min/Km and 286.5m
23. Day 21: Hill Workout of 10.53 km at 06:32 min/Km | ↗️160.0m
24. Day 22: Easy Run of 5.04 km at 06:20 min/Km | ↗️10.0m 
25. Day 25: Recovery Run
26. Day 28: Long Run
30.33 km at 05:29 min/Km and 180.2m
"""


goal_summary = """
Here is a brief summary of the athlete's goals and current situation:

**Goal:** Complete a 100Km ultra trail with 5000m elevation by March 9, 2025.

**Current Fitness Level:** Intermediate

**Available Training Time:** 1.5 hours/day, 5 days a week

**Recent Performances:**

* Completed a 100Km ultra trail with 3342m elevation in 19:27:15
* Completed a marathon in 3:45
* Recent long runs: 100.3km, 42.61km, and 41.86km with varying paces and elevations

**Training Preferences:**

* Long runs and trails only on weekends
* Can commit to 4 strength sessions per week

This information will be used to create a personalized training plan to help the athlete achieve their goal."""


next_week_plan ="""_Dates: 27/01/2025 - 02/01/2025_\n
**Bird's Eye View of the Plan:**\n\nTo reach the goal of completing a 100Km ultra trail with 5000m elevation by March 9, 2025, the athlete will focus on a structured 6-week training plan. The plan will include a mix of endurance runs, tempo runs, hill repeats, strength training, and mobility workouts. The athlete will aim to increase their weekly mileage by 10-15% each week, with a focus on building endurance and strength.\n\nThe plan will be divided into three phases:\n\n1. Building Endurance (Weeks 1-2): Focus on building weekly mileage, with an emphasis on long runs, tempo runs, and hill repeats.\n2. Building Strength and Endurance (Weeks 3-4): Continue to build weekly mileage, with an added focus on strength training and mobility workouts to improve overall strength and resilience.\n3. Taper and Rest (Weeks 5-6): Gradually reduce weekly mileage to allow for rest and recovery before the event.\n\n**Detailed Workout Plan for Week 1:**\n\n**Monday (1.5 hours)**\n\n* Warm-up: 10-15 minutes of easy running\n* Strength Training:\n\t+ Squats: 3 sets of 10 reps\n\t+ Lunges: 3 sets of 10 reps (per leg)\n\t+ Calf raises: 3 sets of 15 reps\n\t+ Core exercises: 3 sets of 10 reps (plank, Russian twists, etc.)\n* Cool-down: 10-15 minutes of stretching and foam rolling\n\n**Tuesday (1.5 hours)**\n\n* Warm-up: 10-15 minutes of easy running\n* Tempo Run: 30 minutes at a moderate pace (approx. 6:00-6:30 min/km)\n* Cool-down: 10-15 minutes of easy running\n* Mobility Workout:\n\t+ Leg swings: 3 sets of 10 reps (front and back)\n\t+ Hip circles: 3 sets of 10 reps\n\t+ Calf stretches: 3 sets of 10 reps\n\n**Wednesday (1.5 hours)**\n\n* Warm-up: 10-15 minutes of easy running\n* Hill Repeats: 6-8 x 400m hill repeats at a high intensity (approx. 4:00-4:30 min/km)\n* Cool-down: 10-15 minutes of easy running\n* Strength Training:\n\t+ Deadlifts: 3 sets of 10 reps\n\t+ Step-ups: 3 sets of 10 reps (per leg)\n\t+ Calf raises: 3 sets of 15 reps\n\n**Thursday (1.5 hours)**\n\n* Warm-up: 10-15 minutes of easy running\n* Easy Run: 45 minutes at an easy pace (approx. 7:00-7:30 min/km)\n* Cool-down: 10-15 minutes of stretching and foam rolling\n* Mobility Workout:\n\t+ Hip flexor stretches: 3 sets of 10 reps\n\t+ Quad stretches: 3 sets of 10 reps\n\t+ Calf stretches: 3 sets of 10 reps\n\n**Friday (1.5 hours)**\n\n* Warm-up: 10-15 minutes of easy running\n* Long Run: 60 minutes at a moderate pace (approx. 6:30-7:00 min/km)\n* Cool-down: 10-15 minutes of easy running\n* Strength Training:\n\t+ Leg press: 3 sets of 10 reps\n\t+ Calf raises: 3 sets of 15 reps\n\t+ Core exercises: 3 sets of 10 reps (plank, Russian twists, etc.)\n\n**Saturday (Rest Day)**\n\n**Sunday (Long Run Day)**\n\n* Warm-up: 10-15 minutes of easy running\n* Long Run: 2 hours at a moderate pace (approx. 6:30-7:00 min/km) with 1000m elevation gain\n* Cool-down: 10-15 minutes of easy running\n\n**Note:**\n\n* The athlete should listen to their body and adjust the intensity and volume of training based on how they feel.\n* The athlete should also pay attention to their nutrition and hydration to ensure they are fueling their body for optimal performance.\n* The athlete should aim to get 7-9 hours of sleep each night to aid in recovery.\n* The athlete should also incorporate rest and recovery techniques such as foam rolling, stretching, and self-myofascial release to aid in recovery."""

dates = "20/01/2025 - 26/01/2025"

goal_summary = "\nHere is a brief summary of the athlete's goals and current situation:\n\n**Goal:** Complete a 100Km ultra trail with 5000m elevation by March 9, 2025.\n\n**Current Fitness Level:** Intermediate\n\n**Available Training Time:** 1.5 hours/day, 5 days a week\n\n**Recent Performances:**\n\n* Completed a 100Km ultra trail with 3342m elevation in 19:27:15\n* Completed a marathon in 3:45\n* Recent long runs: 100.3km, 42.61km, and 41.86km with varying paces and elevations\n\n**Training Preferences:**\n\n* Long runs and trails only on weekends\n* Can commit to 4 strength sessions per week\n\nThis information will be used to create a personalized training plan to help the athlete achieve their goal."


new_plan="Dates: 03/02/2025 - 09/02/2025\n\nOverview of the previous workouts: The athlete completed a hill workout, two trail runs, and a base training session in the past week, with a total distance of 38.3 km and elevation gain of 1256m. Although the athlete did not follow the prescribed workout plan completely, they still managed to get some quality training done. I applaud the athlete for their efforts, but I expect them to be more consistent with the plan in the upcoming week.\n\nWorkout Plan:\nMonday (1.5 hours)\n- Warm-up: \n▪ Easy running: 10-15 minutes\n- Strength Training: \n▪ Squats: 3 sets of 12 reps\n▪ Lunges: 3 sets of 12 reps (per leg)\n▪ Calf raises: 3 sets of 18 reps\n- Cool-down: \n▪ Stretching and foam rolling: 10-15 minutes\nTuesday (1.5 hours)\n- Warm-up: \n▪ Easy running: 10-15 minutes\n- Tempo Run: \n▪ Moderate pace: 35 minutes at approximately 6:00-6:30 min/km\n- Cool-down: \n▪ Easy running: 10-15 minutes\n- Mobility Workout: \n▪ Leg swings: 3 sets of 12 reps (front and back)\n▪ Hip circles: 3 sets of 12 reps\nWednesday (1.5 hours)\n- Warm-up: \n▪ Easy running: 10-15 minutes\n- Hill Repeats: \n▪ High intensity: 7-9 x 400m hill repeats at approximately 4:00-4:30 min/km\n- Cool-down: \n▪ Easy running: 10-15 minutes\n- Strength Training: \n▪ Deadlifts: 3 sets of 12 reps\n▪ Step-ups: 3 sets of 12 reps (per leg)\nThursday (1.5 hours)\n- Warm-up: \n▪ Easy running: 10-15 minutes\n- Easy Run: \n▪ Easy pace: 50 minutes at approximately 7:00-7:30 min/km\n- Cool-down: \n▪ Stretching and foam rolling: 10-15 minutes\n- Mobility Workout: \n▪ Hip flexor stretches: 3 sets of 12 reps\n▪ Quad stretches: 3 sets of 12 reps\nFriday (1.5 hours)\n- Warm-up: \n▪ Easy running: 10-15 minutes\n- Long Run: \n▪ Moderate pace: 70 minutes at approximately 6:30-7:00 min/km\n- Cool-down: \n▪ Easy running: 10-15 minutes\n- Strength Training: \n▪ Leg press: 3 sets of 12 reps\n▪ Calf raises: 3 sets of 18 reps\nSaturday (Rest Day)\nSunday (2.5 hours)\n- Warm-up: \n▪ Easy running: 10-15 minutes\n- Long Run: \n▪ Moderate pace: 2.5 hours at approximately 6:30-7:00 min/km with 1200m elevation gain\n- Cool-down: \n▪ Easy running: 10-15 minutes\n\nNotes:\n- The athlete should focus on proper nutrition and hydration to support their training.\n- It is essential to get 7-9 hours of sleep each night to aid in recovery.\n- The athlete should incorporate rest and recovery techniques such as foam rolling, stretching, and self-myofascial release to aid in recovery.\n- I expect the athlete to follow the prescribed workout plan more consistently in the upcoming week.\n- The athlete should listen to their body and adjust the intensity and volume of training based on how they feel."



past_week_activity_dtls = "1. Day 0: Hill Workout of 11.03 km at 05:43 min/Km | ↗️25.0m\n2. Day 2: Trail Run\n14.40 km | ↗️1017.0m\n3. Day 5: Trail Run\n4.77 km | ↗️202.0m\n4. Day 5:Base Training of 8.10 km at 05:24 min/Km | ↗️12.0m"


new_plan_2 = "### Dates: 03/02/2025 - 09/02/2025\n### Overview of the previous workouts: \nThe athlete has completed some workouts in the past week, including a hill workout, two trail runs, and a base training session. The details of these workouts are as follows:\n* Day 0: Hill Workout of 11.03 km at 05:43 min/Km with 25.0m elevation gain\n* Day 2: Trail Run of 14.40 km with 1017.0m elevation gain\n* Day 5: Trail Run of 4.77 km with 202.0m elevation gain\n* Day 5: Base Training of 8.10 km at 05:24 min/Km with 12.0m elevation gain\nHowever, the athlete has missed some workouts from the provided plan, including strength training sessions, mobility workouts, and easy runs. It is essential to stay on track with the plan to achieve the goal of completing a 100Km ultra trail with 5000m elevation by March 9, 2025.\n\n### Workout Plan:\n#### Monday \n- Warm-up: 10-15 minutes of easy running\n- Strength Training:\n  * Squats: 3 sets of 12 reps\n  * Lunges: 3 sets of 12 reps (per leg)\n  * Calf raises: 3 sets of 18 reps\n  * Core exercises: 3 sets of 12 reps (plank, Russian twists, etc.)\n- Cool-down: 10-15 minutes of stretching and foam rolling\n\n#### Tuesday \n- Warm-up: 10-15 minutes of easy running\n- Tempo Run: 35 minutes at a moderate pace (approx. 6:00-6:30 min/km)\n- Cool-down: 10-15 minutes of easy running\n- Mobility Workout:\n  * Leg swings: 3 sets of 12 reps (front and back)\n  * Hip circles: 3 sets of 12 reps\n  * Calf stretches: 3 sets of 12 reps\n\n#### Wednesday \n- Warm-up: 10-15 minutes of easy running\n- Hill Repeats: 7-9 x 400m hill repeats at a high intensity (approx. 4:00-4:30 min/km)\n- Cool-down: 10-15 minutes of easy running\n- Strength Training:\n  * Deadlifts: 3 sets of 12 reps\n  * Step-ups: 3 sets of 12 reps (per leg)\n  * Calf raises: 3 sets of 18 reps\n\n#### Thursday \n- Warm-up: 10-15 minutes of easy running\n- Easy Run: 50 minutes at an easy pace (approx. 7:00-7:30 min/km)\n- Cool-down: 10-15 minutes of stretching and foam rolling\n- Mobility Workout:\n  * Hip flexor stretches: 3 sets of 12 reps\n  * Quad stretches: 3 sets of 12 reps\n  * Calf stretches: 3 sets of 12 reps\n\n#### Friday \n- Warm-up: 10-15 minutes of easy running\n- Long Run: 70 minutes at a moderate pace (approx. 6:30-7:00 min/km)\n- Cool-down: 10-15 minutes of easy running\n- Strength Training:\n  * Leg press: 3 sets of 12 reps\n  * Calf raises: 3 sets of 18 reps\n  * Core exercises: 3 sets of 12 reps (plank, Russian twists, etc.)\n\n#### Saturday \n- Rest Day\n\n#### Sunday \n- Warm-up: 10-15 minutes of easy running\n- Long Run: 2.5 hours at a moderate pace (approx. 6:30-7:00 min/km) with 1200m elevation gain\n- Cool-down: 10-15 minutes of easy running\n\n### Notes:\n* The athlete should listen to their body and adjust the intensity and volume of training based on how they feel.\n* The athlete should also pay attention to their nutrition and hydration to ensure they are fueling their body for optimal performance.\n* The athlete should aim to get 7-9 hours of sleep each night to aid in recovery.\n* The athlete should also incorporate rest and recovery techniques such as foam rolling, stretching, and self-myofascial release to aid in recovery.\n* It is essential to stay on track with the plan and complete all the workouts as scheduled to achieve the goal of completing a 100Km ultra trail with 5000m elevation by March 9, 2025."

new_plan_3 ="Dates:29/01/2025 - 04/02/2025\n### Bird's eye view: \nThe workout plan for the next week will focus on building the athlete's endurance, strength, and mobility to reach the goal of completing a 100km trail run by 28/06/2025. The plan will include a mix of easy runs, tempo workouts, hill repeats, and long runs to improve cardiovascular fitness and running efficiency. Strength training and mobility workouts will be added to enhance muscular endurance, flexibility, and injury prevention.\n\n### Workout Plan:\n#### Monday \n- Easy Run: 10km at 06:30 min/km pace\n- Strength Training: Lower Body Workout (Squats, Lunges, Calf Raises)\n  * Warm-up: 10-15 minutes of light cardio and dynamic stretching\n  * Squats: 3 sets of 10 reps\n  * Lunges: 3 sets of 10 reps (per leg)\n  * Calf Raises: 3 sets of 15 reps\n  * Cool-down: 10-15 minutes of static stretching\n\n#### Tuesday \n- Tempo Workout: 6km at 05:30 min/km pace\n- Mobility Workout: Foam Rolling and Self-Myofascial Release (Focus on IT Band, Calves, and Quads)\n  * 10-15 minutes of foam rolling and self-myofascial release\n\n#### Wednesday \n- Hill Repeats: 8km (4km uphill at 07:00 min/km pace, 4km downhill at 05:00 min/km pace)\n- Strength Training: Core Workout (Planks, Russian Twists, Leg Raises)\n  * Warm-up: 10-15 minutes of light cardio and dynamic stretching\n  * Planks: 3 sets of 30-second hold\n  * Russian Twists: 3 sets of 15 reps\n  * Leg Raises: 3 sets of 15 reps\n  * Cool-down: 10-15 minutes of static stretching\n\n#### Thursday \n- Easy Run: 10km at 06:30 min/km pace\n- Mobility Workout: Yoga or Active Recovery (Focus on Hip Flexors, Hamstrings, and Lower Back)\n  * 30-45 minutes of yoga or active recovery\n\n#### Friday \n- Long Run: 25km at 06:15 min/km pace\n- Strength Training: Upper Body Workout (Push-ups, Pull-ups, Dumbbell Rows)\n  * Warm-up: 10-15 minutes of light cardio and dynamic stretching\n  * Push-ups: 3 sets of 10 reps\n  * Pull-ups: 3 sets of as many reps as possible\n  * Dumbbell Rows: 3 sets of 10 reps (per arm)\n  * Cool-down: 10-15 minutes of static stretching\n\n#### Saturday \n- Rest Day or Active Recovery (30-45 minutes of easy cycling, swimming, or walking)\n\n#### Sunday \n- Rest Day or Active Recovery (30-45 minutes of easy cycling, swimming, or walking)\n\n### Notes:\n* Make sure to warm up and cool down properly before and after each workout\n* Incorporate proper nutrition and hydration to support training and recovery\n* Listen to your body and adjust the plan as needed to avoid injury or burnout\n* Get at least 7-9 hours of sleep each night to aid in recovery and adaptation\n* Incorporate visualization techniques and positive self-talk to enhance mental preparation and resilience\n* Review and adjust the plan with your coach or trainer on a regular basis to ensure progress towards your goal."

