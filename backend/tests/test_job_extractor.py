from app.services.job_extractor import extract_job_details


def test_extract_job_details():
    jd = """
    Senior Backend Engineer
    - Build APIs in Python
    - Own SQL data models
    Must have: Python, SQL, AWS
    Nice to have: Docker
    Location: Remote
    Salary: $150,000 - $190,000
    """
    result = extract_job_details(jd)
    assert "Python" in result.must_have_skills
    assert result.location == "Remote"
    assert result.compensation == "$150,000 - $190,000"
