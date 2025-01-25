# from flask import Flask, redirect, request, session, url_for, jsonify
# from flask_sqlalchemy import SQLAlchemy
# import requests
# import os
# from datetime import datetime, timedelta

# app = Flask(__name__)
# app.secret_key = os.environ.get('SECRET_KEY')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///athletes.db'
# db = SQLAlchemy(app)

# # Strava Configuration
# STRAVA_CLIENT_ID = os.environ.get('STRAVA_CLIENT_ID')
# STRAVA_CLIENT_SECRET = os.environ.get('STRAVA_CLIENT_SECRET')

# class Athlete(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     athlete_id = db.Column(db.Integer, unique=True)
#     refresh_token = db.Column(db.String(200))
#     access_token = db.Column(db.String(200))
#     expires_at = db.Column(db.DateTime)

# def refresh_access_token(athlete):
#     try:
#         response = requests.post(
#             'https://www.strava.com/oauth/token',
#             data={
#                 'client_id': STRAVA_CLIENT_ID,
#                 'client_secret': STRAVA_CLIENT_SECRET,
#                 'grant_type': 'refresh_token',
#                 'refresh_token': athlete.refresh_token
#             }
#         )
#         response.raise_for_status()
#         token_data = response.json()
        
#         athlete.access_token = token_data['access_token']
#         athlete.refresh_token = token_data['refresh_token']
#         athlete.expires_at = datetime.fromtimestamp(token_data['expires_at'])
#         db.session.commit()
#         return True
#     except Exception as e:
#         print(f"Token refresh failed: {str(e)}")
#         return False

# @app.route('/strava-login')
# def strava_login():
#     # Check if user has existing session
#     if 'athlete_id' in session:
#         athlete = Athlete.query.get(session['athlete_id'])
#         if athlete and athlete.expires_at > datetime.now():
#             return redirect(url_for('dashboard'))
        
#         if athlete and refresh_access_token(athlete):
#             session['athlete_id'] = athlete.athlete_id
#             return redirect(url_for('dashboard'))
    
#     # If no valid session, proceed to normal OAuth flow
#     auth_url = (
#         f"https://www.strava.com/oauth/authorize?"
#         f"client_id={STRAVA_CLIENT_ID}&"
#         f"redirect_uri={url_for('strava_callback', _external=True)}&"
#         f"response_type=code&"
#         f"scope=activity:read_all"
#     )
#     return redirect(auth_url)

# @app.route('/strava-callback')
# def strava_callback():
#     code = request.args.get('code')
#     if not code:
#         return "Authorization failed", 400
    
#     try:
#         # Exchange code for tokens
#         response = requests.post(
#             'https://www.strava.com/oauth/token',
#             data={
#                 'client_id': STRAVA_CLIENT_ID,
#                 'client_secret': STRAVA_CLIENT_SECRET,
#                 'code': code,
#                 'grant_type': 'authorization_code'
#             }
#         )
#         response.raise_for_status()
#         token_data = response.json()
        
#         # Store or update athlete
#         athlete = Athlete.query.filter_by(athlete_id=token_data['athlete']['id']).first()
#         if not athlete:
#             athlete = Athlete(
#                 athlete_id=token_data['athlete']['id'],
#                 refresh_token=token_data['refresh_token'],
#                 access_token=token_data['access_token'],
#                 expires_at=datetime.fromtimestamp(token_data['expires_at'])
#             )
#         else:
#             athlete.refresh_token = token_data['refresh_token']
#             athlete.access_token = token_data['access_token']
#             athlete.expires_at = datetime.fromtimestamp(token_data['expires_at'])
        
#         db.session.add(athlete)
#         db.session.commit()
        
#         # Create session
#         session['athlete_id'] = athlete.athlete_id
#         return redirect(url_for('dashboard'))
    
#     except Exception as e:
#         return f"Error: {str(e)}", 500

# @app.route('/dashboard')
# def dashboard():
#     if 'athlete_id' not in session:
#         return redirect(url_for('strava_login'))
    
#     athlete = Athlete.query.get(session['athlete_id'])
#     if not athlete or athlete.expires_at < datetime.now():
#         return redirect(url_for('strava_login'))
    
#     return f"Welcome Athlete {athlete.athlete_id}!"

# @app.route('/logout')
# def logout():
#     session.pop('athlete_id', None)
#     return redirect(url_for('strava_login'))