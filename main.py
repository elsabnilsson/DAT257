from activitylevel import InactiveNutrition, ModerateNutrition, ActiveNutrition
from person import Person
from rec_water import calc_water_intake
from flask import Flask, render_template, request, redirect, session, url_for
from recipes_api import get_recipes
import os
from flask import redirect, url_for
from firebase_admin import auth
from firebase_config import db
from datetime import datetime, date
import math
from google.cloud.firestore_v1 import ArrayUnion
from google.cloud import firestore
import requests
from flask import Flask, request, session, redirect, url_for, render_template
from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from firebase_admin.auth import EmailAlreadyExistsError
from flask import make_response, jsonify

FIREBASE_API_KEY = "AIzaSyCrlsFF_qHY40TczFJ6jmZEmcKcHY__fmg"
from body_age import BodyAge
from workouts import search_exercises_by_body_part, filter_exercises
from recipes_api import get_recipes, get_recipe_information




app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")


def nocache(view):
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "-1"
        return response
    no_cache.__name__ = view.__name__
    return no_cache

@app.route("/register", methods=["GET", "POST"])
def register():
   
    dob = height = weight = activity = gender = goal_weight = ""


    if request.method == "POST":
        dob_input = request.form.get("dob", "")
        height_input = request.form.get("height", "")
        weight_input = request.form.get("weight", "")
        activity = request.form.get("activity", "active")
        gender = request.form.get("gender", "other")
        goal_weight_input = request.form.get("goal_weight", "")
        

        try:
            dob = datetime.strptime(dob_input, "%Y-%m-%d").date()
            height = float(height_input) / 100
            weight = float(weight_input)
            
            goal_weight = float(goal_weight_input) if goal_weight_input else None

            # Store these values temporarily in session
            session["dob"] = dob.isoformat()
            session["height"] = height
            session["weight"] = weight
            session["activity"] = activity
            session["gender"] = gender
            session["goal_weight"] = goal_weight

            # Proceed to password creation page
            return redirect(url_for("set_password"))
            
        except ValueError:
            return "Invalid input. Please enter valid numbers."
    
    dob_str = session.get("dob")
    is_birthday = False
    if dob_str:
        dob = datetime.fromisoformat(dob_str).date()
        is_birthday = is_user_birthday(dob)

    return render_template("register.html", current_route=request.endpoint, dob=dob, height=height, weight=weight, activity=activity, gender=gender, goal_weight=goal_weight, is_birthday=is_birthday)

@app.route("/set_password", methods=["GET", "POST"])
def set_password():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Retrieve profile info from session
        dob = datetime.fromisoformat(session.get("dob"))
        height = session.get("height")
        weight = session.get("weight")
        activity = session.get("activity")
        gender = session.get("gender")
        goal_weight = session.get("goal_weight")

        try:
            # Create user in Firebase Authentication
            user = auth.create_user(email=email, password=password)

            # Save complete user profile in Firestore
            user_ref = db.collection("users").document(user.uid)
            user_ref.set({
                "email": email,
                "dob": dob.isoformat(),
                "height": height,
                "weight": weight,
                "activity": activity,
                "gender": gender,
                "goal_weight": goal_weight,
            })

            session["user_uid"] = user.uid  # <- This line makes them "logged in"

            return redirect(url_for("profile"))

        except EmailAlreadyExistsError:
            error = "A user with this email already exists."
        except requests.exceptions.RequestException as e:
            # Handle other request exceptions
            error = f"An error occurred: {str(e)}"

    dob_str = session.get("dob")
    is_birthday = False
    if dob_str:
        dob = datetime.fromisoformat(dob_str).date()
        is_birthday = is_user_birthday(dob)

    return render_template("set_password.html", error=error, current_route=request.endpoint, is_birthday=is_birthday)

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
            session["user_email"] = email  
            
            # Fetch user data from Firestore
            user_ref = db.collection("users").document(data["localId"])
            user_data = user_ref.get()
            
            if user_data.exists:
                user_info = user_data.to_dict()
                dob = datetime.fromisoformat(user_info["dob"])

                # Set session variables for the stats page
                session["dob"] = user_info["dob"]
                session["height"] = user_info["height"]
                session["weight"] = user_info["weight"]
                session["activity"] = user_info["activity"]
                session["gender"] = user_info["gender"]
                session["goal_weight"] = user_info["goal_weight"]

                weight_log = user_info.get("weight_log", [])
                weight_log = sorted(weight_log, key=lambda x: x["timestamp"])
    
                dob = datetime.fromisoformat(session["dob"])
                person = Person(dob, session["height"], session["weight"], session["gender"], session["goal_weight"])

                bmi = person.calculate_bmi()
                body_age = BodyAge().calculate(person)

                # Nutrition strategy
                strategy_map = {
                    "inactive": InactiveNutrition(),
                    "moderate": ModerateNutrition(),
                    "active": ActiveNutrition()
                }
                strategy = strategy_map.get(user_info["activity"], ActiveNutrition())
                calories, protein, fat, carbs = strategy.calculate_macros(person)

                # Update session with all calculated data
                session["bmi"] = bmi
                session["rec_calories"] = calories
                session["rec_protein"] = protein
                session["rec_fat"] = fat
                session["rec_carbs"] = carbs
                session["body_age"] = body_age
                session["water_intake"] = calc_water_intake(person, user_info["activity"])
                session["meal_plan"] = strategy.meal_spli(calories, protein, fat, carbs)
                session["weight_log"] = weight_log

            return redirect(url_for("stats"))

        except requests.exceptions.RequestException:
            error = "Wrong email or password."

    dob_str = session.get("dob")
    is_birthday = False
    if dob_str:
        dob = datetime.fromisoformat(dob_str).date()
        is_birthday = is_user_birthday(dob)

    return render_template("login.html", error=error, current_route=request.endpoint, is_birthday=is_birthday)



