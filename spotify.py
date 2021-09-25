import json
import requests
from secrets import SPOTIFY_OATH_TOKEN, SPOTIFY_DEVICE_ID

def make_request(url: str, data: str = ""):
    response = requests.put(
        url, 
        data,
        headers={
            "Authorization": f"Bearer {SPOTIFY_OATH_TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    )

    print(response.content)

def play_music():
    # Toggle Shuffle
    shuffle_endpoint = f"https://api.spotify.com/v1/me/player/shuffle?state=true&device_id={SPOTIFY_DEVICE_ID}"
    make_request(shuffle_endpoint)


    # Play playlist
    playback_url = f"https://api.spotify.com/v1/me/player/play?device_id={SPOTIFY_DEVICE_ID}"
    playback_data = json.dumps({
    "context_uri": "spotify:playlist:37i9dQZF1DX3Ogo9pFvBkY"
    })
    make_request(playback_url, playback_data)

if __name__ == "__main__":
    play_music()