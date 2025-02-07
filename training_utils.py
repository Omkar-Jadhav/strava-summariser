from datetime import datetime
import itertools
import ai
import database
import strava
import utils
import workout_classifier_testing
import markdown2

def generate_next_week_plan(dates, last_week_plan, goal_summary, past_week_activity_dtls, athlete_id):
    today = datetime.today()
    prev_start_date = datetime.strptime(dates[0].strip(), '%d/%m/%Y')
    prev_end_date = datetime.strptime(dates[1].strip(), '%d/%m/%Y')
    next_week_avail = False
    next_week_plan = last_week_plan
    if prev_start_date< today and today >= prev_end_date:
        next_week_avail = True
        last_week_acitivity = strava.get_activities_for_period(1, athlete_id, sport_type='Run')
        last_week_acitivity =list(itertools.chain(*last_week_acitivity))
        access_token = strava.get_access_token(athlete_id)
        headers = {'Authorization': f'Bearer {access_token}'} 

        past_week_activity_dtls, athlete_baseline_stats_last_week = workout_classifier_testing.get_run_type(last_week_acitivity, last_week_acitivity[0],headers)   
        past_week_activity_dtls = "\n".join([f"{i+1}. {run_type}" for i, run_type in enumerate(past_week_activity_dtls)])

        # past_week_activity_dtls = test_plan_data.past_week_activity_dtls
        
        prompt_for_next_week = utils.format_next_week_prompt_for_llm(last_week_plan, goal_summary, past_week_activity_dtls)
        
        next_week_plan_ = ai.get_response_from_groq(prompt_for_next_week)
        
        # next_week_plan = ai.get_response_from_deepseek(prompt_for_next_week)
        workout_json, dates, notes = utils.parse_workout_plan(next_week_plan_)
        
        
        next_week_plan =  markdown2.markdown(next_week_plan_)
        next_week_plan =next_week_plan.replace('\n','')
        goal_summary =  markdown2.markdown(goal_summary)
       
        database.save_workout_plan(athlete_id, workout_json, dates, notes)
        
        return next_week_avail, next_week_plan
    else:
        return next_week_avail, last_week_plan
