from flask import Flask
from flask import flash
from flask import render_template, redirect, url_for, request, session
import config
from sqlalchemy import or_, and_

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
    neighbor = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __init__(self, room_name, city, neighbor,price):
        self.room_name = room_name
        self.city = city
        self.neighbor = neighbor
        self.price = price

class people(db.Model):
    #id = db.Column('id', db.Integer, primary_key = True)
    email = db.Column(db.String(200), nullable=False)
    name= db.Column(db.String(20), primary_key = True)
    
    password = db.Column(db.String(200), nullable=False)
   

    def __init__(self, email, name, password):
        self.name = name
        self.email = email
        self.password= password
        

@app.before_first_request
def create_tables():
    db.create_all()
    print(db)

@app.route('/')
def show_all():
    return render_template('show_all.html', rooms = Rooms.query.all() )

@app.route('/after')
def after_show():
    return render_template('after_show.html', rooms = Rooms.query.all() )



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        register_password = request.form['password']
        register_name= request.form['name']
        register_email=request.form['email']
        if register_name != '' and register_password != '' :
            if register_email !='':
                ques = people.query.filter_by(name =register_name ).all()
                if len(ques)==0:
                    new_people = people(request.form['name'], request.form['email'],request.form['password'])
                    db.session.add(new_people)
                    db.session.commit()
                    return render_template("search.html")
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
        login_password = request.form['password']
        login_name= request.form['name']
        if login_name != '' and login_password != '' :
            ques = people.query.filter_by(name =login_name ).all()
            if len(ques)==0:
                flash( "the username is incorrect, please register or enter correct username") 
                return render_template('login.html')
            else:
                if people.query.filter_by(password =login_password ).all():
                    return redirect('/after')
               
    return render_template('login.html')

@app.route('/logout')
def logout():
    return redirect('/login')


@app.route('/new', methods = ['GET', 'POST'])
def new():
   if request.method == 'POST':
      if not request.form['room_name'] :
          flash('Please enter all the fields', 'error')
      else:
         room = Rooms(request.form['room_name'], request.form['city'],request.form['neighbor'], request.form['price'])

         db.session.add(room)
         db.session.commit()
         flash('Record was successfully added')
         msg = "Record successfully added"
         return render_template("result.html",msg = msg)
   return render_template('new.html')

@app.route('/postpage')
def index():
    return render_template('postPage.html')



@app.route('/search/')
def search():
    c = request.args.get('city')
    n = request.args.get('neighbor')
    if c != '' and n != '':
        ques = Rooms.query.filter(
            and_(
                Rooms.city == c,

                Rooms.neighbor == n
            ))
    elif c == '' and n != '':
        ques = Rooms.query.filter(
            and_(

                Rooms.neighbor == n
            ))
    elif c != '' and n == '':
        ques = Rooms.query.filter(
            and_(

                Rooms.city == c
            ))
    return render_template('search.html', rooms=ques)
if __name__ == '__main__':
    print(Rooms.query.all())
    print(people.query.all()[0])
 
   
    
    app.run(host='0.0.0.0', port=8080, debug=True)

