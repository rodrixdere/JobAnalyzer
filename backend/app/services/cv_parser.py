import json
from app.services.gemini import client


def build_cv_prompt(cv_text: str) -> str:
    return f"""
Eres un analizador experto de CVs. Extrae la información profesional del siguiente CV.

CV:
{cv_text}

Responde ÚNICAMENTE con un JSON válido con esta estructura exacta, sin texto adicional, sin markdown, sin backticks:
{{
    "skills": ["skill1", "skill2"],
    "experience": [
        {{
            "title": "título del puesto",
            "company": "nombre de la empresa",
            "years": 1.5
        }}
    ]
}}

Instrucciones:
- En skills incluye todas las habilidades relevantes para el perfil: técnicas, herramientas, metodologías, idiomas, y habilidades blandas
- En experience incluye toda experiencia laboral o profesional relevante sin importar el campo
- years es un número decimal que representa años en ese puesto, usa 0.5 si fue menos de un año
- Si no encuentras experiencia laboral devuelve una lista vacía en experience
- No asumas el campo profesional, extrae lo que está en el CV tal como está
"""


async def parse_cv(cv_text: str) -> dict:
    prompt = build_cv_prompt(cv_text)

    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    raw = response.text.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"El LLM no devolvió JSON válido: {raw}")

    if "skills" not in result or "experience" not in result:
        raise ValueError("El LLM no devolvió los campos requeridos: skills, experience")

    return result