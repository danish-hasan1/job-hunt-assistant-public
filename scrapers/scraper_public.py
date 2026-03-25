import requests
import time
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def search_jobs_serpapi(
    role, location, track, serpapi_key, max_results=20, linkedin_only=True
):
    if not serpapi_key or serpapi_key == "test_mode":
        return get_test_jobs()

    def run_search(only_linkedin):
        jobs = []
        role_parts = [r.strip() for r in str(role).split(",") if r.strip()]
        if not role_parts:
            role_parts = [str(role).strip()] if role else []
        role_parts = role_parts[:3]
        loc_parts = [l.strip() for l in str(location).split(",") if l.strip()]
        loc_parts = loc_parts[:3] if loc_parts else [""]
        queries = []
        for r in role_parts or [""]:
            for loc in loc_parts:
                base = f"{r} {loc}".strip()
                if not base:
                    continue
                queries.append(base)
                queries.append(f"senior {base}".strip())
                if loc:
                    queries.append(f"{r} near {loc}".strip())

        for query in queries:
            try:
                params = {
                    "engine": "google_jobs",
                    "q": query,
                    "api_key": serpapi_key,
                    "hl": "en",
                    "gl": "us",
                    "num": max_results,
                }
                r = requests.get("https://serpapi.com/search", params=params, timeout=15)
                data = r.json()
                results = data.get("jobs_results", [])

                for job in results:
                    title = job.get("title", "")
                    if any(
                        k in title.lower()
                        for k in [
                            "junior",
                            "intern",
                            "trainee",
                            "graduate",
                            "coordinator",
                            "sourcer",
                        ]
                    ):
                        continue
                    desc = job.get("description", "")
                    desc_lower = desc.lower()
                    sponsorship = (
                        "possible"
                        if any(k in desc_lower for k in ["visa", "sponsor", "relocat"])
                        else "unknown"
                    )
                    url = job.get("share_link", "") or job.get("link", "")
                    via = (job.get("via", "") or "").lower()
                    is_linkedin = "linkedin.com" in url.lower() or "linkedin" in via
                    if only_linkedin and not is_linkedin:
                        continue
                    source_label = "LinkedIn" if is_linkedin else f"Google via {job.get('via', '')}"
                    jobs.append(
                        {
                            "id": len(jobs) + 1,
                            "title": title,
                            "company": job.get("company_name", "Unknown"),
                            "location": job.get("location", ""),
                            "track": track,
                            "score": 0,
                            "status": "new",
                            "url": url,
                            "description": desc[:2000],
                            "source": source_label,
                            "salary": job.get("detected_extensions", {}).get(
                                "salary", "Not disclosed"
                            ),
                            "sponsorship": sponsorship,
                        }
                    )
                time.sleep(1)
            except Exception as e:
                print(f"Search error: {e}")
                continue

        seen = set()
        unique = []
        for job in jobs:
            key = f"{job['title']}_{job['company']}"
            if key not in seen:
                seen.add(key)
                unique.append(job)

        return unique[:max_results]

    jobs = run_search(linkedin_only)
    if linkedin_only and not jobs:
        jobs = run_search(False)

    try:
        extra = search_jobs_linkedin(role, location, track, max_results=max_results // 2)
        if extra:
            seen = {f"{j['title']}_{j['company']}" for j in jobs}
            for job in extra:
                key = f"{job['title']}_{job['company']}"
                if key not in seen:
                    seen.add(key)
                    jobs.append(job)
    except Exception as e:
        print(f"LinkedIn direct search error: {e}")

    return jobs


def score_jobs_with_groq(jobs, profile, groq_key):
    if not groq_key or groq_key == "test_mode":
        for job in jobs:
            job["score"] = 0
            job["score_reason"] = "Scoring disabled — add a valid Groq API key in Settings → API Keys."
        return jobs

    try:
        from groq import Groq
        import json

        client = Groq(api_key=groq_key)

        for job in jobs:
            try:
                prompt = f"""Score this job for this candidate. Return JSON only.

CANDIDATE:
- Target roles: {profile.get('target_roles',[])}
- Experience: {profile.get('years_experience',0)} years
- Current location: {profile.get('location','')}
- Target markets: {profile.get('target_markets',[])}
- Markets experience: {profile.get('experience_markets',[])}
- Relocate: {profile.get('relocate',True)}
- Min annual salary: {profile.get('min_salary','')} {profile.get('salary_currency','')}

JOB: {job['title']} at {job['company']} in {job['location']}
SALARY (if given): {job.get('salary','Not disclosed')}
DESCRIPTION: {job['description'][:500]}

Return: {{"score": 0-100, "reason": "one sentence"}}"""

                r = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                )
                text = r.choices[0].message.content.strip()
                if "```" in text:
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                result = json.loads(text.strip())
                job["score"] = result.get("score", 0)
                job["score_reason"] = result.get("reason", "")
            except Exception:
                job["score"] = 50
                job["score_reason"] = "Scoring unavailable"
    except Exception:
        for job in jobs:
            job["score"] = 50

    return sorted(jobs, key=lambda x: x["score"], reverse=True)


