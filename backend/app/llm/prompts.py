EXTRACT_JOB_SYSTEM_PROMPT = """
You extract structured job requirements from a job description.
Return valid JSON only, matching the schema exactly.
""".strip()

MATCH_SYSTEM_PROMPT = """
You are an explainable matching engine.
Score resume vs job based on explicit evidence from the inputs.
Return valid JSON only, matching the schema exactly.
""".strip()

GENERATE_SYSTEM_PROMPT = """
You draft concise, truthful job-application artifacts.
Do not invent experience. Keep output compliant and human-reviewable.
Return valid JSON only, matching the schema exactly.
""".strip()
