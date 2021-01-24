from flask import Flask, request
from flask_restplus import Resource, Api,fields
from flask_mysqldb import MySQL
import datetime


class TodoDAO(object):
    def __init__(self):
        self.counter = 0
        self.todos = []

    def get(self, id):
        cur = mysql.connection.cursor()
        cur.execute("select * from task where id = %d",[id])
        rv = cur.fetchall()
        cur.close()
        return parsing(rv)
        #api.abort(404, "Todo {} doesn't exist".format(id))

    def create(self, data):
        todo = data
        todo['id'] = self.counter = self.counter + 1
        cur = mysql.connection.cursor()
        cur.execute("INSERT into task(id, task, Due_by, Status) values(%d, %s, %s, %s)",[todo['id'],todo['task'],todo['due_by'],todo['Status']])
        mysql.connection.commit()
        cur.close()
        return 'Inserted successfully !'

    def update(self, id, data):
        cur = mysql.connection.cursor()
        #print(data)
        cur.execute("Update task set Status = %s where id=%d ",[data['status'],data['id']])
        mysql.connection.commit()
        cur.close()
        return 'Updated successfully !'

    def delete(self, id):
        cur = mysql.connection.cursor()
        cur.execute("Delete from task where id=%d ",[data['id']])
        mysql.connection.commit()
        cur.close()

DAO = TodoDAO()
#DAO.create({'task': 'Build an API','due_by':'2020-01-22','Status':'Finished'})




x = datetime.datetime.now()

app = Flask(__name__)
api = Api(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'flaskapp'

formt = api.model('Todo', {
    'due_date': fields.DateTime(required=True, description='The due_date\'s status to be updated'),
    'status': fields.String(required=True, description='The Status')
})

mysql = MySQL(app)

@api.route('/due')
class Task(Resource):
    
    def get(self):
        date =  request.args.get('due_date')
        #print(eval(date))
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from task where Due_by = %s",[date])
        rv = cur.fetchall()
        parse = []
        d = {}
        print(rv)
        for date, status in rv:
            d['date'] = str(date)
            d['status'] = status
            parse.append(d)
        cur.close()
        return parse
    
    def post (self):
        cur = mysql.connection.cursor()
        cur.execute("INSERT into task(Due_by,Status) values(%s,%s)",(str(x.date()),'Finished'))
        mysql.connection.commit()
        cur.close()
        return 'Inserted successfully !'

@api.route('/status_change')
class Status(Resource):

    @api.expect(formt)
    def post (self):
        cur = mysql.connection.cursor()
        data = api.payload
        print(data)
        cur.execute("Update task set Status = %s where Due_by=%s ",[data['status'],data['due_date']])
        mysql.connection.commit()
        cur.close()
        return 'Inserted successfully !'
    
@api.route('/overdue')
class Overdue(Resource):
    def get(self):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from task where Due_by < %s and Status <> 'Finished' ",[str(x.date())])
        rv = cur.fetchall()
        parse = []
        d = {}
        for date, status in rv:
            d['date'] = str(date)
            d['status'] = status
            parse.append(d)
        cur.close()
        return parse


@api.route('/finished')
class Finished(Resource):
    def get(self):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from task where Status = 'Finished'")
        rv = cur.fetchall()
        parse = []
        d = {}
        for date, status in rv:
            d['date'] = str(date)
            d['status'] = status
            parse.append(d)
        cur.close()
        return parse

    
if __name__ =='__main__':
    app.run(debug =True)
