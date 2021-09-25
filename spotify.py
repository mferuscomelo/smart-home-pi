import json
import requests
from secrets import SPOTIFY_OATH_TOKEN

url = "https://api.spotify.com/v1/me/player/play"
data = json.dumps({
  "context_uri": "spotify:playlist:37i9dQZF1DX3Ogo9pFvBkY"
})

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