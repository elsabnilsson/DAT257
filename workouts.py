# exercise_api.py
import requests

API_KEY = "8e71530107msh8e8cc0d77f91ad2p1998f4jsn584195acfd38"
API_HOST = "exercisedb.p.rapidapi.com"
BASE_URL = "https://exercisedb.p.rapidapi.com"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}

def search_exercises_by_body_part(body_part: str, limit: int = 10, offset: int = 0):
    url = f"{BASE_URL}/exercises/bodyPart/{body_part.lower()}"
    params = {"limit": str(limit), "offset": str(offset)}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def filter_exercises(exercises, person, activity):
    filtered = []

    bmi = person.calculate_bmi()

    for ex in exercises:
        name = ex['name'].lower()
        equipment = ex['equipment'].lower()

        if person.age > 50 and 'barbell' in equipment:
            continue
        if bmi >= 30 and any(k in name for k in ['jump', 'burpee']):
            continue
        if activity == "inactive" and 'advanced' in name:
            continue

        filtered.append(ex)

    return filtered

