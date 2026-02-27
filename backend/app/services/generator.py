from app.schemas import JobExtracted, ResumeStructured


def generate_cover_letter(resume: ResumeStructured, title: str, company: str, extracted: JobExtracted) -> dict:
    top_skills = ", ".join(resume.skills[:4]) if resume.skills else "relevant engineering skills"
    body = (
        f"Dear Hiring Team at {company},\n\n"
        f"I am applying for the {title} role. I bring {resume.years_experience}+ years of experience and strengths in {top_skills}. "
        f"My background aligns with your needs in {', '.join(extracted.must_have_skills[:3]) or 'software delivery'}.\n\n"
        "I would value the opportunity to contribute to your team and deliver measurable results.\n\n"
        "Sincerely,\nCandidate"
    )
    return {"subject": f"Application for {title}", "body": body}


def generate_answers(policy: dict, resume: ResumeStructured, extracted: JobExtracted) -> dict:
    defaults = policy.get("default_answers", {})
    return {
        "work_authorization": defaults.get("work_authorization", resume.work_auth),
        "requires_sponsorship": defaults.get("requires_sponsorship", "No"),
        "open_to_relocation": defaults.get("open_to_relocation", "No"),
        "notice_period": defaults.get("notice_period", "2 weeks"),
        "salary_expectation": defaults.get("salary_expectation", "$150,000-$190,000"),
        "why_interested": defaults.get(
            "why_interested",
            f"The role matches my experience in {', '.join(extracted.must_have_skills[:2]) or 'engineering'} and my interest in impactful products.",
        ),
    }


def generate_checklist() -> list[str]:
    return [
        "Confirm every auto-filled answer matches your current situation.",
        "Review compensation and location constraints before submission.",
        "Verify resume version and cover letter personalization.",
        "Ensure platform terms permit your current workflow.",
        "Complete final human review and click Submit manually.",
    ]
