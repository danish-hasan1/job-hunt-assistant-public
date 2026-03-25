import os
import time as _time
import json as _json
from datetime import date
import sys

try:
    from playwright.sync_api import sync_playwright

    PLAYWRIGHT_AVAILABLE = True
except Exception:
    sync_playwright = None
    PLAYWRIGHT_AVAILABLE = False

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_browser_with_session(p):
    if not PLAYWRIGHT_AVAILABLE:
        raise RuntimeError("Playwright not available")
    browser = p.webkit.launch(headless=False, slow_mo=200)
    context = browser.new_context()
    try:
        cookies = _json.load(open('linkedin_cookies.json'))
        context.add_cookies(cookies)
        print(f'Loaded {len(cookies)} cookies')
    except Exception as e:
        print(f'Cookie error: {e}')
    page = context.new_page()
    return browser, context, page


def connect_linkedin_for_cookies(wait_seconds: int = 90):
    if not PLAYWRIGHT_AVAILABLE:
        return False, "Playwright is not installed. Install it to enable LinkedIn session connect."
    with sync_playwright() as p:
        browser = p.webkit.launch(headless=False, slow_mo=300)
        context = browser.new_context()
        page = context.new_page()
        try:
            page.goto("https://www.linkedin.com/login", timeout=30000)
            print(
                f"Please log in to LinkedIn in the opened window. Waiting up to {wait_seconds} seconds..."
            )
            _time.sleep(wait_seconds)
            cookies = context.cookies()
            with open("linkedin_cookies.json", "w") as f:
                _json.dump(cookies, f)
            print(f"Saved {len(cookies)} cookies to linkedin_cookies.json")
            browser.close()
            return True, "LinkedIn connected and cookies saved for automation."
        except Exception as e:
            try:
                browser.close()
            except Exception:
                pass
            return False, f"Error while connecting to LinkedIn: {str(e)}"


def find_hiring_managers(company_name, role_hint="talent acquisition", max_results=3):
    if not PLAYWRIGHT_AVAILABLE:
        return [], ["Playwright not available. Install it to enable automatic LinkedIn hiring-manager search."]
    contacts = []
    errors = []
    if not company_name:
        return contacts, errors

    base_role = (role_hint or "hiring manager").strip()
    queries = [
        f"{company_name} {base_role}",
        f"{company_name} {base_role} director manager",
        f"{company_name} head {base_role}",
    ]

    RELEVANT_TITLES = [
        "talent",
        "recruit",
        "hr",
        "human resources",
        "people",
        "hiring",
        "workforce",
        "acquisition",
        "director",
        "head",
        "manager",
        "lead",
        "vp",
        "vice president",
        "partner",
        "rpo",
    ]

    with sync_playwright() as p:
        browser, context, page = get_browser_with_session(p)
        try:
            page.goto("https://www.linkedin.com/feed/", timeout=15000)
            _time.sleep(2)
            current_url = page.url or ""
            if "login" in current_url or "authwall" in current_url:
                raise Exception("LinkedIn login required - please refresh cookies")

            for query in queries:
                if len(contacts) >= max_results:
                    break
                try:
                    url = f"https://www.linkedin.com/search/results/people/?keywords={query.replace(' ', '%20')}"
                    page.goto(url, timeout=15000)
                    _time.sleep(4)
                    links = page.locator('a[href*="/in/"]').all()
                    print(f"  Query '{query}': {len(links)} links found")
                    seen = set()
                    for link in links[:15]:
                        try:
                            href = link.get_attribute("href", timeout=2000)
                            if not href or "/in/" not in href:
                                continue
                            clean_url = href.split("?")[0]
                            if clean_url in seen:
                                continue
                            seen.add(clean_url)
                            text = link.inner_text(timeout=2000).strip()
                            lines = [
                                l.strip()
                                for l in text.split("\n")
                                if l.strip() and len(l.strip()) > 2
                            ]
                            if not lines:
                                continue
                            name = lines[0]
                            for badge in ["• 1st", "• 2nd", "• 3rd", "· 1st", "· 2nd", "· 3rd"]:
                                name = name.replace(badge, "").strip()
                            if len(name) < 3 or len(name) > 60:
                                continue
                            role = lines[1][:100] if len(lines) > 1 else ""
                            role_lower = role.lower()
                            if role and not any(k in role_lower for k in RELEVANT_TITLES):
                                continue
                            contacts.append(
                                {
                                    "contact_name": name,
                                    "contact_role": role or "Professional",
                                    "linkedin_url": clean_url,
                                    "company": company_name,
                                }
                            )
                            print(f"  + {name} | {role}")
                            if len(contacts) >= max_results:
                                break
                        except Exception:
                            continue
                except Exception as e:
                    errors.append(f"Query '{query}' failed: {str(e)}")
                    continue
        except Exception as e:
            errors.append(str(e))
            print(f"LinkedIn error: {e}")
        finally:
            _time.sleep(2)
            browser.close()

    return contacts, errors

