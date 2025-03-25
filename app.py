from flask import Flask, request, redirect, session, render_template
from spotify_auth import get_auth_url, get_token_with_auth_code, refresh_access_token
from spotify_api import get_user_profile, get_user_top_tracks, get_user_top_artists
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    auth_url = get_auth_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    error = request.args.get('error')
    if error:
        return f"Error: {error}"
    
    code = request.args.get('code')
    token_info = get_token_with_auth_code(code)
    
    # Store tokens in session
    session['access_token'] = token_info.get('access_token')
    session['refresh_token'] = token_info.get('refresh_token')  # Use .get() method
    session['expires_in'] = token_info.get('expires_in')
    
    if not session['refresh_token']:
        app.logger.warning("No refresh token received from Spotify API")
    
    return redirect('/profile')


@app.route('/profile')
def profile():
    if 'access_token' not in session:
        return redirect('/login')
    
    try:
        user_info = get_user_profile(session['access_token'])
        return render_template('profile.html', user=user_info)
    except Exception as e:
        # Token might be expired, try refreshing
        if 'refresh_token' in session:
            try:
                new_token_info = refresh_access_token(session['refresh_token'])
                session['access_token'] = new_token_info['access_token']
                return redirect('/profile')
            except:
                return redirect('/login')
        return redirect('/login')

@app.route('/top-tracks')
def top_tracks():
    if 'access_token' not in session:
        return redirect('/login')
    
    try:
        time_range = request.args.get('time_range', 'medium_term')
        tracks_data = get_user_top_tracks(session['access_token'], time_range=time_range)
        return render_template('top_tracks.html', tracks=tracks_data['items'], time_range=time_range)
    except Exception as e:
        # Token might be expired, try refreshing
        if 'refresh_token' in session:
            try:
                new_token_info = refresh_access_token(session['refresh_token'])
                session['access_token'] = new_token_info['access_token']
                return redirect('/top-tracks')
            except:
                return redirect('/login')
        return redirect('/login')

@app.route('/top-artists')
def top_artists():
    if 'access_token' not in session:
        return redirect('/login')
    
    try:
        time_range = request.args.get('time_range', 'medium_term')
        artists_data = get_user_top_artists(session['access_token'], time_range=time_range)
        return render_template('top_artists.html', artists=artists_data['items'], time_range=time_range)
    except Exception as e:
        # Token might be expired, try refreshing
        if 'refresh_token' in session:
            try:
                new_token_info = refresh_access_token(session['refresh_token'])
                session['access_token'] = new_token_info['access_token']
                return redirect('/top-artists')
            except:
                return redirect('/login')
        return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True, port=8888)
