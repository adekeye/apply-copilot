from app.schemas import JobExtracted, ResumeStructured
from app.services.matcher import score_job


def test_score_job_explains_overlap():
    resume = ResumeStructured(
        raw_text="x",
        contact={},
        skills=["python", "sql", "aws"],
        years_experience=6,
        projects=[],
        employers=[],
        education=[],
        keywords=[],
        location_preferences=["Remote"],
        work_auth="Authorized",
        links=[],
    )
    extracted = JobExtracted(
        responsibilities=[],
        must_have_skills=["Python", "SQL"],
        nice_to_have_skills=["Kubernetes"],
        location="Remote",
        seniority="Senior",
        compensation=None,
    )
    score, explanation = score_job(resume, extracted)
    assert score > 70
    assert "python" in explanation["must_have_matched"]
