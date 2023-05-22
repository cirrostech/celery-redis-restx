from flask import Flask
from flask_restx import Api, Namespace, Resource, reqparse,fields
from celery import Celery, states
from celery.result import AsyncResult
from celery_worker import *
import json

# Create the Flask application
app = Flask(__name__)

# Initialize Flask-RESTX API

api = Api(app, title='Awesome API')

# ... Define your API routes and resources ...

todo_parser = reqparse.RequestParser()
todo_parser.add_argument('task', type=str, required=True, help='Task is required')

protect_data_parser = reqparse.RequestParser()
protect_data_parser.add_argument('raw_data', type=str, required=True)

request_model = api.model('Request', {
    'data': fields.String(required=True)
})

response_model = api.model('Response', {
    'message': fields.String
})

# Sample data
todos = [
    {'id': 1, 'task': 'Task 1'},
    {'id': 2, 'task': 'Task 2'},
    {'id': 3, 'task': 'Task 3'}
]

users = [
    {'id': 1, 'name': 'User 1'},
    {'id': 2, 'name': 'User 2'},
    {'id': 3, 'name': 'User 3'}
]

ns1 = Namespace('market_hub', description='Market Hub')
api.add_namespace(ns1)

# Second namespace
ns2 = Namespace('markets_spoke', description='Market Spoke')
api.add_namespace(ns2)

ns3 = Namespace('task', description='Task management')
api.add_namespace(ns3)

ns4 = Namespace('protect_data', description='Protect Data')
api.add_namespace(ns4)

@ns1.route('/todos')
class TodoList(Resource):
    def get(self):
        return todos

    def post(self):

        data = todo_parser.parse_args()
        new_todo = {'id': len(todos) + 1, 'task': data['task']}
        todos.append(new_todo)
        
        return new_todo, 201

@ns1.route('/todos/<int:todo_id>')
class TodoItem(Resource):
    def get(self, todo_id):
        todo = next((t for t in todos if t['id'] == todo_id), None)
        if todo:
            return todo
        else:
            return {'error': 'Todo not found'}, 404

    def put(self, todo_id):
        todo = next((t for t in todos if t['id'] == todo_id), None)
        if todo:
            todo['task'] = 'Updated Task'
            return todo
        else:
            return {'error': 'Todo not found'}, 404

    def delete(self, todo_id):
        todo = next((t for t in todos if t['id'] == todo_id), None)
        if todo:
            todos.remove(todo)
            return {'message': 'Todo deleted'}
        else:
            return {'error': 'Todo not found'}, 404

@ns2.route('/')
class UserList(Resource):
    def get(self):
        print("call do something")
        task = do_something.delay(1, 3)
        print(task,id)
        # Return the task ID for later retrieval
        return {'task_id': task.id, 'users': users}, 202
    

    def post(self):
        new_user = {'id': len(users) + 1, 'name': 'New User'}
        users.append(new_user)
        return new_user, 201
    

@ns3.route('/result/<string:task_id>')
class ResultResource(Resource):
    def get(self, task_id):
        # Retrieve the result of the task by task ID
        result = do_something.AsyncResult(task_id)
        
        if result.state == states.SUCCESS:
            # Task completed successfully, return the result
            return {'result': result.get()}
        elif result.state == states.PENDING or result.state == states.RECEIVED:
            # Task is still running or pending, return the task state
            return {'state': result.state}
        else:
            # Task failed or revoked, return an error message
            return {'error': 'Task failed or revoked'}, 404


@ns4.route('/')
class ProtectData(Resource):
    def get(self):
        print("call do something")
        task = do_something.delay(1, 3)
        print(task,id)
        # Return the task ID for later retrieval
        return {'task_id': task.id, 'users': users}, 202

    @api.expect(request_model)
    @api.response(200, 'Success', response_model)
    def post(self):

        payload = api.payload
        raw_data = payload['data']

        task = process_data.delay(raw_data)
        
        if task.state == states.SUCCESS:
            # Task completed successfully, return the result
            return_value =  {'result': task.get(), 'state': task.state, 'task_id': task.id }
        elif task.state == states.PENDING or task.state == states.RECEIVED:
            # Task is still running or pending, return the task state
            return_value = {'state': task.state, 'task_id': task.id}
        else:
            return_value = {'state': task.state,  'task_id': task.id}

        return {'return': return_value}, 200
    
if __name__ == '__main__':
    app.run(debug=True)



# curl -X 'POST'  'http://localhost:5000/protect_data/'  -H 'accept: application/json'   -d '{"data":"message"}'