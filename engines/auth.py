import hashlib
import json
from datetime import datetime
import base64
import random
import string

SUPABASE_URL = "https://ggdnrhrwgyezzccrcwyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdnZG5yaHJ3Z3llenpjY3Jjd3lxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwMDUxMDQsImV4cCI6MjA4OTU4MTEwNH0.4W6scrIGIJl56y4NN7MI2iHBx5Q-ZmlViottew91iLc"


def get_client():
    from supabase import create_client

    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _is_users_permission_error(err):
    msg = str(err) or ""
    return "permission denied for table users" in msg or '"code": "42501"' in msg or "42501" in msg

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
        if _is_users_permission_error(e):
            return True, "Registration running in local mode (no cloud user storage)"
        return False, "Sign-up backend unavailable. Please try again later."

def login_user(email, password):
    try:
        client = get_client()
        result = client.table("users").select("*").eq("email", email).execute()

        err = getattr(result, "error", None)
        if err:
            msg = str(getattr(err, "message", err))
            if _is_users_permission_error(msg):
                raise Exception(msg)
            return False, None, msg

        if not result.data:
            return False, None, "Email not found"
        user = result.data[0]
        if user.get("password_hash") != hash_password(password):
            return False, None, "Wrong password"
        return True, user, "Login successful"
    except Exception as e:
        user = {
            "email": email,
            "name": email.split("@")[0],
            "location": "",
            "target_roles": "[]",
            "target_markets": "[]",
            "years_experience": 0,
        }
        return True, user, "Login in local mode (no cloud user storage)"

def save_user_data(email, data_type, data):
    payload = json.dumps(data)
    try:
        from engines.database import save_user_state

        save_user_state(email, data_type, payload)
    except Exception as e2:
        print(f"Local save error: {e2}")
    try:
        client = get_client()
        client.table('user_data').upsert({
            'email': email,
            'data_type': data_type,
            'data': payload,
            'updated_at': datetime.now().isoformat()
        }).execute()
        return True
    except Exception as e:
        print(f"Save error: {e}")
        return False

def load_user_data(email, data_type):
    try:
        from engines.database import load_user_state

        raw = load_user_state(email, data_type)
        if raw:
            return json.loads(raw)
    except Exception as e2:
        print(f"Local load error: {e2}")
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
        print(f"Cloud load error: {e}")
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


def generate_reset_code():
    return "".join(random.choices(string.digits, k=6))


def save_reset_code(email, code):
    try:
        client = get_client()
        client.table("users").update(
            {
                "reset_code": code,
                "reset_at": datetime.now().isoformat(),
            }
        ).eq("email", email).execute()
        return True
    except Exception as e:
        print(f"Reset code save error: {e}")
        return False


def verify_reset_code(email, code):
    try:
        client = get_client()
        result = (
            client.table("users")
            .select("reset_code, reset_at")
            .eq("email", email)
            .execute()
        )
        if not result.data:
            return False, "Email not found"
        user = result.data[0]
        if user.get("reset_code") != code:
            return False, "Invalid code"
        from datetime import timedelta

        reset_at = datetime.fromisoformat(user.get("reset_at", ""))
        if datetime.now() - reset_at > timedelta(minutes=15):
            return False, "Code expired — request a new one"
        return True, "Code verified"
    except Exception as e:
        if _is_users_permission_error(e):
            return False, "Password reset not available in local mode"
        return False, "Password reset temporarily unavailable"


def reset_password(email, new_password):
    try:
        client = get_client()
        client.table("users").update(
            {
                "password_hash": hash_password(new_password),
                "reset_code": None,
            }
        ).eq("email", email).execute()
        return True, "Password updated"
    except Exception as e:
        if _is_users_permission_error(e):
            return False, "Password reset not available in local mode"
        return False, "Password reset temporarily unavailable"


def send_reset_email(email, code, gmail, gmail_pass):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    try:
        msg = MIMEMultipart()
        msg["From"] = gmail
        msg["To"] = email
        msg["Subject"] = "Job Hunt Assistant — Password Reset Code"
        body = f"""Hi, 

 Your password reset code is: {code} 

 This code expires in 15 minutes. 

 If you didn't request this, ignore this email. 

 Job Hunt Assistant Team"""
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail, gmail_pass)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Reset email error: {e}")
        return False


if __name__ == "__main__":
    print("Auth engine ready ✓")
