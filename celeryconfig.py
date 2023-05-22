# celeryconfig.py

# Set the pool type to "solo"
CELERYD_POOL = "solo"
CELERY_BROKER_URL='redis://localhost:6379/0'
CELERY_RESULT_BACKEND='redis://localhost:6379/0'
