# 1. pip install requests  (in the terminal)
# 2. import requests
# 3. use requests.get() on: https://steamspy.com/api.php
#    with params={"request": "tag", "tag": "Roguelike"}
# 4. turn the response into Python data with .json()
# 5. print it, then figure out how to print just the first 5 game names

import requests

response = requests.get(
"https://steamspy.com/api.php",
    params={"request": "tag", "tag": "Roguelike"}
)

data = response.json()

games = list(data.values())

for game in games[:5]:
    print(game["name"], "-", game["positive"], "positive reviews")