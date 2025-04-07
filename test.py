from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    age = height = weight = activity = ""
    bmi = protein = calories = fat = carbs = None

    if request.method == "POST":
        age_input = request.form.get("age", "")
        height_input = request.form.get("height", "")
        weight_input = request.form.get("weight", "")

        try:
            age = int(age_input) if age_input else ""
            height = float(height_input) / 100 if height_input else None
            weight = float(weight_input) if weight_input else None

            # Calculate BMI
            if height > 0 and weight > 0:
                bmi = round(weight / (height ** 2), 2)

        except ValueError:
            bmi = "Invalid input. Please enter valid numbers."


    #protein, fat and carbohydrates calculation
    if request.method == "POST":
        weight_input = request.form.get("weight", "")
        activity = request.form.get("activity", "active")  # default to active

        try:
            weight = float(weight_input) if weight_input else None

            if weight > 0:
            
                # Calories based on activity
                activity_factor = {"sedentary": 25, "moderate": 30, "active": 35}
                calories = round(weight * activity_factor[activity])
                
                # Protein calculation
                protein = round(weight * 1.6, 1)
                protein_kcal = protein * 4

                # Fat: 25% of calories
                fat_kcal = calories * 0.25
                fat = round(fat_kcal / 9, 1)

                # Carbs: remaining calories
                carbs_kcal = calories - protein_kcal - fat_kcal
                carbs = round(carbs_kcal / 4, 1)
        except ValueError:
            weight = "Invalid input. Please enter valid numbers."


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
