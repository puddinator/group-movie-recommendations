import time
from flask import Flask, flash, redirect, render_template, request, jsonify, url_for
from celery import Celery

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
    
    if(number_of_accounts > 5 or len(usernames) > 5):
        return jsonify({}), 404
    print(number_of_accounts)
    print(usernames)
    task = long_task.delay(usernames)

    return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

@celery.task(bind=True)
def long_task(self, usernames):
    number_of_accounts = len(usernames)
    results = scrape_many(self, usernames, number_of_accounts)
    return {'state': 'DONE', 'status': 'Task completed!', 'result': results}

@app.route('/status/<task_id>')
def taskstatus(task_id):
    task_result = long_task.AsyncResult(task_id)
    if task_result.state == 'PENDING':
        # Task not started
        response = {
            'state': task_result.state,
            'status': 'Celery task not started...'
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
            'status': 'Something went wrong! Error:' + str(task_result.info),
        }
    return jsonify(response)