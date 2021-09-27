#Made by Sushaan Patel
import os
import time
import random
import dotenv
import mysql.connector
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_login import LoginManager, login_required, current_user, login_user, logout_user, UserMixin

app = Flask(__name__)
dotenv.load_dotenv()
user = os.environ.get('USER')
passw = os.environ.get('PASS')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{passw}@us-cdbr-east-03.cleardb.com/heroku_90bf9fb7090b7d5'
app.config['SQLALCHEMY_POOL_RECYCLE'] = 60
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "passmanagerseckey"
db2 = SQLAlchemy(app)

class Users(db2.Model, UserMixin):
    id = db2.Column(db2.Integer, primary_key = True)
    username = db2.Column(db2.String(100))
    password = db2.Column(db2.String(100))

con = mysql.connector.connect(
  host="us-cdbr-east-03.cleardb.com",
  user=user,
  password=passw,
  database="heroku_90bf9fb7090b7d5"
)

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
  return Users.query.get(user_id)

@login_manager.unauthorized_handler
def unauth():
    return redirect('/login')

@app.route('/', methods=["POST", "GET"])
def main():
    if current_user.is_authenticated:
        return redirect('/home')
    else:
        return render_template('rpg/index.html')

@app.route('/signout')
def signout():
    logout_user()
    return redirect('/login')

@app.route('/signup', methods=["POST", "GET"])
def index():
    # try:
    if current_user.is_authenticated:
        return redirect('/home')
    if request.method == "POST":
        name_res = request.form['new_username'].lower()
        password_res = request.form['new_password']
        remember = True if request.form.get('new_remember_me') else False
        con.reconnect()
        db = con.cursor()
        db.execute("SELECT username FROM users")
        x = db.fetchall()
        for i in x:
            if name_res == i[0]:
                return redirect('/signup')
        password = generate_password_hash(password_res, "sha256")
        db.execute(f"INSERT INTO users(username, password) VALUES('{name_res}','{password}')")
        con.commit()
        db.execute(f"""CREATE TABLE pass_{name_res}(
            pass_id INT AUTO_INCREMENT,
            acc_type VARCHAR(30),
            username VARCHAR(30),
            pass VARCHAR(30),
            PRIMARY KEY(pass_id)
        )""")
        y = Users.query.filter_by(username = name_res).first()
        login_user(y, remember=remember)
        con.commit()
        return redirect('/home')
    else:
        return render_template('rpg/signup.html')
    # except:
    #     return redirect('/error')

@app.route('/login', methods = ["POST", "GET"])
def login():
    # try:
    if current_user.is_authenticated:
        return redirect('/home')
    if request.method == "POST":
        name = request.form['username'].lower()
        password = request.form['password']
        remember = True if request.form.get('new_remember_me') else False
        con.reconnect()
        db = con.cursor()
        db.execute(f"SELECT * from users WHERE username = '{name}'")
        x = db.fetchall()
        if check_password_hash(x[0][2], password):
            y = Users.query.filter_by(username = name).first()
            login_user(y, remember=remember)
            return redirect('/home')
        else:
            return redirect('/login')
    else:
        return render_template('rpg/login.html')
    # except:
    #     return redirect('/error')

@app.route('/home', methods = ["POST", "GET"])
@login_required
def mid():
    # try:
    if request.method == "POST":
        search = request.form['search']
        con.reconnect()
        db = con.cursor()
        db.execute(f"SELECT * FROM pass_{current_user.username} WHERE acc_type LIKE '%{search}%' ")
        passes = db.fetchall()
        msg = "searched"
        return render_template('rpg/home.html', passes = passes, msg = msg)
    else:
        con.reconnect()
        db = con.cursor()
        db.execute(f"SELECT * FROM pass_{current_user.username}")
        passes = db.fetchall()
        msg = ""
        return render_template('rpg/home.html', passes = passes, msg = msg)
    # except:
    #     return redirect('/error')
    
@app.route('/generate', methods = ["POST", "GET"])
@login_required
def gen():
    try:
        alph = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
        alp = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
        nums1 = random.randint(0,10)
        nums2 = random.randint(0,10)
        nums3 = random.randint(0,10)
        nums4 = random.randint(0,10)
        a = random.randint(0,1)
        pas = ""
        if a == 0:
            char1 = random.choice(alph)
            char2 = nums1
            char3 = random.choice(alph)
            char4 = nums2
            char5 = random.choice(alph)
            char6 = nums3
            char7 = random.choice(alph)
            char8 = nums4
            pas = char1 + str(char2) + char3 + str(char4) + char5 + str(char6) + char7 + str(char8)
        if a == 1:
            char11 = nums1**2
            char22 = random.choice(alp)
            char33 = nums2**2
            char44 = random.choice(alp)
            char55 = nums3**2
            char66 = random.choice(alp)
            char77 = nums4**2
            char88 = random.choice(alp)
            pas = str(char11) + char22 + str(char33) + char44 + str(char55) + char66 + str(char77) + char88
        if request.method == "POST":
            acc_type = request.form['acc_type']
            acc_user = request.form['acc_user']
            acc_pass = request.form['acc_pass']
            con.reconnect()
            db = con.cursor()
            db.execute(f"INSERT INTO pass_{current_user.username}(acc_type, username, pass) VALUES(%s,%s,%s)", (acc_type, acc_user, acc_pass))
            con.commit()
            return redirect('/home')
        else:
            return render_template("rpg/gen.html", a = a, pas=pas)
    except:
        return redirect('/error')

@app.route('/delete/<int:elem>')
@login_required
def delete(elem):
    try:
        con.reconnect()
        db = con.cursor()
        db.execute(f"DELETE FROM pass_{current_user.username} WHERE pass_id = '{elem}'")
        con.commit()
        return redirect('/home')
    except:
        return redirect('/error')


@app.route('/error')
def error():
    try:
        return render_template("rpg/error.html")
    except:
        return render_template("rpg/error.html") 

@app.route('/delete_acc')
@login_required
def del_acc():
    try:
        con.reconnect()
        db = con.cursor()
        db.execute(f"DELETE FROM users WHERE username = '{current_user.username}'")
        db.execute(f"DROP TABLE pass_{current_user.username}")
        con.commit()
        return redirect('/signup')
    except:
        return redirect('/error')

@app.route('/update/<int:ele>', methods=['POST', 'GET'])
@login_required
def update(ele):
    try:
        con.reconnect()
        db = con.cursor()
        db.execute(f"SELECT * from pass_{current_user.username} WHERE pass_id='{ele}'")
        y = db.fetchall()
        if request.method == "POST":
            up_type = request.form["up_type"]
            up_user = request.form["up_user"]
            up_pass = request.form["up_pass"]
            con.reconnect()
            db = con.cursor()
            db.execute(f"UPDATE pass_{current_user.username} SET acc_type = '{up_type}', username = '{up_user}', pass = '{up_pass}' WHERE pass_id = '{ele}'")
            con.commit()
            return redirect('/home')
        else:
            return render_template('rpg/updatepass.html', y=y[0])
    except:
        return redirect('/error')

if __name__ == "__main__":
  app.run(debug=True)
