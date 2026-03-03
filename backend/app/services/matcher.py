from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.schemas import JobExtracted, ResumeStructured


def _tfidf_similarity(text_a: str, text_b: str) -> float:
    """Compute TF-IDF cosine similarity between two documents. Returns 0.0–1.0."""
    if not text_a.strip() or not text_b.strip():
        return 0.0
    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=1000, sublinear_tf=True)
        matrix = vectorizer.fit_transform([text_a, text_b])
        return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    except Exception:
        return 0.0


def _keyword_score(resume: ResumeStructured, extracted: JobExtracted) -> tuple[float, dict]:
    """
    Keyword-based scoring:
      - Must-have skills:  70 pts max  (or 40 if none listed)
      - Nice-to-have:      15 pts max  (or 10 if none listed)
      - Years experience:  1.5 pts/yr, capped at 10 yrs → 15 pts max
      - Location match:    10 pts bonus
    """
    resume_skills = {s.lower() for s in resume.skills}
    must_have = {s.lower() for s in extracted.must_have_skills}
    nice_to_have = {s.lower() for s in extracted.nice_to_have_skills}

    must_overlap = sorted(must_have & resume_skills)
    nice_overlap = sorted(nice_to_have & resume_skills)

    must_score = (len(must_overlap) / len(must_have) * 70) if must_have else 40.0
    nice_score = (len(nice_overlap) / len(nice_to_have) * 15) if nice_to_have else 10.0
    years_bonus = min(resume.years_experience, 10) * 1.5

    location_bonus = 0.0
    if extracted.location != "Unknown":
        if extracted.location.lower() in {p.lower() for p in resume.location_preferences}:
            location_bonus = 10.0

    total = min(must_score + nice_score + years_bonus + location_bonus, 100.0)
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


def score_job(
    resume: ResumeStructured,
    extracted: JobExtracted,
    jd_text: str = "",
) -> tuple[float, dict]:
    """
    Hybrid NLP + keyword scorer.

    When `jd_text` is provided:
      final = 0.6 × keyword_score + 0.4 × (tfidf_similarity × 100)

    Without `jd_text` (backwards-compatible):
      final = keyword_score
    """
    keyword_total, explanation = _keyword_score(resume, extracted)

    nlp_similarity = 0.0
    nlp_score = 0.0

    if jd_text and resume.raw_text:
        nlp_similarity = _tfidf_similarity(resume.raw_text, jd_text)
        nlp_score = nlp_similarity * 100
        total = round(min(0.6 * keyword_total + 0.4 * nlp_score, 100.0), 2)
    else:
        total = round(keyword_total, 2)

    explanation["score_components"].update(
        {
            "nlp_similarity": round(nlp_similarity, 4),
            "nlp_score": round(nlp_score, 2),
            "keyword_score": round(keyword_total, 2),
            "final_score": total,
        }
    )
    return total, explanation
