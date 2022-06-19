import time
from flask import Flask, flash, redirect, render_template, request, jsonify, url_for
from celery import Celery
# celery worker -l info -A my_app
from scraper import scrape_many

# Configure application
app = Flask(__name__)
app.config['CELERY_broker_url'] = 'redis://localhost:6379/0'
app.config['result_backend'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_broker_url'])
celery.conf.update(app.config)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/results", methods=["POST"])
def results():
    usernames = request.form.to_dict()
    # Mutates usernames too
    number_of_accounts = int(usernames.pop("number-of-accounts"))
    # Check if fast
    if "fast?" in usernames:
        fast = True
        usernames.pop("fast?")
    else: fast = False
    usernames = list(usernames.values())
    if (number_of_accounts > 5 or len(usernames) > 5):
        return jsonify({}), 404

    task = long_task.delay(usernames, fast)

    return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

@celery.task(bind=True)
def long_task(self, usernames, fast):
    number_of_accounts = len(usernames)
    results = scrape_many(self, usernames, number_of_accounts, fast)
    if results == None and number_of_accounts == 1:
        return {'state': 'ERROR', 'status': 'Username could not be found, did you spell it correctly?'}
    elif results == None:
        return {'state': 'ERROR', 'status': 'None of the usernames could not be found, did you spell them correctly?'}
    return {'state': 'DONE', 'status': 'Task completed!', 'result': results}

@app.route('/status/<task_id>')
def taskstatus(task_id):
    task_result = long_task.AsyncResult(task_id)
    if task_result.state == 'PENDING':
        # Task not started
        response = {
            'state': task_result.state,
            'status': 'Celery task not started yet...'
        }
    elif task_result.state != 'FAILURE':
        response = {
            'state': task_result.state,
            # Updates with status
            'status': task_result.info.get('status', "A value to return if the specified key does not exist.")
        }
        if 'result' in task_result.info:
            response['result'] = task_result.info['result']
    else:
        # Something died...
        response = {
            'state': task_result.state,
            'status': 'Something went wrong! Error: ' + str(task_result.info),
        }
    return jsonify(response)


if __name__ == "__main__":
    app.run(host='0.0.0.0')