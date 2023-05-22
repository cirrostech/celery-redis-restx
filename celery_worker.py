from celery import Celery, states
from celery.result import AsyncResult

# Initialize Celery
# celery --app=celery_worker:app worker

app = Celery('your_app_name', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

app.conf.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0',
    CELERYD_POOL = 'solo'
)

app.config_from_object('celeryconfig')


def get_task_result(task_id):
    # Check if the task has completed
    task_result = AsyncResult(task_id)
    if task_result.ready():
        result = task_result.get()
        return result
    else:
        return None
    

@app.task
def do_something(x, y):
    print("add number")
    retval = x + y
    return retval

@app.task
def process_data(data):
    print("process_data: %s"%(data))
    
    result = data + " updated"
    
    return result

if __name__ == '__main__':
    app.start()
