import json
from app.services.groq_client import client


def build_analysis_prompt(profile: dict, job_text: str) -> str:
    return f"""
Eres un analizador experto de ofertas de trabajo. Analiza la compatibilidad entre el perfil del usuario y la oferta de trabajo.

PERFIL DEL USUARIO:
Skills: {", ".join(profile["skills"])}
Experiencia: {json.dumps(profile["experience"], ensure_ascii=False)}

OFERTA DE TRABAJO:
{job_text}

Responde ÚNICAMENTE con un JSON válido con esta estructura exacta, sin texto adicional, sin markdown, sin backticks:
{{
    "job_title": "título del puesto o null si no se encuentra",
    "company": "nombre de la empresa o null si no se encuentra",
    "required_skills": ["skill1", "skill2"],
    "matching_skills": ["skill1"],
    "missing_skills": ["skill2"],
    "match_score": 75,
    "summary": "resumen breve en español de máximo 2 oraciones"
}}

Criterios del match_score:
- 90-100: cumple todos los requisitos incluyendo los opcionales
- 70-89: cumple todos los requisitos principales, faltan algunos secundarios
- 40-69: cumple la mitad de los requisitos principales
- 20-39: cumple pocos requisitos principales
- 0-19: no cumple los requisitos principales
"""


async def analyze_job_offer(profile: dict, job_text: str) -> dict:
    prompt = build_analysis_prompt(profile, job_text)

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    raw = response.choices[0].message.content.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"El LLM no devolvió JSON válido: {raw}")

    required_keys = [
        "job_title", "company", "required_skills",
        "matching_skills", "missing_skills", "match_score", "summary"
    ]
    for key in required_keys:
        if key not in result:
            raise ValueError(f"El LLM no devolvió el campo requerido: {key}")

    return result