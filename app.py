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
#os.environ['DATABASE_URL'] = "postgresql+psycopg2://ygxlhfqvqavygx:c8e92f760da666fa8457f28e9bbf9c7e5e4c11dd087409cdbeaba31b844be85a@ec2-18-211-48-247.compute-1.amazonaws.com:5432/d6sv13havqsimc"

#for establising connection to the DB
engine = create_engine(os.getenv('DATABASE_URL'))
#For creating a session with the DB
db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)

#Variable declaration for Login
entered_username = " "
entered_password = " "
admin_user = "Admin"
admin_password = "Admin123"
status=False
selectedImage = ""

'''This is for the homepage'''
@app.route('/home', methods=["GET", "POST"])
def home():
    #get the images list
    imagesList = os.getcwd()
    imagesList = (os.listdir(imagesList + "/static/images"))
    global entered_username
    if request.method == "POST":
        #To fetch the values from the textbox
        message = request.form.get('text')
        '''Insert into Db for the css property'''
        db.execute("INSERT INTO css (message, loginuser, backgroundimage) VALUES (:message, :loginuser, :backgroundimage)", {"message":message, "loginuser":entered_username, "backgroundimage":selectedImage})
        db.commit()

        #Need to fetch all the data stored values in the db\        
        cssProperties = db.execute("SELECT * FROM css").fetchall()
        return render_template('messages.html', fetchedList = cssProperties, length=len(cssProperties), username=entered_username, imagesList=imagesList )
    else:
        return render_template('home.html', username = entered_username, imagesList=imagesList)

'''This is for the root page'''
@app.route('/', methods=["GET"])
def index():
    if request.method == "POST":
        return redirect(url_for('login'))
    return render_template('login.html',error_message= "", status=status)


'''This is for the login page'''
@app.route('/login', methods=["POST"])
def login():
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
                    return redirect(url_for('message'))
                else:
                    
                    return render_template('login.html', error_message="Invalid username or password.")
                    return redirect(url_for('message'))

            else:
                
                return render_template('login.html', error_message="Invalid username or password.")
                return redirect(url_for('message'))
    else:
        return render_template('login.html',error_message= "", status=status)

'''This is for the recover page'''
@app.route('/recover', methods=["GET","POST"])
def recover():
    if request.method == "POST":
        recovery_username = request.form.get("recovery_username")
        command = "SELECT password FROM users WHERE username = '"+str(recovery_username + "'")
        recovery_password = db.execute(command).fetchone()      
        if recovery_password is not None:
            return render_template('recover.html',message="Success, your password is writtten below:", password=recovery_password[0])
        else:
            return render_template('recover.html',message="Failure, No user with such username.")
        
    else:
        return render_template('recover.html')

@app.route('/register', methods=["GET", "POST"])
def register():
	if request.method == "POST":
		registered_username = request.form.get('username')
		registered_password = request.form.get('psw')
		registered_confirm_password = request.form.get('psw-repeat')		
		#For matching both the password entered.
		if registered_password != registered_confirm_password:
			return render_template('register.html',failure_message="Password's dont match")
		#For adding the newly added user in the DB.
		else:
			#Before adding in the Db , check if the username already exists
			users = db.execute("SELECT * FROM users").fetchall()
			for user in users:
				#User already exists display output
				if registered_username == user.username:
					return render_template('register.html',failure_message="User already exists. Please enter a different username.") 		
			#Addign the user in the DB.
			db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": registered_username, "password": registered_password})
			db.commit()					
		#For validation of the actual addition of the user
		users = db.execute("SELECT * FROM users").fetchall()
		if len(users) == 0:
			return render_template('error.html', error_message="User not added successfully in the DB.")
		else:
			for user in users:
				#To check for the username in the complete arrray of users and then update the matchStatus flag.
				if user.username == registered_username:
					matchStatus = True
				else:
					matchStatus=False	
		#Final check for the validation of the user in the DB.			
		if matchStatus:
			return render_template('register.html',success_message="User successfully added.")
		else:
			return render_template('register.html',failure_message="Error while user addition")
	return render_template('register.html')

@app.route('/delete_post/<int:id>', methods=["GET","POST"])
def delete_post(id):
    #Delete the entry from database
    db.execute("DELETE FROM css WHERE id=:id",{"id":id})
    db.commit()
    #Now reload all the data again
    cssProperties = db.execute("SELECT * FROM css").fetchall()
    #return render_template('home.html', fetchedList = cssProperties, length=len(cssProperties), username=entered_username)
    return redirect(url_for('home'))

@app.route('/backgroundselection/<string:img_name>', methods=["GET","POST"])
def backgroundselection(img_name):
    global selectedImage
    selectedImage = img_name
    return redirect(url_for('home'))

@app.route('/messages', methods=["GET","POST"])
def message():
    if entered_username == None or entered_username == " " :
            return render_template('error.html', error_message="Please login first")
    if request.method == "GET":
        cssProperties = db.execute("SELECT * FROM css").fetchall()
        return render_template('messages.html', fetchedList = cssProperties, length=len(cssProperties), username=entered_username)
    return render_template('messages.html', username = entered_username)



#This function is for sending of email
def sendEmail(email):
        return 'True'

if __name__ == "__main__":
	app.run()

