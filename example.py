import app.api.omdbapi as api
import os
import requests


# Module example
module_example = api.get_omdb_movies('Fast')
print(f"Module example:\n {module_example}")

# Command example
print("Command example:")
os.system('python -m app.api.omdbapi --title "Avengers: Endgame"')

# HTTP example
r = requests.get('https://api-test-edreams-odbm.herokuapp.com/Dragon Ball')
print(f"HTTP example:\n {r.json()}")






