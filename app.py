from flask import Flask, flash, redirect, render_template, request, jsonify, url_for
from celery import Celery

from scraper import scrape_many

# Configure application
app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/results", methods=["GET"])
def results():
    number_of_accounts = int(request.args.get('number_of_accounts'))
    usernames = request.args.to_dict()
    if(number_of_accounts > 5 or len(usernames) > 6):
        return jsonify({}), 404
    
    for key in list(usernames.keys()):
        if usernames[key] == 'undefined' or key == 'number_of_accounts':
            usernames.pop(key)

    task = long_task.delay(usernames)

    return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

@celery.task(bind=True)
def long_task(self, usernames):
    print(usernames)
    number_of_accounts = len(usernames)
    print(number_of_accounts)
    results = scrape_many(self, usernames, number_of_accounts)
    return {'state': 'DONE', 'status': 'Task completed!', 'result': results}

@app.route('/status/<task_id>')
def taskstatus(task_id):
    task_result = long_task.AsyncResult(task_id)
    if task_result.state == 'PENDING':
        # Task not started
        response = {
            'state': task_result.state,
            'status': 'Task not started...'
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