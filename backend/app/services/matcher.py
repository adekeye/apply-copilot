from app.schemas import JobExtracted, ResumeStructured


def score_job(resume: ResumeStructured, extracted: JobExtracted) -> tuple[float, dict]:
    resume_skills = {s.lower() for s in resume.skills}
    must_have = {s.lower() for s in extracted.must_have_skills}
    nice_to_have = {s.lower() for s in extracted.nice_to_have_skills}

    must_overlap = sorted(must_have & resume_skills)
    nice_overlap = sorted(nice_to_have & resume_skills)

    must_score = (len(must_overlap) / len(must_have) * 70) if must_have else 40
    nice_score = (len(nice_overlap) / len(nice_to_have) * 15) if nice_to_have else 10

    years_bonus = min(resume.years_experience, 10) * 1.5

    location_bonus = 0
    if extracted.location != "Unknown":
        if extracted.location.lower() in {p.lower() for p in resume.location_preferences}:
            location_bonus = 10

    total = min(round(must_score + nice_score + years_bonus + location_bonus, 2), 100.0)
    explanation = {
        "must_have_matched": must_overlap,
        "nice_to_have_matched": nice_overlap,
        "years_experience": resume.years_experience,
        "location_fit": location_bonus > 0,
        "score_components": {
            "must_score": round(must_score, 2),
            "nice_score": round(nice_score, 2),
            "years_bonus": round(years_bonus, 2),
            "location_bonus": location_bonus,
        },
    }
    return total, explanation
