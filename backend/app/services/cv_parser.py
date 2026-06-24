import json
from app.services.groq_client import client


def build_cv_prompt(cv_text: str) -> str:
    return f"""
Eres un analizador experto de CVs. Extrae la información profesional del siguiente CV.

CV:
{cv_text}

Responde ÚNICAMENTE con un JSON válido con esta estructura exacta, sin texto adicional, sin markdown, sin backticks:
{{
    "full_name": "nombre completo o null",
    "professional_title": "título profesional o null",
    "email": "email o null",
    "skills": ["skill1", "skill2"],
    "experience": [
        {{
            "title": "título del puesto",
            "company": "nombre de la empresa",
            "years": 1.5
        }}
    ],
    "projects": [
        {{
            "name": "nombre del proyecto",
            "description": "descripción breve",
            "technologies": ["tech1", "tech2"]
        }}
    ],
    "education": [
        {{
            "degree": "título o carrera",
            "institution": "institución educativa",
            "year": 2024
        }}
    ],
    "languages": ["Español", "Inglés"],
    "links": {{
        "github": "url o null",
        "linkedin": "url o null",
        "portfolio": "url o null"
    }}
}}

Instrucciones:
- Extrae toda la información que encuentres en el CV sin importar el campo profesional
- En skills incluye habilidades técnicas, herramientas, metodologías, y habilidades blandas relevantes
- En experience incluye toda experiencia laboral o profesional relevante
- years es un número decimal, usa 0.5 si fue menos de un año
- Si no encuentras un campo devuelve null para strings o lista vacía para arrays
- No inventes información que no esté en el CV
"""


async def parse_cv(cv_text: str) -> dict:
    prompt = build_cv_prompt(cv_text)

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    raw = response.choices[0].message.content.strip()
    print("RAW RESPONSE:", raw[:500])

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"El LLM no devolvió JSON válido: {raw}")

    if "skills" not in result or "experience" not in result:
        raise ValueError("El LLM no devolvió los campos requeridos: skills, experience")

    return result