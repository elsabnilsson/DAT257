import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase with credentials
cred = credentials.Certificate("snackrobat-128e7-firebase-adminsdk-fbsvc-3c0fe10982.json")
firebase_admin.initialize_app(cred)

# Get the Firestore client
db = firestore.client()

