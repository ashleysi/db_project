from flask import Flask, render_template, request, session, url_for, redirect
from passlib.hash import pbkdf2_sha256
import pymysql.cursors

app = Flask(__name__)

app.secret_key = 'steven'

conn = pymysql.connect(
    host='127.0.0.1',
    #host='localhost',
    port=3306,
    user='root',
    password='root',
    db='proj_schema',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    username = request.form['username']
    submitted_password = request.form['password']  # The password submitted by the user during login

    cursor = conn.cursor()

    # Query to get the stored hashed password for the given username
    query = 'SELECT passwd FROM Users WHERE username = %s'
    cursor.execute(query, (username,))

    data = cursor.fetchone()
    cursor.close()

    if data:
        # data is a dictionary so need to get value from the 'passwd' key
        stored_hash = data['passwd']
        # Use Passlib to verify the submitted password against the stored hash
        if pbkdf2_sha256.verify(submitted_password, stored_hash):
            # Password matches
            session['username'] = username
            return redirect(url_for('home'))  # Redirect to main page if login is successful
        else:
            # Password does not match
            error = 'Invalid login or username'
            return render_template('index.html', error=error)
    else:
        # Username not found
        error = 'This username does not exist'
        return render_template('index.html', error=error)

@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    username = request.form['username']
    first_name = request.form['FName']
    last_name = request.form['LName']
    DOB = request.form['DOB']
    gender = request.form['gender']
    email = request.form['email']
    phone = request.form['phone']
    password = request.form['pw']
    hashed_password = pbkdf2_sha256.hash(password)

    cursor = conn.cursor()
    query = 'SELECT * FROM Users WHERE username = %s'
    cursor.execute(query, (username,))

    data = cursor.fetchone()

    if data:
        error = 'This user already exists'
        cursor.close()
        return render_template('register.html', error=error)
    else:
        ins = 'INSERT INTO Users (username, first_name, last_name, DOB, gender, email, phone, passwd) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, first_name, last_name, DOB, gender, email, phone, hashed_password))
        conn.commit()
        cursor.close()
        return render_template('temp.html')

@app.route('/home')
def home():
    user = session['username']
    return render_template('temp2.html', username=user)

@app.route('/pet_register', methods=['GET', 'POST'])
def pet_register():
    if request.method == 'POST':
        pet_name = request.form['pet_name']
        pet_type = request.form['pet_type']
        pet_size = request.form['pet_size']
        owner_username = session['username']

        cursor = conn.cursor()
        query = 'SELECT * FROM registered_pet WHERE pet_name = %s AND owner_username = %s'
        cursor.execute(query, (pet_name, owner_username))
        data = cursor.fetchone()

        if data:
            error = 'This pet already exists'
            cursor.close()
            return render_template('pet_register.html', error=error)
        else:
            ins = 'INSERT INTO registered_pet (pet_name, pet_type, pet_size, owner_username) VALUES (%s, %s, %s, %s)'
            cursor.execute(ins, (pet_name, pet_type, pet_size, owner_username))
            conn.commit()
            cursor.close()
            return render_template('registerPet.html')  # Redirect to thank you page after successful pet registration
    else:
        return render_template('pet_register.html')

@app.route('/registerPet', methods=['GET', 'POST'])
def registered_pet():
    return render_template('registerPet.html')

if __name__ == '__main__':
    app.run(debug=True)
