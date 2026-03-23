import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def extract_email_from_jd(description):
    if not description:
        return None
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(pattern, description)
    valid = [
        e
        for e in emails
        if not any(x in e.lower() for x in ["example", "noreply", "no-reply", "test@"])
    ]
    return valid[0] if valid else None


def find_company_email_groq(company_name, groq_key):
    if not groq_key or groq_key == "test_mode":
        return None
    try:
        from groq import Groq
    except Exception:
        return None
    try:
        client = Groq(api_key=groq_key)
        prompt = f"""Find the recruitment or HR email for {company_name}.
Return ONLY the email address, nothing else.
If unknown, return: unknown"""
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        result = r.choices[0].message.content.strip()
        if "@" in result and "unknown" not in result.lower():
            return result
        return None
    except Exception:
        return None


def build_subject(job, profile):
    name = profile.get("name", "")
    years = profile.get("years_experience")
    if years:
        return f"Application: {job['title']} | {name} | {years}+ years"
    return f"Application: {job['title']} | {name}"


def build_body(job, profile, cover_letter):
    highlights = []
    years = profile.get("years_experience")
    if years:
        highlights.append(f"{years}+ years of experience in relevant roles")
    key_skills = profile.get("skills") or []
    if key_skills:
        highlights.append("Key skills: " + ", ".join(key_skills[:6]))
    markets = profile.get("experience_markets") or []
    if markets:
        highlights.append("Market experience: " + ", ".join(markets))
    highlight_text = "\n".join(f"- {h}" for h in highlights) if highlights else ""
    linkedin = profile.get("linkedin")
    linkedin_line = f"\nLinkedIn: {linkedin}" if linkedin else ""
    return f"""Dear Hiring Team,

{cover_letter}

Please find attached my tailored CV and cover letter for the {job['title']} position at {job['company']}.

Key highlights:
{highlight_text}

I would welcome the opportunity to discuss how my experience fits this role.

Best regards,
{profile.get('name')}
{profile.get('phone')}
{profile.get('email')}{linkedin_line}"""


def send_application_email(
    to_email, subject, body, cv_bytes, cl_text, gmail, gmail_pass, profile
):
    try:
        msg = MIMEMultipart()
        msg["From"] = gmail
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        if cv_bytes:
            part = MIMEBase(
                "application",
                "vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            part.set_payload(cv_bytes)
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                'attachment; filename="CV.docx"',
            )
            msg.attach(part)
        if cl_text:
            cl_part = MIMEBase("text", "plain")
            cl_part.set_payload(cl_text.encode("utf-8"))
            encoders.encode_base64(cl_part)
            cl_part.add_header(
                "Content-Disposition",
                'attachment; filename="CoverLetter.txt"',
            )
            msg.attach(cl_part)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail, gmail_pass)
            server.send_message(msg)
        return True, f"Email sent to {to_email}"
    except Exception as e:
        return False, f"Email error: {str(e)}"


if __name__ == "__main__":
    print("Email public engine ready ✓")

