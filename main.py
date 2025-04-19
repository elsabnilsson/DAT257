from activitylevel import InactiveNutrition, ModerateNutrition, ActiveNutrition
from person import Person
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    age = height = weight = activity = gender = ""
    bmi = protein = calories = fat = carbs = meal_plan = None

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
        gender=gender,
        meal_plan=meal_plan 
    )



if __name__ == "__main__":
    app.run(debug=True)
