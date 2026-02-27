from app.schemas import JobExtracted, ResumeStructured
from app.services.generator import generate_answers, generate_cover_letter


def test_generate_outputs():
    resume = ResumeStructured(
        raw_text="x",
        contact={},
        skills=["python", "fastapi"],
        years_experience=5,
        projects=[],
        employers=[],
        education=[],
        keywords=[],
        location_preferences=[],
        work_auth="US Citizen",
        links=[],
    )
    extracted = JobExtracted(
        responsibilities=[],
        must_have_skills=["Python"],
        nice_to_have_skills=[],
        location="Remote",
        seniority="Staff",
        compensation=None,
    )
    cl = generate_cover_letter(resume, "Staff Engineer", "Acme", extracted)
    ans = generate_answers({"default_answers": {}}, resume, extracted)
    assert "Staff Engineer" in cl["subject"]
    assert ans["work_authorization"] == "US Citizen"
