from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import date
import time
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['MYSQL_HOST'] = '192.168.18.161'
app.config['MYSQL_USER'] = 'alisql'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'alnafi'
mysql = MySQL(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(id=user[0], username=user[1], email=user[3])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user:
            user_obj = User(id=user[0], username=user[1], email=user[3])
            login_user(user_obj)
            return redirect(url_for('get_home'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Password validation
        if not re.match(r'^[a-zA-Z0-9]+$', password):
            flash('Password can only contain letters and numbers', 'danger')
            return redirect(url_for('register'))

        # Email validation
        if '@' not in email:
            flash('Invalid email address', 'danger')
            return redirect(url_for('register'))

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
        mysql.connection.commit()
        cursor.close()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/")
@login_required
def get_home():
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM trainer_details ORDER BY t_id DESC LIMIT 2"
    cursor.execute(sql)
    recent_entries = cursor.fetchall()
    cursor.close()
    return render_template("index.html", recent_entries=recent_entries)

@app.route("/trainer")
@login_required
def trainer():
    return render_template("trainer_details.html")

@app.route("/trainer_create", methods=["POST", "GET"])
@login_required
def trainer_create():
    if request.method == "POST":
        fname = request.form['first-name']
        lname = request.form['last-name']
        designation = request.form['designation']
        course = request.form['course-name']
        cdate = date.today()
        sql = "INSERT INTO trainer_details (fname, lname, design, course, datetime) VALUES (%s,%s,%s,%s,%s)"
        val = (fname, lname, designation, course, cdate)

        cursor = mysql.connection.cursor()
        cursor.execute(sql, val)

        mysql.connection.commit()

        cursor.close()
        return render_template('trainer_details.html')

@app.route("/trainer_data", methods=["POST", "GET"])
@login_required
def trainer_data():
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM trainer_details"
    cursor.execute(sql)
    row = cursor.fetchall()
    cursor.close()
    return render_template('display_trainer.html', output_data=row)

@app.route("/delete_trainer/<int:t_id>", methods=["GET", "POST"])
@login_required
def delete_trainer(t_id):
    cursor = mysql.connection.cursor()
    sql = "DELETE FROM trainer_details WHERE t_id = %s"
    cursor.execute(sql, (t_id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('trainer_data'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="9000")
