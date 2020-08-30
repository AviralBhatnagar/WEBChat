#importing necessary packages.
from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#Initializing Flask
app = Flask(__name__,template_folder="template")
#Configuring sqlite with flask.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/chatroom.db'
#Adding SECRET KEY for authentication session.
app.config['SECRET_KEY'] = 'Y]\x06\xdc(\xdbZA-\xd7\x84\x96C\xb6V\t\xda6\xac\xa5\xb9\\\xd8\xf5'
db = SQLAlchemy(app)

#Class for Table roomname
class Roomname(db.Model):
    sno = db.Column(db.Integer,primary_key=True,nullable=False)
    room_name = db.Column(db.String(10),nullable=False)
    date_time = db.Column(db.String(20),nullable=False)

#Class for Table messages
class Messages(db.Model):
    sno = db.Column(db.Integer,primary_key=True,nullable=False)
    room_name = db.Column(db.String(10),nullable=False)
    user = db.Column(db.String(20),nullable=False)
    message = db.Column(db.String(100),nullable=False)
    ip = db.Column(db.String(20),nullable=False)
    time = db.Column(db.String(20),nullable=False)

#default route
@app.route('/')
def home():
    return render_template('index.html',roomname_error_code=-1);

#This route is called when room name is entered.
#To check whether room name is valid.
@app.route('/validate',methods=['GET'])
def validate_room():

    room_name = request.args.get('room')

    #room name length should be in between 3 to 10.
    if len(room_name)>10 or len(room_name)<3:
        return render_template('index.html',roomname_error_code=0)

    #room name should be alphanumeric.
    if not room_name.isalnum():
        return render_template('index.html',roomname_error_code=1)

    #fetching entries from database where room_name=room_name
    #To check whether room with given name exist or not.
    get_room_name = Roomname.query.filter_by(room_name=room_name).first();

    #If room name exist then send error message.
    if get_room_name:
        return render_template('index.html',roomname_error_code=2)

    #Checks whether user is logged in.
    if 'user' in session:
        #If exist create entry in table.
        rname = Roomname(room_name=room_name,date_time=datetime.now())
        db.session.add(rname)
        db.session.commit()
        #then redirect to chat room.
        return redirect('/room?room='+room_name)

    #If user is not logged in then proceed to sign in.
    return redirect('/signin/'+room_name)


#Sign In route,
@app.route('/signin/<string:room_name>',methods=['GET','POST'])
def signin(room_name):

    #Handle POST request.
    if request.method == "POST":
        #Getting form data.
        user = request.form.get('user')
        room_name = request.form.get('room_name')
        #Creating session variable.
        session['user'] = user
        session['room_name'] = room_name

        #fetching entries from database where room_name=room_name
        #To check whether room with given name exist or not.
        get_room_name = Roomname.query.filter_by(room_name=room_name).first();

        #If room name exist then send error message.
        if not get_room_name:
            return redirect('/validate?room='+room_name)


        return redirect('/room?room='+room_name)

    #Handle GET request
    return render_template('signin.html',room_name=room_name)

#Chat room route.
@app.route('/room',methods=['POST','GET'])
def room():

    #Handling POST request for chat messages.
    if request.method == 'POST':
        #Getting message from form.
        message = request.form.get('message')
        #Getting ip of the user who sends message.
        ip = request.remote_addr
        #Create entry in database.
        newMessage = Messages(room_name=session['room_name'],user=session['user'],message=message,ip=ip,time=datetime.now())
        db.session.add(newMessage)
        db.session.commit()

    #Handling GET request.
    room_name = request.args.get('room')
    if 'user' in session:
        return render_template('room.html',room_name=room_name)

    return redirect('/signin/'+room_name)

#To fetch messages.
@app.route('/fetch',methods=['POST'])
def fetch():
    if request.method == 'POST':
        room_name = request.form.get('room_name')
        msg_list = Messages.query.filter_by(room_name=room_name).all()
        return render_template('single_message.html',msg_list=msg_list,user=session['user'])

#Logout Route.
@app.route('/logout')
def logout():
    #Deleting Session variable.
    session.pop('user',None)
    #Redirect to Homepage.
    return redirect('/')


#Entry Point.
if __name__=="__main__":
    app.run()
