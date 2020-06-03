from flask import Flask, render_template, request, redirect, url_for
import os

'''Libraries required for connection of postgreSQL database Need to install sqlalchemy and psycopg2
Command : pip install sqlalchemy psycopg2'''

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

#Method to have an authenticated connection to the database
#template : engine = create_engine('postgresql+psycopg2://user:password@hostname/database_name')
#Connectionto the Local Database
os.environ['DATABASE_URL'] = "postgresql+psycopg2://postgres:mutemath966@@localhost/flask"
#Connection to Heroku database
#os.environ['DATABASE_URL'] = "postgresql+psycopg2://wwrbwqttpywumi:a3a8fbe6d6414d66eb3df2de27495158d4e7566ecb4b0151d8ec7bde0a9979be@ec2-3-231-16-122.compute-1.amazonaws.com/d141a4s5ol22hi"

#for establising connection to the DB
engine = create_engine(os.getenv('DATABASE_URL'))
#For creating a session with the DB
db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)
textColor = ""
backgroundColor = ""
Text = ""
#Variable declaration for Login
entered_username = " "
entered_password = " "
admin_user = "Admin"
admin_password = "Admin123"
status=False
#For maintaining a list
text=[]
backgroundcolor = []
textcolor = []


@app.route('/home', methods=["GET", "POST"])
def home():
    global textColor,backgroundColor, text,entered_username, text, backgroundcolor, textcolor
    print(entered_username)
    if request.method == "POST":
        textColor = request.form.get('text-color')
        #the list
        textcolor.append(textColor)
        backgroundColor = request.form.get('background-color')
        #the list
        backgroundcolor.append(backgroundColor)
        Text = request.form.get('text')
        #the list
        text.append(Text)     
        return render_template('home.html',textColor=textcolor,backgroundColor=backgroundcolor,text=text,username=entered_username, length=len(textcolor) )
    else:
        return render_template('home.html', username = entered_username, length=len(textcolor) )

@app.route('/', methods=["GET"])
def index():
    print(request.method)
    if request.method == "POST":
        return redirect(url_for('login'))
    return render_template('login.html',error_message= "", status=status)



@app.route('/login', methods=["POST"])
def login():
    print(request.method)
    global entered_password, entered_username
    entered_username = request.form.get('email')
    entered_password = request.form.get('pass')
    user_status=False
    if request.method == "POST":
        #fetch from the DB all the users and password
        users = db.execute("SELECT * FROM users").fetchall()
        #For the case in which no user exists in the DB
        if len(users) == 0:
            return render_template('error.html', error_message="No user currently active. Please register a user First.") 
        #If the entered_username == Admin
        elif entered_username == admin_user and entered_password == admin_password:			
            return redirect(url_for('admin'))
        #For any other user.
        else:
            #First a check if the user exists or not.
            for user in users:
                if entered_username == user.username:
                    user_status = True
                    userId = user.id			
            #If the user exists, then redirect it to homepage for the user after fetching the password for the user, based on id in the db.								
            if user_status:
                command = "SELECT password FROM users WHERE id="+str(userId)
                user_password = db.execute(command).fetchone()[0]
                #Matching for the password entered and password fetched from the DB.
                if entered_password == user_password:
                    return redirect(url_for('home'))
                else:
                    
                    return render_template('login.html', error_message="Invalid username or password.")
                    return redirect(url_for('index'))

            else:
                
                return render_template('login.html', error_message="Invalid username or password.")
                return redirect(url_for('index'))
    else:
        return render_template('login.html',error_message= "", status=status)

if __name__ == "__main__":
	app.run()

