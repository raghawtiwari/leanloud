from flask import Flask
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix
from flask_mysqldb import MySQL
import time

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'flaskapp'

#app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='TodoMVC API',
    description='A simple TodoMVC API',
)
mysql = MySQL(app)

ns = api.namespace('todos', description='TODO operations')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'Due_by': fields.DateTime(required=True, description='The due_date\'s status to be updated'),
    'Status': fields.String(required=True, description='The Status')
})

model = api.model('Todo', {
    'id': fields.Integer(required=True, description='The task unique identifier'),
    'Status': fields.String(required=True, description='The Status')
})

def parsing(rv): # returning Into dictionary format
    parse = []
    d = {}
    for id, task, date, status in rv:
        d['id'] = id
        d['task'] = task
        d['date'] = str(date)
        d['status'] = status
        parse.append(d)
    return parse

class TodoDAO(object):
    def __init__(self):
        self.counter = 0
        self.todos = []

    def get(self, id):
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("select * from flask where id = %s",[str(id)])
            rv = cur.fetchall()
            cur.close()
        return parsing(rv)
        #api.abort(404, "Todo {} doesn't exist".format(id))

    def create(self, data):
        todo = data
        todo['id'] = self.counter = self.counter + 1
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("INSERT into flask(id, task, Due_by, Status) values(%s, %s, %s, %s)",[str(todo['id']), todo['task'], todo['Due_by'], todo['Status']])
            mysql.connection.commit()
            cur.close()
        return 'Inserted successfully !'

    def update(self, id, data):
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("Update flask set Status = %s where id=%s ",[data['Status'],str(data['id'])])
            mysql.connection.commit()
            cur.close()
        return 'Updated successfully !'

    def delete(self, id):
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("Delete from flask where id=%s ",[str(id)])
            mysql.connection.commit()
            cur.close()

DAO = TodoDAO()
DAO.create({'task': 'Build an API','Due_by':'2020-01-20','Status':'Finished'})


@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("select * from flask ")
            rv = cur.fetchall()
            cur.close()
        return parsing(rv)
        

    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        return DAO.create(api.payload), 201


@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204

    @ns.expect(model)
    #@ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)


if __name__ == '__main__':
    app.run(debug=True)
