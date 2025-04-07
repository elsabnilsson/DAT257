from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    age = height = weight = ""
    bmi = None

    if request.method == "POST":
        age = request.form.get("age", "")
        height = request.form.get("height", "")
        weight = request.form.get("weight", "")

        try:
            if age:
                age = int(age)
            if height:
                height = float(height) / 100  # Convert cm to meters
            if weight:
                weight = float(weight)

            if height > 0 and weight > 0:
                bmi = round(weight / (height ** 2), 2)
            else:
                bmi = "Height and weight must be positive numbers."
        except ValueError:
            bmi = "Invalid input. Please enter valid numbers."

    return render_template("index.html", bmi=bmi, age=age, height=height * 100 if height else "", weight=weight)

if __name__ == "__main__":
    app.run(debug=True)