@app.route("/profile", methods=["GET", "POST"])
@nocache
def profile():
    user_uid = session.get("user_uid")
    if not user_uid:
        return redirect(url_for("login"))

    user_ref = db.collection("users").document(user_uid)

    if request.method == "POST":
        try:
            # Fetch updated values from form
            dob_input = request.form.get("dob", "")
            weight = float(request.form.get("weight", ""))
            activity = request.form.get("activity", "active")
            dob = datetime.strptime(dob_input, "%Y-%m-%d").date()
            height = float(request.form.get("height", "")) / 100
            gender = request.form.get("gender", "other")
            goal_weight = float(request.form.get("goal_weight", "")) if request.form.get("goal_weight") else None

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
                "dob": dob.isoformat(),
                "height": height,
                "gender": gender,
                "weight": weight,
                "activity": activity,
                "weight_log": updated_log,
                "goal_weight": goal_weight
            })


        except ValueError:
            return "Invalid input. Please enter valid numbers."

        return redirect(url_for("stats"))

    user_data = user_ref.get()
    if not user_data.exists:
        return "User profile not found", 404

    user_info = user_data.to_dict()
    dob = datetime.fromisoformat(user_info["dob"]).date()
    height = user_info["height"]
    weight = user_info["weight"]
    activity = user_info["activity"]
    gender = user_info["gender"]
    goal_weight = user_info["goal_weight"]

    dob_str = session.get("dob")
    is_birthday = False
    if dob_str:
        dob = datetime.fromisoformat(dob_str).date()
        is_birthday = is_user_birthday(dob)

    return render_template(
        "index.html",
        dob = dob.isoformat(),
        height=height * 100,
        weight=weight,
        activity=activity,
        gender=gender,
        goal_weight=goal_weight,
        is_birthday=is_birthday
    )

@app.route("/stats", methods=["GET", "POST"])
@nocache
def stats():
    user_uid = session.get("user_uid")
    if not user_uid:
        return redirect(url_for("login"))
    
    user_ref = db.collection("users").document(user_uid)
    
    user_data = user_ref.get()
    if not user_data.exists:
        return "User profile not found", 404

    user_info = user_data.to_dict()
    height = user_info["height"]
    weight = user_info["weight"]
    activity = user_info["activity"]
    gender = user_info["gender"]
    goal_weight = user_info["goal_weight"]
    
        
    # Now calculate the BMI, body age, etc.
    
    dob = datetime.fromisoformat(user_info["dob"]).date()
    person = Person(dob, height, weight, gender, goal_weight)

    bmi = person.calculate_bmi()
    body_age = BodyAge().calculate(person)

    strategy_map = {
        "inactive": InactiveNutrition(),
        "moderate": ModerateNutrition(),
        "active": ActiveNutrition()
    }

    strategy = strategy_map.get(activity, ActiveNutrition())
    calories, protein, fat, carbs = strategy.calculate_macros(person)
    water_intake = calc_water_intake(person, activity)
    meal_plan = strategy.meal_spli(calories, protein, fat, carbs)
    
    water_log = user_info.get("water_log", [])
    
    latest_water_log = {}
    for entry in water_log:
        date_str = entry["date"]
        if date_str not in latest_water_log or entry["glasses"] > latest_water_log[date_str]["glasses"]:
            latest_water_log[date_str] = entry

    water_log_sorted = sorted(latest_water_log.values(), key=lambda x: x["date"])
    session["water_log"] = water_log_sorted
    
    current_date = date.today().strftime("%Y-%m-%d")
    if 'water_glasses' not in session or session.get("water_date") != current_date:
        session["water_glasses"] = 0
        session["water_date"] = current_date

    if request.args.get('click_glass'):
        if session["water_date"] != current_date:
            session["water_glasses"] = 0
            session["water_date"] = current_date

        session["water_glasses"] += 1

        user_ref.update({
            "water_log": ArrayUnion([{
                "date": current_date,
                "glasses": session["water_glasses"]
            }])
        })

