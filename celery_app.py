from celery import Celery

celery = Celery(
    "resume_tasks",
    broker="redis://localhost:6379/0",      
    backend="redis://localhost:6379/1"       
)

import resume_ingest