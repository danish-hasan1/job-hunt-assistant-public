import hashlib
import json
from datetime import datetime
import base64

SUPABASE_URL = "https://ggdnrhrwgyezzccrcwyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdnZG5yaHJ3Z3llenpjY3Jjd3lxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwMDUxMDQsImV4cCI6MjA4OTU4MTEwNH0.4W6scrIGIJl56y4NN7MI2iHBx5Q-ZmlViottew91iLc"

def get_client():
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, password, profile):
    try:
        client = get_client()
        existing = client.table('users').select('email').eq('email', email).execute()
        if existing.data:
            return False, "Email already registered"
        client.table('users').insert({
            'email': email,
            'name': profile.get('name',''),
            'location': profile.get('location',''),
            'target_roles': json.dumps(profile.get('target_roles',[])),
            'target_markets': json.dumps(profile.get('target_markets',[])),
            'years_experience': int(profile.get('years_experience',0)),
            'setup_completed': True,
            'onboarding_step_reached': 4,
            'password_hash': hash_password(password),
            'created_at': datetime.now().isoformat()
        }).execute()
        return True, "Registration successful"
    except Exception as e:
        return False, str(e)

def login_user(email, password):
    try:
        client = get_client()
        result = client.table('users').select('*').eq('email', email).execute()
        if not result.data:
            return False, None, "Email not found"
        user = result.data[0]
        if user.get('password_hash') != hash_password(password):
            return False, None, "Wrong password"
        return True, user, "Login successful"
    except Exception as e:
        return False, None, str(e)

def save_user_data(email, data_type, data):
    try:
        client = get_client()
        client.table('user_data').upsert({
            'email': email,
            'data_type': data_type,
            'data': json.dumps(data),
            'updated_at': datetime.now().isoformat()
        }).execute()
        return True
    except Exception as e:
        print(f"Save error: {e}")
        return False

def load_user_data(email, data_type):
    try:
        client = get_client()
        result = (
            client.table("user_data")
            .select("data")
            .eq("email", email)
            .eq("data_type", data_type)
            .execute()
        )
        if result.data:
            return json.loads(result.data[0]["data"])
        return None
    except Exception as e:
        return None


def save_cv(email, cv_bytes):
    try:
        encoded = base64.b64encode(cv_bytes).decode("utf-8")
        save_user_data(email, "cv_bytes", encoded)
        return True
    except Exception as e:
        print(f"CV save error: {e}")
        return False


def load_cv(email):
    try:
        encoded = load_user_data(email, "cv_bytes")
        if encoded:
            return base64.b64decode(encoded.encode("utf-8"))
        return None
    except Exception as e:
        print(f"CV load error: {e}")
        return None


def save_api_keys(email, groq, serpapi, gmail, gmail_pass, gemini):
    save_user_data(
        email,
        "api_keys",
        {
            "groq": groq,
            "serpapi": serpapi,
            "gmail": gmail,
            "gmail_pass": gmail_pass,
            "gemini": gemini,
        },
    )


def load_session_data(email):
    keys = load_user_data(email, "api_keys") or {}
    jobs = load_user_data(email, "jobs") or []
    applications = load_user_data(email, "applications") or []
    cv_bytes = load_cv(email)
    return keys, jobs, applications, cv_bytes


if __name__ == "__main__":
    print("Auth engine ready ✓")