# Update session with recalculated values
    session["bmi"] = bmi
    session["rec_calories"] = calories
    session["rec_protein"] = protein
    session["rec_fat"] = fat
    session["rec_carbs"] = carbs
    session["water_intake"] = water_intake
    session["meal_plan"] = meal_plan
    session["body_age"] = body_age
    
    # Fetch weight log from the database for historical data
    weight_log = user_info.get("weight_log", [])
    weight_log = sorted(weight_log, key=lambda x: x["timestamp"])


    return render_template(
        "stats.html",
        bmi=bmi,
        calories=calories,
        protein=protein,
        fat=fat,
        carbs=carbs,
        water_intake=water_intake,
        meal_plan=meal_plan,
        body_age=body_age,
        weight_log=weight_log,
        water_glasses=session.get("water_glasses", 0),
        water_log=water_log_sorted,
        goal_weight=goal_weight,
        weight=weight,
    )

def is_user_birthday(dob):
    today = date.today()
    return dob.month == today.month and dob.day == today.day


@app.route("/remove_water_glass", methods=["POST"])
def remove_water_glass():
    user_uid = session.get("user_uid")
    if not user_uid:
        return redirect(url_for("login"))
    
    user_ref = db.collection("users").document(user_uid)
    
    current_date = date.today().strftime("%Y-%m-%d")
    
    if session.get("water_date") != current_date:
        session["water_glasses"] = 0
        session["water_date"] = current_date

    if session.get("water_glasses", 0) > 0:
        session["water_glasses"] -= 1
        
        user_data = user_ref.get()
        if not user_data.exists:
            return "User profile not found", 404
            
        user_info = user_data.to_dict()
        water_log = user_info.get("water_log", [])
        
        water_log_sorted = [entry for entry in water_log if entry["date"] != current_date]
        
        updated_entry = {
            "date": current_date,
            "glasses": session["water_glasses"]
        }
        water_log_sorted.append(updated_entry)
        
        user_ref.update({
            "water_log": water_log_sorted
        })
        
    return redirect(url_for("stats"))


@app.route("/recipes")
@nocache
def recipes():
    user_uid = session.get("user_uid")
    if not user_uid:
        return redirect(url_for("login"))

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




@app.route("/workouts", methods=["GET"])
def workouts():
    body_part = request.args.get("body_part", "")
    exercises = []

    user_uid = session.get("user_uid")
    if not user_uid:
        return redirect(url_for("login"))

    user_ref = db.collection("users").document(user_uid).get()
    if not user_ref.exists:
        return "User not found", 404

    user = user_ref.to_dict()
    dob = datetime.fromisoformat(user["dob"]).date()
    person = Person(dob, user["height"], user["weight"], user["gender"], user["goal_weight"])

    # Determine goal advice
    advice = None
    if user.get("goal_weight") is not None:
        current = user["weight"]
        goal = user["goal_weight"]

        if goal < current:
            advice = "För att gå ner i vikt, överväg att öka träningsintensiteten, exempelvis med mer cardio."
        elif goal > current:
            advice = "För att öka i vikt, fokusera på tung styrketräning och tillräckligt proteinintag."
        else:
            advice = "Du har redan nått din målvikt – håll igång med balanserad träning."

    if body_part:
        try:
            raw = search_exercises_by_body_part(body_part)
            exercises = filter_exercises(raw, person, user["activity"])
        except Exception as e:
            exercises = [{"name": f"Error fetching exercises: {str(e)}"}]

    return render_template("workouts.html", exercises=exercises, body_part=body_part, advice=advice)

    



@app.route("/logout", methods=["GET", "POST"])
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


@app.route("/recipes/<int:recipe_id>")
@nocache
def recipe_detail(recipe_id):
    user_uid = session.get("user_uid")
    if not user_uid:
        return redirect(url_for("login"))

    # Fetch full recipe info
    try:
        recipe = get_recipe_information(recipe_id)
    except Exception as e:
        flash(f"Could not load recipe: {e}", "error")
        return redirect(url_for("recipes"))

    return render_template("recipe_detail.html",
                           recipe=recipe,
                           current_route=request.endpoint)



@app.route("/update_password", methods=["GET", "POST"])
@nocache
def update_password():
    error = None

    if "user_uid" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        password = request.form.get("password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not all([password, new_password, confirm_password]):
            error = "Please fill in all required fields."
        elif new_password != confirm_password:
            error = "New passwords do not match. Please try again."
        else:
            email = session.get("user_email")
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

                update_payload = {
                    "idToken": data["idToken"],
                    "password": new_password,
                    "returnSecureToken": True
                }

                update_r = requests.post(
                    f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={FIREBASE_API_KEY}",
                    json=update_payload
                )
                update_r.raise_for_status()

                return redirect(url_for("profile"))

            except requests.exceptions.RequestException:
                error = "Old password is incorrect. Please try again."

    dob_str = session.get("dob")
    is_birthday = False
    if dob_str:
        dob = datetime.fromisoformat(dob_str).date()
        is_birthday = is_user_birthday(dob)

    return render_template("update_password.html", error=error, current_route=request.endpoint, is_birthday=is_birthday)

if __name__ == "__main__":
    app.run(debug=True)
