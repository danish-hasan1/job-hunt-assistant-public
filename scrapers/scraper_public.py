import requests
import time
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def search_jobs_serpapi(role, location, track, serpapi_key, max_results=20):
    if not serpapi_key or serpapi_key == "test_mode":
        return get_test_jobs()

    jobs = []
    # Build queries that emphasise the target location and nearby roles
    base = f"{role} {location}".strip()
    queries = [base, f"senior {role} {location}".strip(), f"{role} near {location}".strip()]

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
                jobs.append(
                    {
                        "id": len(jobs) + 1,
                        "title": title,
                        "company": job.get("company_name", "Unknown"),
                        "location": job.get("location", ""),
                        "track": track,
                        "score": 0,
                        "status": "new",
                        "url": job.get("share_link", ""),
                        "description": desc[:2000],
                        "source": f"Google via {job.get('via', '')}",
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


def score_jobs_with_groq(jobs, profile, groq_key):
    if not groq_key or groq_key == "test_mode":
        for job in jobs:
            job["score"] = 75
            job["score_reason"] = "Test mode score"
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
