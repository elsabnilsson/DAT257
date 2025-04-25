import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase with credentials
cred = credentials.Certificate("DAT257/DAT257/firebase-adminsdk.json")
firebase_admin.initialize_app(cred)

# Get the Firestore client
db = firestore.client()

def save_user_profile(user_id, age, height, weight, activity, gender):
    # Reference to the 'users' collection in Firestore
    user_ref = db.collection('users').document(user_id)

    # Data to store
    user_data = {
        'age': age,
        'height': height,
        'weight': weight,
        'activity': activity,
        'gender': gender,
    }

    # Set data to Firestore
    user_ref.set(user_data)
