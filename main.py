from activitylevel import InactiveNutrition, ModerateNutrition, ActiveNutrition
from person import Person
from rec_water import calc_water_intake
from flask import Flask, render_template, request
from recipes_api import get_recipes
from flask import session
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")

@app.route("/", methods=["GET", "POST"])
def index():
    age = height = weight = activity = gender = ""
    bmi = protein = calories = fat = carbs = water_intake = meal_plan = None

    if request.method == "POST":
        age_input = request.form.get("age", "")
        height_input = request.form.get("height", "")
        weight_input = request.form.get("weight", "")
        activity = request.form.get("activity", "active")
        gender = request.form.get("gender", "other")

        try:
            age = int(age_input)
            height = float(height_input) / 100
            weight = float(weight_input)

            person = Person(age, height, weight, gender)
            bmi = person.calculate_bmi()

            strategy_map = {
                "inactive": InactiveNutrition(),
                "moderate": ModerateNutrition(),
                "active": ActiveNutrition()
            }

            strategy = strategy_map.get(activity, ActiveNutrition())
            calories, protein, fat, carbs = strategy.calculate_macros(person)
            session["rec_calories"] = calories
            session["rec_protein"]  = protein
            session["rec_carbs"]    = carbs
            water_intake = calc_water_intake(person, activity)
            meal_plan = strategy.meal_spli(calories, protein, fat, carbs)

        except ValueError:
            bmi = "Invalid input. Please enter valid numbers."

    return render_template(
        "index.html",
        bmi=bmi,
        protein=protein,
        calories=calories,
        fat=fat,
        carbs=carbs,
        age=age,    
        height=height * 100 if height else "",
        weight=weight if weight else "",
        activity=activity,
        water_intake=water_intake,
        gender=gender,
        meal_plan=meal_plan 
    )

@app.route("/stats")
def stats():
    return render_template("stats.html")

@app.route("/recipes")
def recipes():

    query = request.args.get("query", "side salad")

    diet = "vegetarian" if request.args.get("vegetarian") else None


    intolerances = []
    if request.args.get("lactose"):
        intolerances.append("lactose")
    if request.args.get("gluten"):
        intolerances.append("gluten")
    if not intolerances:
        intolerances = None

    rec_cal  = session.get("rec_calories")
    rec_prot = session.get("rec_protein")
    rec_carb = session.get("rec_carbs")

    if rec_cal and rec_prot and rec_carb:
        min_cal = int(rec_cal * 0.1)
        max_cal = int(rec_cal * 7)
        min_prot = int(rec_prot * 0.1)
        max_prot = int(rec_prot * 7)
        min_carb = int(rec_carb * 0.1)
        max_carb = int(rec_carb * 7)
    else:
        min_cal = max_cal = min_prot = max_prot = min_carb = max_carb = None

    recipes_data = get_recipes(
        query=query,
        diet=diet,
        intolerances=intolerances,
        add_recipe_information=True,
        add_recipe_instructions=True,
        add_recipe_nutrition=True,
        min_calories=min_cal,
        max_calories=max_cal,
        min_protein=min_prot,
        max_protein=max_prot,
        min_carbs=min_carb,
        max_carbs=max_carb,
    )
    return render_template("recipes.html", recipes=recipes_data, query=query)

@app.route("/workouts")
def workouts():
    return render_template("workouts.html")



if __name__ == "__main__":
    app.run(debug=True)
