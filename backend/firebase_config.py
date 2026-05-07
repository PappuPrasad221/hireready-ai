import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
from dotenv import load_dotenv

load_dotenv()

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        if not firebase_admin._apps:
            # For development, you can use a service account key file
            # In production, use environment variables or Google Cloud credentials
            cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
            
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
            else:
                # For development without a service account file
                # You'll need to set up proper credentials in production
                print("Warning: Firebase credentials not found. Using mock mode.")
                return None
            
            firebase_admin.initialize_app(cred, {
                'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', 'hireready-ai.appspot.com')
            })
            
        return True
    except Exception as e:
        print(f"Firebase initialization error: {e}")
        return None

def get_firestore_db():
    """Get Firestore database instance"""
    try:
        return firestore.client()
    except:
        print("Firestore not available, using mock mode")
        return None

def get_storage_bucket():
    """Get Firebase Storage bucket"""
    try:
        return storage.bucket()
    except:
        print("Firebase Storage not available, using local storage")
        return None
