import re

from app.schemas import JobExtracted


def extract_job_details(jd_text: str) -> JobExtracted:
    text = jd_text.strip()
    lowered = text.lower()

    bullets = [line.strip("- *\t") for line in text.splitlines() if line.strip().startswith(("-", "*"))]
    responsibilities = bullets[:8]

    skills_pattern = r"\b(python|sql|aws|docker|kubernetes|fastapi|react|typescript|javascript|postgresql|machine learning|nlp|java|go)\b"
    found_skills = sorted(set(s.title() for s in re.findall(skills_pattern, lowered)))

    must_have = found_skills[:6]
    nice_to_have = found_skills[6:10]

    seniority = "Unknown"
    for label in ["Staff", "Senior", "Lead", "Principal", "Mid", "Junior"]:
        if label.lower() in lowered:
            seniority = label
            break

    location = "Unknown"
    for loc in ["Remote", "New York", "San Francisco", "Seattle", "Austin", "United States"]:
        if loc.lower() in lowered:
            location = loc
            break

    comp_match = re.search(r"\$[\d,]+\s*(?:-|to)\s*\$[\d,]+", text)

    return JobExtracted(
        responsibilities=responsibilities,
        must_have_skills=must_have,
        nice_to_have_skills=nice_to_have,
        location=location,
        seniority=seniority,
        compensation=comp_match.group(0) if comp_match else None,
    )
