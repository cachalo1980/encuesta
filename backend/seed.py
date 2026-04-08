"""
Seeder de Preguntas — DevMentor Survey App
==========================================
Pobla la tabla 'questions' con las preguntas reales del cuestionario.
Ejecutar UNA VEZ desde dentro del contenedor:

    docker compose exec backend python seed.py

El script es idempotente: si ya existen preguntas en la tabla, no hace nada.
"""

from database import SessionLocal
from models import Question

questions_data = [
    {
        "section": "1. Perfil General",
        "question_type": "TEXT",
        "text": "¿Qué edad tienes?",
        "is_required": True,
        "order": 1,
    },
    {
        "section": "1. Perfil General",
        "question_type": "PARAGRAPH",
        "text": "¿Cuál es tu principal motivación para aprender sobre DevOps, Seguridad y Desarrollo?",
        "is_required": True,
        "order": 2,
    },
    {
        "section": "2. Desarrollo",
        "question_type": "TEXT",
        "text": "¿Qué lenguajes de programación conoces y en qué nivel?",
        "is_required": True,
        "order": 3,
    },
    {
        "section": "2. Desarrollo",
        "question_type": "PARAGRAPH",
        "text": "¿Has usado Git? Explica con tus palabras qué problema resuelve y qué hace git clone, commit, push y branch.",
        "is_required": True,
        "order": 4,
    },
    {
        "section": "3. Linux / Sistemas",
        "question_type": "PARAGRAPH",
        "text": "¿Qué hace el comando chmod 755 archivo.sh? Explica el significado de 755.",
        "is_required": True,
        "order": 5,
    },
    {
        "section": "3. Linux / Sistemas",
        "question_type": "TEXT",
        "text": "¿Cómo verías las últimas 100 líneas de un archivo de log en tiempo real?",
        "is_required": True,
        "order": 6,
    },
    {
        "section": "4. Redes",
        "question_type": "PARAGRAPH",
        "text": "Explica la diferencia entre TCP y UDP. ¿En qué escenarios usarías cada uno?",
        "is_required": True,
        "order": 7,
    },
    {
        "section": "5. DevOps",
        "question_type": "PARAGRAPH",
        "text": "¿Qué es Docker y qué diferencia hay entre una imagen y un contenedor?",
        "is_required": True,
        "order": 8,
    },
    {
        "section": "6. Seguridad",
        "question_type": "PARAGRAPH",
        "text": "¿Qué es una inyección SQL (SQL Injection)? ¿Cómo se podría prevenir?",
        "is_required": True,
        "order": 9,
    },
    {
        "section": "7. Pensamiento Práctico",
        "question_type": "PARAGRAPH",
        "text": "Tienes una aplicación web en producción que de repente deja de responder. ¿Cuál sería tu secuencia de pasos para diagnosticar y resolver el problema?",
        "is_required": True,
        "order": 10,
    },
    {
        "section": "8. Mentalidad",
        "question_type": "PARAGRAPH",
        "text": "Cuando te enfrentas a un problema técnico difícil que no logras resolver, ¿cómo manejas la frustración? ¿Cuál es tu proceso para superarlo?",
        "is_required": True,
        "order": 11,
    },
    {
        "section": "9. Autoevaluación",
        "question_type": "LINEAR_SCALE",
        "text": "Del 1 al 10: ¿Cuál es tu nivel general en Linux/Sistemas?",
        "is_required": True,
        "order": 12,
    },
]


def seed_questions():
    db = SessionLocal()
    try:
        # Guard de idempotencia: si ya hay preguntas, no hacemos nada.
        # Así el script es seguro de ejecutar múltiples veces sin duplicar datos.
        existing = db.query(Question).count()
        if existing > 0:
            print(f"[seeder] La tabla 'questions' ya tiene {existing} registros. Nada que hacer.")
            return

        db.bulk_insert_mappings(Question, questions_data)
        db.commit()
        print(f"[seeder] {len(questions_data)} preguntas insertadas correctamente.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_questions()
