"""
Seeder de Preguntas — DevMentor Survey App
==========================================
Pobla la tabla 'questions' con el cuestionario oficial completo (61 preguntas).
Ejecutar desde dentro del contenedor:

    docker compose exec backend python seed.py

El script elimina las preguntas (y respuestas asociadas) existentes antes de
reinsertar, garantizando que siempre quede el cuestionario definitivo.
"""

from database import SessionLocal
from models import Question, Response

questions_data = [
    # 1. Perfil General
    {"section": "1. Perfil General", "question_type": "TEXT", "text": "¿Qué edad tienes?", "is_required": True, "order": 1},
    {"section": "1. Perfil General", "question_type": "PARAGRAPH", "text": "¿Estudias algo relacionado a IT actualmente? Si es así, ¿qué y dónde?", "is_required": True, "order": 2},
    {"section": "1. Perfil General", "question_type": "PARAGRAPH", "text": "¿Trabajas actualmente en el área de IT o en alguna otra? ¿En qué rol o sector?", "is_required": True, "order": 3},
    {"section": "1. Perfil General", "question_type": "TEXT", "text": "¿Cuántas horas por semana, de forma realista y sostenible, puedes dedicar a aprender y practicar fuera de tus otras responsabilidades?", "is_required": True, "order": 4},
    {"section": "1. Perfil General", "question_type": "PARAGRAPH", "text": "¿Cuál es tu principal motivación para aprender sobre DevOps, Seguridad y Desarrollo?", "is_required": True, "order": 5},

    # 2. Desarrollo
    {"section": "2. Desarrollo", "question_type": "PARAGRAPH", "text": "¿Qué lenguajes de programación conoces y en qué nivel de confianza te sientes con cada uno (ej. Básico, Intermedio, Avanzado)?", "is_required": True, "order": 6},
    {"section": "2. Desarrollo", "question_type": "PARAGRAPH", "text": "Para el lenguaje en el que te sientas más cómodo, describe brevemente un proyecto (real o imaginario) que hayas construido con él.", "is_required": True, "order": 7},
    {"section": "2. Desarrollo", "question_type": "PARAGRAPH", "text": "¿Podrías describir los pasos fundamentales para crear un CRUD completo para una entidad simple? ¿Qué tecnologías usarías para el backend y el frontend?", "is_required": True, "order": 8},
    {"section": "2. Desarrollo", "question_type": "PARAGRAPH", "text": "¿Qué es una API REST? ¿Cuáles son sus principios clave (verbos HTTP, stateless, etc.)? ¿Cómo la diseñarías y consumirías?", "is_required": True, "order": 9},
    {"section": "2. Desarrollo", "question_type": "PARAGRAPH", "text": "¿Has usado Git? Explica con tus palabras qué problema resuelve Git y por qué es importante.", "is_required": True, "order": 10},
    {"section": "2. Desarrollo", "question_type": "PARAGRAPH", "text": "Describe el propósito y uso de los siguientes comandos de Git: clone, commit, push, branch, merge, pull.", "is_required": True, "order": 11},
    {"section": "2. Desarrollo", "question_type": "PARAGRAPH", "text": "Imagina que estás trabajando en una rama (feature-A) y necesitas integrar los últimos cambios de la rama principal (main). ¿Qué secuencia de comandos usarías?", "is_required": True, "order": 12},
    {"section": "2. Desarrollo", "question_type": "TEXT", "text": "¿Has subido proyectos a GitHub, GitLab o Bitbucket? Por favor, comparte el/los enlace(s) a tu(s) repositorio(s) público(s) si los tienes.", "is_required": False, "order": 13},

    # 3. Linux / Sistemas
    {"section": "3. Linux / Sistemas", "question_type": "PARAGRAPH", "text": "¿Has usado Linux? ¿Cuál(es) distribución(es) (ej. Ubuntu, Debian, CentOS)? ¿Para qué lo usaste?", "is_required": True, "order": 14},
    {"section": "3. Linux / Sistemas", "question_type": "TEXT", "text": "¿Cuál es tu editor de texto preferido en la terminal (nano, vim, emacs, etc.) y por qué?", "is_required": True, "order": 15},
    {"section": "3. Linux / Sistemas", "question_type": "PARAGRAPH", "text": "¿Qué hace el comando chmod 755 archivo.sh? Explica el significado de 755.", "is_required": True, "order": 16},
    {"section": "3. Linux / Sistemas", "question_type": "PARAGRAPH", "text": "¿Qué información te proporciona el comando ps aux?", "is_required": True, "order": 17},
    {"section": "3. Linux / Sistemas", "question_type": "TEXT", "text": "¿Cómo buscarías un archivo específico en todo el sistema de archivos si solo recuerdas parte de su nombre?", "is_required": True, "order": 18},
    {"section": "3. Linux / Sistemas", "question_type": "TEXT", "text": "¿Cómo verías las últimas 100 líneas de un archivo de log que se está actualizando constantemente en tiempo real?", "is_required": True, "order": 19},
    {"section": "3. Linux / Sistemas", "question_type": "TEXT", "text": "¿Cómo verificarías el uso de espacio en disco de cada directorio dentro de tu ubicación actual?", "is_required": True, "order": 20},
    {"section": "3. Linux / Sistemas", "question_type": "PARAGRAPH", "text": "¿Cómo iniciar, detener y reiniciar un servicio en Linux (ej. Apache, Nginx)?", "is_required": True, "order": 21},
    {"section": "3. Linux / Sistemas", "question_type": "PARAGRAPH", "text": "¿Qué son los permisos de archivos y directorios en Linux y cómo los gestionarías?", "is_required": True, "order": 22},
    {"section": "3. Linux / Sistemas", "question_type": "PARAGRAPH", "text": "¿Qué es la diferencia entre un usuario y un grupo en Linux?", "is_required": True, "order": 23},

    # 4. Redes
    {"section": "4. Redes", "question_type": "PARAGRAPH", "text": "¿Qué es una dirección IP? ¿Cuál es la diferencia entre una IP pública y una privada?", "is_required": True, "order": 24},
    {"section": "4. Redes", "question_type": "PARAGRAPH", "text": "Explica la diferencia entre TCP y UDP. ¿En qué escenarios usarías cada uno?", "is_required": True, "order": 25},
    {"section": "4. Redes", "question_type": "PARAGRAPH", "text": "¿Cuál es la diferencia principal entre HTTP y HTTPS? ¿Por qué es importante HTTPS?", "is_required": True, "order": 26},
    {"section": "4. Redes", "question_type": "PARAGRAPH", "text": "¿Qué es un puerto de red? Menciona algunos puertos comunes y los servicios asociados.", "is_required": True, "order": 27},
    {"section": "4. Redes", "question_type": "TEXT", "text": "¿Para qué se usa el comando ping?", "is_required": True, "order": 28},
    {"section": "4. Redes", "question_type": "TEXT", "text": "¿Qué información te proporciona traceroute (o tracert en Windows)?", "is_required": True, "order": 29},
    {"section": "4. Redes", "question_type": "TEXT", "text": "¿Cómo usarías netstat (o ss) para ver qué puertos están abiertos y escuchando en tu máquina?", "is_required": True, "order": 30},
    {"section": "4. Redes", "question_type": "TEXT", "text": "¿Cómo verificarías si un servidor remoto está escuchando en un puerto específico sin intentar acceder a una URL completa?", "is_required": True, "order": 31},

    # 5. DevOps
    {"section": "5. DevOps", "question_type": "PARAGRAPH", "text": "Con tus propias palabras, ¿qué entiendes por DevOps? ¿Cuáles crees que son sus pilares fundamentales?", "is_required": True, "order": 32},
    {"section": "5. DevOps", "question_type": "PARAGRAPH", "text": "¿Qué es Docker y qué problema(s) resuelve?", "is_required": True, "order": 33},
    {"section": "5. DevOps", "question_type": "PARAGRAPH", "text": "¿Cuál es la diferencia entre una imagen Docker y un contenedor Docker?", "is_required": True, "order": 34},
    {"section": "5. DevOps", "question_type": "PARAGRAPH", "text": "¿Has usado Docker? Si es así, ¿para qué? ¿Podrías describir un comando Docker básico que hayas utilizado?", "is_required": True, "order": 35},
    {"section": "5. DevOps", "question_type": "PARAGRAPH", "text": "¿Qué significan las siglas CI/CD? Explica brevemente cada parte.", "is_required": True, "order": 36},
    {"section": "5. DevOps", "question_type": "PARAGRAPH", "text": "¿Has tenido alguna experiencia con herramientas de CI/CD como GitHub Actions, GitLab CI, Jenkins, Travis CI, etc.? Si es así, ¿qué hiciste?", "is_required": True, "order": 37},
    {"section": "5. DevOps", "question_type": "PARAGRAPH", "text": "¿Has desplegado alguna aplicación web o servicio? ¿Dónde? Describe el proceso general.", "is_required": True, "order": 38},
    {"section": "5. DevOps", "question_type": "PARAGRAPH", "text": "¿Qué es la 'infraestructura como código' (IaC)? ¿Conoces alguna herramienta relacionada?", "is_required": True, "order": 39},
    {"section": "5. DevOps", "question_type": "PARAGRAPH", "text": "¿Qué importancia tiene la monitorización en un entorno DevOps? ¿Conoces alguna herramienta de monitorización?", "is_required": True, "order": 40},

    # 6. Seguridad
    {"section": "6. Seguridad", "question_type": "PARAGRAPH", "text": "Explica la diferencia entre autenticación y autorización.", "is_required": True, "order": 41},
    {"section": "6. Seguridad", "question_type": "PARAGRAPH", "text": "¿Qué es el hashing y para qué se utiliza? ¿Cuál es la diferencia con el cifrado?", "is_required": True, "order": 42},
    {"section": "6. Seguridad", "question_type": "PARAGRAPH", "text": "¿Qué es un certificado SSL/TLS y cuál es su función principal en la seguridad web?", "is_required": True, "order": 43},
    {"section": "6. Seguridad", "question_type": "PARAGRAPH", "text": "¿Qué es una inyección SQL (SQL Injection)? ¿Cómo se podría prevenir?", "is_required": True, "order": 44},
    {"section": "6. Seguridad", "question_type": "PARAGRAPH", "text": "¿Qué es un ataque de Cross-Site Scripting (XSS)? ¿Cómo se podría mitigar?", "is_required": True, "order": 45},
    {"section": "6. Seguridad", "question_type": "PARAGRAPH", "text": "¿Has oído hablar o usado herramientas como nmap o Burp Suite? ¿Para qué sirven?", "is_required": True, "order": 46},
    {"section": "6. Seguridad", "question_type": "PARAGRAPH", "text": "¿Qué medidas de seguridad básicas implementarías al desarrollar una nueva aplicación web?", "is_required": True, "order": 47},

    # 7. Pensamiento Práctico
    {"section": "7. Pensamiento Práctico", "question_type": "PARAGRAPH", "text": "Tienes una aplicación web en producción que de repente deja de responder. ¿Cuál sería tu secuencia de pasos para diagnosticar y resolver el problema?", "is_required": True, "order": 48},
    {"section": "7. Pensamiento Práctico", "question_type": "PARAGRAPH", "text": "Un usuario te reporta: 'La aplicación no funciona'. ¿Qué preguntas clave le harías para obtener más información y empezar a investigar?", "is_required": True, "order": 49},
    {"section": "7. Pensamiento Práctico", "question_type": "PARAGRAPH", "text": "Un servidor que aloja una base de datos está reportando un rendimiento muy lento. ¿Qué métricas o recursos revisarías primero para identificar la causa?", "is_required": True, "order": 50},
    {"section": "7. Pensamiento Práctico", "question_type": "PARAGRAPH", "text": "Estás a punto de desplegar una nueva versión de una aplicación crítica. ¿Qué precauciones tomarías para minimizar el riesgo de fallos y asegurar una recuperación rápida si algo sale mal?", "is_required": True, "order": 51},

    # 8. Mentalidad
    {"section": "8. Mentalidad", "question_type": "PARAGRAPH", "text": "Describe algo que hayas aprendido o construido por tu cuenta, sin que nadie te lo pidiera, simplemente por curiosidad o interés.", "is_required": True, "order": 52},
    {"section": "8. Mentalidad", "question_type": "PARAGRAPH", "text": "Cuando te enfrentas a un problema técnico difícil que no logras resolver, ¿cómo manejas la frustración? ¿Cuál es tu proceso para superarlo?", "is_required": True, "order": 53},
    {"section": "8. Mentalidad", "question_type": "TEXT", "text": "¿Qué prefieres cuando aprendes algo nuevo: que te expliquen todo detalladamente, o investigar y experimentar por tu cuenta con una guía mínima?", "is_required": True, "order": 54},
    {"section": "8. Mentalidad", "question_type": "PARAGRAPH", "text": "¿Cuál es tu objetivo principal en el área de tecnología para los próximos 6 meses? ¿Y para el próximo año?", "is_required": True, "order": 55},
    {"section": "8. Mentalidad", "question_type": "PARAGRAPH", "text": "¿Cómo te mantienes actualizado sobre las nuevas tecnologías y tendencias en el mundo del desarrollo, DevOps y la seguridad?", "is_required": True, "order": 56},

    # 9. Autoevaluación
    {"section": "9. Autoevaluación", "question_type": "LINEAR_SCALE", "text": "Del 1 al 10: ¿Cuál es tu nivel en Linux/Sistemas?", "is_required": True, "order": 57},
    {"section": "9. Autoevaluación", "question_type": "LINEAR_SCALE", "text": "Del 1 al 10: ¿Cuál es tu nivel en Programación/Desarrollo?", "is_required": True, "order": 58},
    {"section": "9. Autoevaluación", "question_type": "LINEAR_SCALE", "text": "Del 1 al 10: ¿Cuál es tu nivel en Redes?", "is_required": True, "order": 59},
    {"section": "9. Autoevaluación", "question_type": "LINEAR_SCALE", "text": "Del 1 al 10: ¿Cuál es tu nivel en Seguridad?", "is_required": True, "order": 60},
    {"section": "9. Autoevaluación", "question_type": "LINEAR_SCALE", "text": "Del 1 al 10: ¿Cuál es tu nivel en DevOps (conceptos y herramientas)?", "is_required": True, "order": 61},
]


def seed_questions():
    db = SessionLocal()
    try:
        # Eliminar respuestas primero (FK hacia questions) y luego las preguntas.
        # Esto garantiza que el cuestionario quede en su estado definitivo sin
        # violar la restricción de clave foránea responses.question_id → questions.id.
        responses_deleted = db.query(Response).delete()
        questions_deleted = db.query(Question).delete()
        db.commit()

        if questions_deleted > 0:
            print(f"[seeder] Se eliminaron {questions_deleted} preguntas y {responses_deleted} respuestas previas.")

        db.bulk_insert_mappings(Question, questions_data)
        db.commit()
        print(f"[seeder] {len(questions_data)} preguntas insertadas correctamente.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_questions()
