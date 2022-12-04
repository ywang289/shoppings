from flask import Flask
from flask import flash
from flask import render_template, redirect, url_for, request, session
import config
from datetime import datetime
from sqlalchemy import or_, and_
from sqlalchemy import desc


from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rooms.sqlite3'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

class Rooms(db.Model):
    #id = db.Column('id', db.Integer, primary_key = True)
    room_name = db.Column(db.String(20), primary_key = True)
    city = db.Column(db.String(200), nullable=False)
    neighbor = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __init__(self, room_name, city, neighbor,price):
        self.room_name = room_name
        self.city = city
        self.neighbor = neighbor
        self.price = price

class people(db.Model):
    #id = db.Column('id', db.Integer, primary_key = True)
    name= db.Column(db.String(20), primary_key = True)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
   

    def __init__(self, name,email, password):
        self.name = name
        self.email = email
        self.password= password
    
    

class message(db.Model):
    
    name= db.Column(db.String(20), primary_key = True)
    message = db.Column(db.String(200), nullable=False)

    def __init__(self, name,message):
        self.name = name
        self.message = message
       
messages=[]       
current_user=[] 

@app.before_first_request
def create_tables():
    db.create_all()
    # room = Rooms("villas", "buffalo",3, 1000)
    # db.session.add(room)
    # db.session.commit()

    # room2 = Rooms("good_house", "bulo",1, 1500)
    # db.session.add(room2)
    # db.session.commit()

    # room3 = Rooms("near_sea_house", "la",5, 6800)
    # db.session.add(room3)
    # db.session.commit()

    
def add_message(username, message):
    now = datetime.now().strftime("%H:%M:%S") # new variable = now
    messages.append({"timestamp": now, "from": username, "message":message})

@app.route('/profile', methods = ["GET", "POST"]) # route decorator that aligns to index.html
def index():
    if request.method == "POST":
        session["username"] = request.form["username"]
        return redirect(url_for("user", username=session["username"]))
        
   
    return render_template("profile.html") # 'index.html' now replaces message



@app.route('/chat/<username>', methods = ["GET", "POST"])
def user(username):
    """ Add & Display chat messages. {0} = username argument """
    """ username & messages get added to the list """
    if request.method == "POST":
        username = session["username"]
        message = request.form["message"]
        add_message(username,message)
        return redirect(url_for("user", username=session["username"]))
    
    return render_template("chat.html", username = username, chat_messages = messages)

@app.route('/delete',methods = ["GET", "POST"])

def delete():
    username = session["username"]
    message_obj = message.query.filter_by(name=username).all()
    
    if message_obj:
        db.session.delete(message_obj)
    
    db.session.commit()
    

    return redirect('/profile')

    
    
    
    

@app.route('/')
def show_all():
    return render_template('show_all.html', rooms = Rooms.query.all() )

@app.route('/after')
def after_show():
    return render_template('after_show.html',rooms = Rooms.query.all())





@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        register_name= request.form['name']
        register_email=request.form['email']
        register_password = request.form['password']
        if register_name != '' and register_password != '' :
            if register_email !='':
                ques = people.query.filter_by(email =register_email ).all()
                ques2= people.query.filter_by(name = register_name ).all()
                if len(ques2)==0:
                    if len(ques)==0:
                        new_people = people(request.form['name'], request.form['email'],request.form['password'])
                        db.session.add(new_people)
                        db.session.commit()
                        flash( "register successfully") 
                        return redirect('/login')
                    else:
                        flash( "the email is used. Please change another email") 
                        return render_template('register.html')
                else:
                    flash( "the username is used. Please change another username") 
                    return render_template('register.html')
                    
            else:
                flash('Please enter all the fields', 'error')   
        else:
            flash('Please enter all the fields', 'error')
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_name= request.form['name']
        login_password = request.form['password']
        if login_name != '' and login_password != '' :
            ques = people.query.filter_by(name =login_name).all()
            print (ques)
            if len(ques)==0:
                flash( "the username is incorrect, please register or enter correct username") 
                return render_template('login.html')
            else:
                if ques[0].password == login_password:
                    current_user.append(login_name)
                    return redirect('/after')

                else:
                    flash( "please enter the correct password") 
                    return render_template('login.html')
               
    return render_template('login.html')
               

@app.route('/edit', methods=['GET', 'POST'])
def dashboard():
    ques = people.query.filter_by(name =current_user[0]).all()
    print("edit username")
    print(ques)
    if len(ques)!=0:
        email = ques[0].email
        if request.method == "POST":
            new_username  = request.form['name']
            print(new_username)
            if new_username != "":
                Username_query = people.query.filter_by(name=new_username).all()
                if len(Username_query ) !=0 :
                    flash("Username in use")
                else:
                    sql = "UPDATE people SET name = '{}' where email = '{}'".format(new_username, email)
                    db.session.execute(sql)
                    db.session.commit()
                    flash( "update successfully") 
                    return redirect('/login')
        return render_template("edit.html")
    else: 
        flash( "please log in first") 
        return redirect('/login')
               

@app.route('/logout')
def logout():
    return redirect('/login')

@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/new', methods = ['GET', 'POST'])
def new():
   if request.method == 'POST':
      if not request.form['room_name'] :
          flash('Please enter all the fields', 'error')
      else:
        post_name = request.form['room_name']
        room_list = Rooms.query.filter_by(room_name=post_name).all()
       
        if len(room_list)==0:
            room = Rooms(request.form['room_name'], request.form['city'],request.form['neighbor'], request.form['price'])

            db.session.add(room)
            db.session.commit()
            flash('Record was successfully added')
            msg = "Record successfully added"
            return render_template("result.html",msg = msg)
        else:
            flash("please change another room name", 'error')
   return render_template('new.html')

@app.route('/postpage')
def postpage():
    return render_template('postPage.html')


@app.route('/search/')
def search():
    c = request.args.get('city')
    way = request.args.get('direction')
    if way=="from_higher":
        ques=Rooms.query.filter(Rooms.city.endswith(c)).order_by(Rooms.price.desc()).all()
    # elif way=="neighbor_from_smaller":
    #     ques=Rooms.query.filter (Rooms.city.endswith(c))
    #     for i in ques:
    #         print(i.neighbor)
    # elif way=="neighbor_from_higher":
    #     ques=Rooms.query.filter(Rooms.city.endswith(c)).order_by(Rooms.neighbor.desc()).all()
    else:
        ques=Rooms.query.filter(Rooms.city.endswith(c)).order_by(Rooms.price.asc()).all()
    
    return render_template('search.html', rooms=ques)

if __name__ == '__main__':
   
    
  
    app.run(host='0.0.0.0', port=8080, debug=True)

