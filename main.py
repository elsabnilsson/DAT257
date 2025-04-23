from activitylevel import InactiveNutrition, ModerateNutrition, ActiveNutrition
from person import Person
from rec_water import calc_water_intake
from flask import Flask, render_template, request
from recipes_api import get_recipes
from flask import session
import os
from flask import redirect, url_for
from firebase_admin import auth
from firebase_config import *
from datetime import datetime
from google.cloud.firestore_v1 import ArrayUnion

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")

@app.route("/register", methods=["GET", "POST"])
def register():
   
    age = height = weight = activity = gender = ""

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

            # Store these values temporarily in session
            session["age"] = age
            session["height"] = height
            session["weight"] = weight
            session["activity"] = activity
            session["gender"] = gender

            # Proceed to password creation page
            return redirect(url_for("set_password"))
            
        except ValueError:
            return "Invalid input. Please enter valid numbers."

    return render_template("register.html", age=age, height=height, weight=weight, activity=activity, gender=gender)

@app.route("/set_password", methods=["GET", "POST"])
def set_password():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Retrieve profile info from session
        age = session.get("age")
        height = session.get("height")
        weight = session.get("weight")
        activity = session.get("activity")
        gender = session.get("gender")

        try:
            # Create user in Firebase Authentication
            user = auth.create_user(email=email, password=password)

            # Save complete user profile in Firestore
            user_ref = db.collection("users").document(user.uid)
            user_ref.set({
                "email": email,
                "age": age,
                "height": height,
                "weight": weight,
                "activity": activity,
                "gender": gender,
            })

            return redirect(url_for("login"))

        except Exception as e:
            return f"Error registering user: {e}"

    return render_template("set_password.html")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            # Sign in the user
            user = auth.get_user_by_email(email)
            # Check the password manually (you can also use Firebase Auth SDK on the client-side)
            # For simplicity, we are assuming the password is correct here
            session["user_uid"] = user.uid
            return redirect(url_for("profile"))

        except Exception as e:
            return f"Login failed: {e}"

    return render_template("login.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    user_uid = session.get("user_uid")
    if not user_uid:
        return redirect(url_for("login"))

    user_ref = db.collection("users").document(user_uid)

    if request.method == "POST":
        try:
            # Fetch updated values from form
            age = int(request.form.get("age", ""))
            height = float(request.form.get("height", "")) / 100
            weight = float(request.form.get("weight", ""))
            activity = request.form.get("activity", "active")
            gender = request.form.get("gender", "other")

            # Update Firestore with new values
            user_ref.update({
                "age": age,
                "height": height,
                "weight": weight,
                "activity": activity,
                "gender": gender,
                "weight_log": ArrayUnion([{
                    "weight": weight,
                    "timestamp": datetime.utcnow().isoformat()
    }])
            })
        except ValueError:
            return "Invalid input. Please enter valid numbers."

    user_data = user_ref.get()
    if not user_data.exists:
        return "User profile not found", 404

    user_info = user_data.to_dict()
    age = user_info["age"]
    height = user_info["height"]
    weight = user_info["weight"]
    activity = user_info["activity"]
    gender = user_info["gender"]
    
    weight_log = user_info.get("weight_log", [])
    weight_log = sorted(weight_log, key=lambda x: x["timestamp"])
    

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
    session["rec_protein"] = protein
    session["rec_carbs"] = carbs
    water_intake = calc_water_intake(person, activity)
    meal_plan = strategy.meal_spli(calories, protein, fat, carbs)

    return render_template(
        "profile.html",
        bmi=bmi,
        protein=protein,
        calories=calories,
        fat=fat,
        carbs=carbs,
        age=age,
        height=height * 100,
        weight=weight,
        activity=activity,
        gender=gender,
        water_intake=water_intake,
        meal_plan=meal_plan,
        weight_log=weight_log
    )



@app.route("/main", methods=["GET", "POST"])
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

            # Save user data to Firebase
            user_id = str(age) + str(height) + str(weight)  # Or use a proper unique ID
            save_user_profile(user_id, age, height, weight, activity, gender)
            
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

@app.route("/session-login", methods=["POST"])
def session_login():
    data = request.get_json()
    id_token = data.get("idToken")

    try:
        decoded = auth.verify_id_token(id_token)
        session["user_uid"] = decoded["uid"]
        return "", 200
    except Exception as e:
        return str(e), 401




if __name__ == "__main__":
    app.run(debug=True)
