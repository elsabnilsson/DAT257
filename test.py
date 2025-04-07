from flask import Flask, render_template, request

app = Flask(__name__)

def calculate_nutrition(age, height, weight, activity):
    
        
        bmr = 10 * weight + 6.25 * 100 * height - 5 * age + 5

        activity_factor = {
            "inactive": 1.2,
            "moderate": 1.45,
            "active": 1.7
        }
        calories = round(bmr * activity_factor[activity], 1)

        protein = round((calories * 0.30) / 4, 1)
        fat = round((calories * 0.30) / 9, 1)
        carbs = round((calories * 0.40) / 4, 1)

        return calories, protein, fat, carbs


@app.route("/", methods=["GET", "POST"])
def index():
    age = height = weight = activity = ""
    bmi = protein = calories = fat = carbs = None

    if request.method == "POST":
        age_input = request.form.get("age", "")
        height_input = request.form.get("height", "")
        weight_input = request.form.get("weight", "")
        activity = request.form.get("activity", "active")

        try:
            age = int(age_input) if age_input else ""
            height = float(height_input) / 100 if height_input else None
            weight = float(weight_input) if weight_input else None

            # Calculate BMI
            if height > 0 and weight > 0:
                bmi = round(weight / (height ** 2), 2)
                calories, protein, fat, carbs = calculate_nutrition(age, height, weight, activity)

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
        activity=activity
    )


if __name__ == "__main__":
    app.run(debug=True)