def get_test_jobs():
    return [
        {
            "id": 1,
            "title": "Head of Talent Acquisition",
            "company": "Cielo Talent",
            "location": "Barcelona, Spain",
            "track": "B",
            "score": 92,
            "status": "new",
            "url": "https://linkedin.com",
            "description": "Lead RPO delivery for pharma clients across Europe. 10+ years experience required.",
            "source": "Test",
            "salary": "€80,000-100,000",
            "sponsorship": "possible",
        },
        {
            "id": 2,
            "title": "RPO Delivery Manager",
            "company": "Randstad",
            "location": "Mumbai, India",
            "track": "A",
            "score": 85,
            "status": "new",
            "url": "https://linkedin.com",
            "description": "Manage European client recruitment from India delivery centre. EMEA experience essential.",
            "source": "Test",
            "salary": "25-30 LPA",
            "sponsorship": "unknown",
        },
        {
            "id": 3,
            "title": "Senior TA Manager EMEA",
            "company": "Allegis Group",
            "location": "Amsterdam, Netherlands",
            "track": "B",
            "score": 78,
            "status": "new",
            "url": "https://linkedin.com",
            "description": "Lead EMEA talent acquisition strategy for global clients.",
            "source": "Test",
            "salary": "€70,000-85,000",
            "sponsorship": "possible",
        },
        {
            "id": 4,
            "title": "Associate Director Recruitment",
            "company": "Korn Ferry",
            "location": "Bengaluru, India",
            "track": "A",
            "score": 75,
            "status": "new",
            "url": "https://linkedin.com",
            "description": "Drive European hiring programmes from India hub.",
            "source": "Test",
            "salary": "20-25 LPA",
            "sponsorship": "unknown",
        },
        {
            "id": 5,
            "title": "Global Talent Director",
            "company": "BCG",
            "location": "Madrid, Spain",
            "track": "B",
            "score": 88,
            "status": "new",
            "url": "https://linkedin.com",
            "description": "Lead global talent acquisition for BCG Europe. Relocation support available.",
            "source": "Test",
            "salary": "€90,000-120,000",
            "sponsorship": "possible",
        },
    ]


def search_jobs_linkedin(role, location, track, max_results=10):
    try:
        from playwright.sync_api import sync_playwright
        from engines.apply_agent import get_browser_with_session
    except Exception as e:
        print(f"Playwright import error: {e}")
        return []

    jobs = []
    base_query = str(role or "").strip()
    loc_query = str(location or "").strip()
    query = base_query
    if loc_query:
        query = f"{base_query} {loc_query}".strip()
    if not query:
        return []

    q = query.replace(" ", "%20")
    loc_param = loc_query.replace(" ", "%20") if loc_query else ""
    url = f"https://www.linkedin.com/jobs/search/?keywords={q}"
    if loc_param:
        url += f"&location={loc_param}"

    with sync_playwright() as p:
        browser, context, page = get_browser_with_session(p)
        try:
            page.goto(url, timeout=30000)
            time.sleep(4)
            cards = page.locator("li.jobs-search-results__list-item").all()
            for card in cards:
                if len(jobs) >= max_results:
                    break
                try:
                    title_el = card.locator("a.job-card-list__title").first
                    title = title_el.inner_text().strip()
                    if not title:
                        continue
                    company = ""
                    try:
                        company_el = card.locator(
                            "a.job-card-container__company-name"
                        ).first
                        company = company_el.inner_text().strip()
                    except Exception:
                        try:
                            company_el = card.locator(
                                "span.job-card-container__primary-description"
                            ).first
                            company = company_el.inner_text().strip()
                        except Exception:
                            company = "Unknown"
                    location_text = ""
                    try:
                        loc_el = card.locator(
                            "span.job-card-container__metadata-item"
                        ).first
                        location_text = loc_el.inner_text().strip()
                    except Exception:
                        location_text = loc_query
                    href = title_el.get_attribute("href") or ""
                    if href.startswith("/"):
                        href = "https://www.linkedin.com" + href
                    jobs.append(
                        {
                            "id": len(jobs) + 1,
                            "title": title,
                            "company": company or "Unknown",
                            "location": location_text,
                            "track": track,
                            "score": 0,
                            "status": "new",
                            "url": href,
                            "description": "",
                            "source": "LinkedIn Direct",
                            "salary": "Not disclosed",
                            "sponsorship": "unknown",
                        }
                    )
                except Exception:
                    continue
        except Exception as e:
            print(f"LinkedIn search error: {e}")
        finally:
            try:
                browser.close()
            except Exception:
                pass

    return jobs
