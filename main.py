from activitylevel import InactiveNutrition, ModerateNutrition, ActiveNutrition
from person import Person
from rec_water import calc_water_intake
from flask import Flask, render_template, request, redirect, session, url_for
from recipes_api import get_recipes
import os
from flask import redirect, url_for
from firebase_admin import auth
from firebase_config import db
from datetime import datetime
from google.cloud.firestore_v1 import ArrayUnion
from google.cloud import firestore
import requests
from flask import Flask, request, session, redirect, url_for, render_template
from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from firebase_admin.auth import EmailAlreadyExistsError

FIREBASE_API_KEY = "AIzaSyCrlsFF_qHY40TczFJ6jmZEmcKcHY__fmg"

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

    return render_template("register.html", current_route=request.endpoint, age=age, height=height, weight=weight, activity=activity, gender=gender)

@app.route("/set_password", methods=["GET", "POST"])
def set_password():
    error = None
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

        except EmailAlreadyExistsError:
            error = "A user with this email already exists."
        except requests.exceptions.RequestException as e:
            # Handle other request exceptions
            error = f"An error occurred: {str(e)}"

    return render_template("set_password.html", error=error, current_route=request.endpoint)

@app.route("/", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        try:
            r = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}",
                json=payload
            )
            r.raise_for_status()
            data = r.json()
            session["user_uid"] = data["localId"]
            
            return redirect(url_for("stats"))

        except requests.exceptions.RequestException:
            error = "Wrong email or password."

    return render_template("login.html", error=error, current_route=request.endpoint)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    user_uid = session.get("user_uid")
    if not user_uid:
        return redirect(url_for("login"))

    user_ref = db.collection("users").document(user_uid)

    if request.method == "POST":
        try:
            # Fetch updated values from form
           
            weight = float(request.form.get("weight", ""))
            activity = request.form.get("activity", "active")
    
    

            # Fetch the existing weight log
            user_doc = user_ref.get()
            user_data = user_doc.to_dict()
            weight_log = user_data.get("weight_log", [])

            # Get today's date as string (YYYY-MM-DD)
            today_str = datetime.utcnow().date().isoformat()

            # Remove any existing entry for today
            updated_log = [entry for entry in weight_log if not entry["timestamp"].startswith(today_str)]

            # Add the new entry for today
            updated_log.append({
                "weight": weight,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Update Firestore with the new weight, activity, and cleaned log
            user_ref.update({
                "weight": weight,
                "activity": activity,
                "weight_log": updated_log
            })
            
        
            session["weight"] = weight
            session["activity"] = activity
            
            
        except ValueError:
            return "Invalid input. Please enter valid numbers."

        return redirect(url_for("stats"))
    
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
    
    session["bmi"] = bmi
    session["rec_fat"] = fat
    session["water_intake"] = water_intake
    session["meal_plan"] = meal_plan  
    session["weight_log"] = weight_log

    return render_template(
        "index.html",
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


@app.route("/stats")
def stats():
    return render_template(
        "stats.html",
        bmi=session.get("bmi"),
        calories=session.get("rec_calories"),
        protein=session.get("rec_protein"),
        fat=session.get("rec_fat"),
        carbs=session.get("rec_carbs"),
        water_intake=session.get("water_intake"),
        meal_plan=session.get("meal_plan"),
        weight_log=session.get("weight_log", []),
    )


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

    meal = request.args.get("meal", "Breakfast")
    meal_plan = session.get("meal_plan", {})

    if meal_plan and meal in meal_plan:
        rec = meal_plan[meal]
        rec_cal, rec_prot, rec_carb = rec["calories"], rec["protein"], rec["carbs"]
        min_cal = int(rec_cal * 0.9); max_cal = int(rec_cal * 1.1)
        min_prot = int(rec_prot * 0.1); max_prot = int(rec_prot * 7)
        min_carb = int(rec_carb * 0.1); max_carb = int(rec_carb * 7)
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
    return render_template(
        "recipes.html",
        recipes=recipes_data,
        query=query,
        meal=meal
    )

@app.route("/workouts")
def workouts():
    return render_template("workouts.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        email = request.form["email"]

        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }

        try:
            response = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}",
                json=payload
            )
            response.raise_for_status()
            flash("Password reset link sent! Please check your email.", "success")
        except requests.exceptions.RequestException:
            flash("Error sending reset link. Make sure the email is correct.", "error")

        return redirect(url_for("login"))

    return render_template("change_password.html", current_route=request.endpoint)
    


if __name__ == "__main__":
    app.run(debug=True)
