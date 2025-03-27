from flask import Flask, request, redirect, session, render_template
from spotify_auth import get_auth_url, get_token_with_auth_code, refresh_access_token
from spotify_api import get_user_profile, get_user_top_tracks, get_user_top_artists
import os
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Load Llama model and tokenizer
try:
    model = OllamaLLM(model="llama3")
except Exception as e:
    print(f"Error loading model: {e}")
    # Fallback message if model fails to load
    CHANDLER_FALLBACK = "Could I BE any more disappointed with your music taste? But seriously, I'm having trouble judging right now. Try again later."

def generate_chandler_response(user_music_data):
    try:
        # Create a prompt that includes Chandler's personality and the music data
        prompt = f"""
        <|begin_of_text|>
        <|user|>
        You are Chandler Bing from Friends. Judge this person's 10 most listented to tracks with your signature sarcasm and humor: {user_music_data}
        <|assistant|>
        """

        result = model.invoke(input=prompt)
        
        return result
    except Exception as e:
        print(f"Error generating response: {e}")
        return CHANDLER_FALLBACK

def format_music_for_chandler(tracks):
    formatted_data = "Top tracks:\n"
    for i, track in enumerate(tracks[:10], 1):
        artists = ", ".join([artist['name'] for artist in track['artists']])
        formatted_data += f"{i}. {track['name']} by {artists}\n"
    return formatted_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email user-top-read playlist-read-private'
    auth_url = get_auth_url(scope)
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
    
    # Only store refresh_token if it exists
    if 'refresh_token' in token_info:
        session['refresh_token'] = token_info['refresh_token']
    else:
        # Log this issue or handle it appropriately
        print("No refresh token received from Spotify API")
    
    session['expires_in'] = token_info.get('expires_in', 3600)
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

@app.route('/chandler-judgment')
def chandler_judgment():
    if 'access_token' not in session:
        return redirect('/login')
    
    try:
        # Get user's top tracks
        time_range = request.args.get('time_range', 'medium_term')
        tracks_data = get_user_top_tracks(session['access_token'], time_range=time_range)
        
        # Format music data for the model
        music_data = format_music_for_chandler(tracks_data['items'])
        
        # Generate Chandler's response
        chandler_response = generate_chandler_response(music_data)
        
        return render_template('chandler_judgment.html', 
                              tracks=tracks_data['items'], 
                              judgment=chandler_response,
                              time_range=time_range)
    except Exception as e:
        # Handle token refresh as in your other routes
        if 'refresh_token' in session:
            try:
                new_token_info = refresh_access_token(session['refresh_token'])
                session['access_token'] = new_token_info['access_token']
                return redirect('/chandler-judgment')
            except:
                return redirect('/login')
        return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True, port=8888)
