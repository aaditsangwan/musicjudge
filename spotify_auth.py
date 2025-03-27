from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = "http://localhost:8888/callback"

def get_auth_url(scope):
    auth_url = "https://accounts.spotify.com/authorize"
    auth_url += "?client_id=" + client_id
    auth_url += "&response_type=code"
    auth_url += "&redirect_uri=" + redirect_uri
    auth_url += "&scope=" + scope
    return auth_url

def get_token_with_auth_code(code):
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }
    
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    return json_result

def refresh_access_token(refresh_token):
    """Get a new access token using the refresh token"""
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    response = post(url, headers=headers, data=data)
    if response.status_code == 200:
        new_token_info = json.loads(response.content)
        return new_token_info
    else:
        raise Exception(f"Token refresh failed: {response.status_code}, {response.content}")