def find_company_contact(company_name):
    if not PLAYWRIGHT_AVAILABLE:
        return []
    contacts = []
    query = f"\"{company_name}\" talent acquisition recruitment HR"
    
    with sync_playwright() as p:
        browser, context, page = get_browser_with_session(p)
        try:
            url = f"https://www.linkedin.com/search/results/people/?keywords={query.replace(' ','%20')}"
            page.goto(url, timeout=20000)
            _time.sleep(6)
            seen = set()
            links = page.locator('a[href*="/in/"]').all()
            print(f'Found {len(links)} profile links')
            for link in links[:20]:
                try:
                    href = link.get_attribute('href', timeout=2000)
                    if not href or '/in/' not in href:
                        continue
                    clean_url = href.split('?')[0]
                    if clean_url in seen:
                        continue
                    seen.add(clean_url)
                    text = link.inner_text(timeout=2000).strip()
                    lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 2]
                    if not lines:
                        continue
                    company_lower = (company_name or "").lower()
                    if not any(company_lower in l.lower() for l in lines):
                        continue
                    name = lines[0]
                    for badge in ['• 1st','• 2nd','• 3rd','· 1st','· 2nd','· 3rd']:
                        name = name.replace(badge,'').strip()
                    if len(name) < 3 or len(name) > 60:
                        continue
                    role = lines[1][:100] if len(lines) > 1 else 'Recruitment Professional'
                    contacts.append({
                        'name': name,
                        'role': role,
                        'url': clean_url,
                        'company': company_name
                    })
                    print(f'  + {name} | {role}')
                    if len(contacts) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f'Error: {e}')
        finally:
            _time.sleep(2)
            browser.close()
    return contacts

def generate_outreach_message(contact_name, company_name, job_title, profile, groq_client):
    prompt = f"""Write a personalised LinkedIn connection request from {profile.get('name')} to {contact_name} at {company_name}.
MAX 280 characters.
Goals:
- Open a warm conversation about their work and the company
- Show one specific point of alignment with this role: {job_title}
- Sound like a senior recruitment/RPO leader, not a junior recruiter

Rules:
- Do NOT mention applying for a job or phrases like "role" or "position"
- No generic phrases like "I hope you are doing well" or "I am reaching out because"
- No emojis
- Use natural, concise language that feels human
- Ask one thoughtful question about their experience, team, or culture
- Return ONLY the message text, no quotes, no explanation"""
    try:
        r = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )
        return r.choices[0].message.content.strip()[:280]
    except Exception as e:
        return f"Hi {contact_name.split()[0]}, I've been following {company_name} and would love to connect. How has your experience been there?"

def send_connection_request(profile_url, message):
    if not PLAYWRIGHT_AVAILABLE:
        return False, "Playwright not available. Open the LinkedIn profile URL in your browser and send the request manually."
    with sync_playwright() as p:
        browser, context, page = get_browser_with_session(p)
        try:
            page.goto(profile_url, timeout=15000)
            _time.sleep(3)
            for sel in ["button:has-text('Connect')", "button[aria-label*='Connect']"]:
                try:
                    btn = page.locator(sel).first
                    if btn.is_visible(timeout=3000):
                        btn.click()
                        _time.sleep(2)
                        break
                except:
                    continue
            for sel in ["button:has-text('Add a note')", "button[aria-label*='note']"]:
                try:
                    btn = page.locator(sel).first
                    if btn.is_visible(timeout=3000):
                        btn.click()
                        _time.sleep(1)
                        break
                except:
                    continue
            try:
                field = page.locator("textarea[name='message']").first
                if field.is_visible(timeout=3000):
                    field.fill(message)
                    _time.sleep(1)
            except:
                pass
            page.evaluate("document.querySelectorAll('button').forEach(b=>{if(b.textContent.includes('Send')){b.style.border='4px solid #00ff00';b.style.backgroundColor='#00aa00';b.style.color='white';b.style.fontSize='18px';}})")
            print("Click the GREEN SEND button!")
            _time.sleep(20)
            browser.close()
            return True, "Request sent"
        except Exception as e:
            browser.close()
            return False, str(e)

def save_outreach(job_id, company, name, role, url, message):
    import sqlite3
    conn = sqlite3.connect("data/jobs.db")
    conn.execute("CREATE TABLE IF NOT EXISTS outreach (id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER, company TEXT, contact_name TEXT, contact_role TEXT, contact_url TEXT, message TEXT, status TEXT DEFAULT 'sent', date_sent TEXT)")
    conn.execute("INSERT INTO outreach (job_id,company,contact_name,contact_role,contact_url,message,date_sent) VALUES (?,?,?,?,?,?,?)", (job_id,company,name,role,url,message,date.today().isoformat()))
    conn.commit()
    conn.close()


def launch_outreach_request(profile_url, message):
    import subprocess
    import json
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"url": profile_url, "message": message}, f)
        temp_path = f.name

    subprocess.Popen(
        [
            "python3",
            "-c",
            f'''
import json
from engines.outreach_agent import send_connection_request
data = json.load(open("{temp_path}"))
success, msg = send_connection_request(data["url"], data["message"])
print("Outreach result:", success, msg)
''',
        ]
    )
    return True, "LinkedIn outreach window launching..."

if __name__ == "__main__":
    print("Outreach agent ready ✓")
    contacts = find_company_contact('Randstad')
    print('Contacts:', len(contacts))
    for c in contacts:
        print(c)
