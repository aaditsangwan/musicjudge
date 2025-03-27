from requests import get

def get_user_profile(access_token):
    url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = get(url, headers=headers)
    return response.json()

def get_user_top_tracks(access_token, limit=10, time_range="medium_term"):
    """Get the user's top tracks
    time_range: short_term (4 weeks), medium_term (6 months), long_term (years)
    """
    url = f"https://api.spotify.com/v1/me/top/tracks?limit={limit}&time_range={time_range}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Top tracks request failed: {response.status_code}, {response.content}")

def get_user_top_artists(access_token, limit=10, time_range="medium_term"):
    """Get the user's top artists"""
    url = f"https://api.spotify.com/v1/me/top/artists?limit={limit}&time_range={time_range}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Top artists request failed: {response.status_code}, {response.content}")
