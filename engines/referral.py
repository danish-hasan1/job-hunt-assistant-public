import random
import string
from datetime import datetime


SUPABASE_URL = "https://ggdnrhrwgyezzccrcwyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdnZG5yaHJ3Z3llenpjY3Jjd3lxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwMDUxMDQsImV4cCI6MjA4OTU4MTEwNH0.4W6scrIGIJl56y4NN7MI2iHBx5Q-ZmlViottew91iLc"


def get_client():
    from supabase import create_client

    return create_client(SUPABASE_URL, SUPABASE_KEY)


def generate_referral_code(name):
    clean = name.upper().replace(" ", "")[:6]
    suffix = "".join(random.choices(string.digits, k=4))
    return f"{clean}{suffix}"


def get_or_create_referral_code(email, name):
    try:
        client = get_client()
        result = (
            client.table("users")
            .select("referral_code")
            .eq("email", email)
            .execute()
        )
        if result.data and result.data[0].get("referral_code"):
            return result.data[0]["referral_code"]
        code = generate_referral_code(name)
        client.table("users").update({"referral_code": code}).eq(
            "email", email
        ).execute()
        return code
    except Exception as e:
        print(f"Referral code error: {e}")
        return None


def get_referral_stats(email):
    try:
        client = get_client()
        result = (
            client.table("referrals")
            .select("*")
            .eq("referrer_email", email)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def apply_referral_code(referred_email, code):
    try:
        client = get_client()
        result = (
            client.table("users")
            .select("email,name")
            .eq("referral_code", code)
            .execute()
        )
        if not result.data:
            return False, "Invalid referral code"
        referrer = result.data[0]
        client.table("users").update(
            {"referred_by": referrer["email"]}
        ).eq("email", referred_email).execute()
        client.table("referrals").insert(
            {
                "referrer_email": referrer["email"],
                "referred_email": referred_email,
                "created_at": datetime.now().isoformat(),
            }
        ).execute()
        return True, f"Referral applied! You were referred by {referrer['name']}"
    except Exception as e:
        return False, str(e)


def get_referral_leaderboard():
    try:
        client = get_client()
        referrals = client.table("referrals").select("referrer_email").execute().data
        counts = {}
        for r in referrals:
            e = r["referrer_email"]
            counts[e] = counts.get(e, 0) + 1
        users = client.table("users").select("email,name").execute().data
        user_map = {u["email"]: u["name"] for u in users}
        leaderboard = [
            {"name": user_map.get(e, "Unknown"), "email": e, "referrals": c}
            for e, c in counts.items()
        ]
        return sorted(leaderboard, key=lambda x: x["referrals"], reverse=True)[:10]
    except Exception:
        return []


if __name__ == "__main__":
    print("Referral engine ready ✓")

