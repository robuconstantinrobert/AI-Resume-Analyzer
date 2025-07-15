# import os
# from celery import Celery

# broker_url = os.getenv("CELERY_BROKER_URL")
# backend_url = os.getenv("CELERY_RESULT_BACKEND", broker_url)

# celery = Celery(
#     "resume_tasks",
#     broker=broker_url,
#     backend=backend_url,
# )

# import resume_ingest