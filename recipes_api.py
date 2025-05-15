import os
import requests

API_HOST = "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
BASE_URL = f"https://{API_HOST}/recipes/complexSearch"
API_KEY = os.getenv("SPOONACULAR_API_KEY")
if not API_KEY:
    raise RuntimeError("SPOONACULAR_API_KEY not set in env")

def get_recipes(
    query: str,
    diet: str = None,
    intolerances: list[str] = None,
    include_ingredients: list[str] = None,
    exclude_ingredients: list[str] = None,
    max_ready_time: int = 45,
    number: int = 10,
    offset: int = 0,
    add_recipe_information: bool = False,
    add_recipe_instructions: bool = False,
    add_recipe_nutrition: bool = False,
    min_carbs: int = None,
    max_carbs: int = None,
    min_protein: int = None,
    max_protein: int = None,
    min_calories: int = None,
    max_calories: int = None,
) -> dict:
    params = {
        "query": query,
        "instructionsRequired": "true",
        "fillIngredients": "false",
        "ignorePantry": "true",
        "sort": "max-used-ingredients",
        "maxReadyTime": max_ready_time,
        "offset": offset,
        "number": number,
    }
    if diet:
        params["diet"] = diet
    if intolerances:
        params["intolerances"] = ",".join(intolerances)
    if include_ingredients:
        params["includeIngredients"] = ",".join(include_ingredients)
    if exclude_ingredients:
        params["excludeIngredients"] = ",".join(exclude_ingredients)
    if add_recipe_information:
        params["addRecipeInformation"] = "true"
    if add_recipe_instructions:
        params["addRecipeInstructions"] = "true"
    if add_recipe_nutrition:
        params["addRecipeNutrition"] = "true"
    if min_carbs is not None:
        params["minCarbs"] = min_carbs
    if max_carbs is not None:
        params["maxCarbs"] = max_carbs
    if min_protein is not None:
        params["minProtein"] = min_protein
    if max_protein is not None:
        params["maxProtein"] = max_protein
    if min_calories is not None:
        params["minCalories"] = min_calories
    if max_calories is not None:
        params["maxCalories"] = max_calories

    headers = {
        "x-rapidapi-host": API_HOST,
        "x-rapidapi-key": API_KEY,
    }

    resp = requests.get(BASE_URL, headers=headers, params=params)
    if resp.status_code != 200:
        print("❌ API error", resp.status_code, resp.text)
    resp.raise_for_status()
    return resp.json()

def get_recipe_information(recipe_id: int) -> dict:
    """Fetch full recipe details (including nutrition) from Spoonacular."""
    url = f"https://{API_HOST}/recipes/{recipe_id}/information"
    headers = {
        "x-rapidapi-host": API_HOST,
        "x-rapidapi-key": API_KEY,
    }
    params = {
        "includeNutrition": "true"
    }
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()

