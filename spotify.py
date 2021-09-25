import json
import requests
from secrets import SPOTIFY_OATH_TOKEN

def make_request(url: str, data: str = ""):
    response = requests.put(
        url, 
        data,
        headers={
            "Authorization": "Bearer {}".format(SPOTIFY_OATH_TOKEN),
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    )

    print(response)


# Toggle Shuffle
shuffle_endpoint = "https://api.spotify.com/v1/me/player/shuffle?state=true"
make_request(shuffle_endpoint)


# Play playlist
playback_url = "https://api.spotify.com/v1/me/player/play"
playback_data = json.dumps({
  "context_uri": "spotify:playlist:37i9dQZF1DX3Ogo9pFvBkY"
})
make_request(playback_url, playback_data)