from flask import Flask, render_template, request, session, url_for, redirect
from passlib.hash import pbkdf2_sha256
import pymysql.cursors
import mysql.connector

app = Flask(__name__)

app.secret_key = 'steven'

conn = pymysql.connect(
    host = '127.0.0.1',
    port = 3306,
    user = 'root',
    #password = '083723',
    password = 'Saugust1678@',
    db = 'roomio',
    charset = 'utf8mb4',
    cursorclass = pymysql.cursors.DictCursor
)

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/loginAuth', methods = ['GET', 'POST'])
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

@app.route('/registerAuth', methods = ['GET', 'POST'])
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
    cursor.execute(query, (username))

    data = cursor.fetchone()

    if(data):
        error = 'This user already exists'
        cursor.close()
        return render_template('register.html', error = error)
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

@app.route('/home/search', methods = ['GET'])
def search():
    user = session['username']
    company_name = request.args.get('company_name')
    building_name = request.args.get('building_name')
    pet_y_n = request.args.get('pet_y_n', type=bool)
    minimum_rent = request.args.get('minimum_rent', type=int)
    maximum_rent = request.args.get('maximum_rent', type=int)
    cursor = conn.cursor()
    
    if ((company_name is None) & (building_name is None)):
        cursor.close()
        return render_template('search.html', user=user)
    elif (pet_y_n is True):
        x= "WHERE 1=1"

        if company_name:
            x+= " AND ApartmentBuilding.CompanyName = %s"
        if building_name:
            x+= " AND ApartmentUnit.BuildingName = %s"

        query1 = f"""
            SELECT DISTINCT ApartmentUnit.CompanyName, ApartmentUnit.BuildingName, ApartmentUnit.unitNumber, ApartmentUnit.MonthlyRent, ApartmentUnit.squareFootage, ApartmentUnit.AvailableDateForMoveIn
            FROM ApartmentUnit
            JOIN ApartmentBuilding ON ApartmentUnit.CompanyName = ApartmentBuilding.CompanyName AND ApartmentUnit.BuildingName = ApartmentBuilding.BuildingName
            JOIN PetPolicy ON ApartmentUnit.CompanyName = PetPolicy.CompanyName AND ApartmentUnit.BuildingName = PetPolicy.BuildingName \
            JOIN Interests ON ApartmentUnit.UnitRentID = Interests.UnitRentID \
            JOIN Users ON Interests.username = Users.username \
            JOIN Pets ON Users.username = Pets.username = '{user}' \
            AND PetPolicy.PetType = 'Dog' AND PetPolicy.PetSize = 'Large'
            {x}
        """
        print (query1)
        
        add_ons = []
        if company_name:
            add_ons = add_ons  + [company_name]
        if building_name:
            add_ons = add_ons  + [building_name]
        if minimum_rent:
            add_ons = add_ons  + [minimum_rent]
        if maximum_rent:
            add_ons = add_ons  + [maximum_rent]
    
        #cursor.execute(query1,(building_name, company_name))
        cursor.execute(query1,add_ons)
        units = cursor.fetchall()


        cursor.close()
            
        #return render_template('search.html', user=user)

        #return render_template('search.html', user=user, units=units)

        return render_template('search.html', user=user, units=units,
                               company_name=company_name, building_name=building_name, pet_y_n=pet_y_n,
                              minimum_rent=minimum_rent, maximum_rent=maximum_rent)
    
    else: 
        x= "WHERE 1=1" 

        if company_name:
            x+= " AND ApartmentBuilding.CompanyName = %s"
        if building_name:
            x+= " AND ApartmentUnit.BuildingName = %s"

        # Search for apartment units based on building name and company name
        #query1 = 'SELECT ApartmentUnit.unitNumber, ApartmentUnit.MonthlyRent, ApartmentUnit.squareFootage, ApartmentUnit.AvailableDateForMoveIn \
        #        FROM ApartmentUnit \
        #        JOIN ApartmentBuilding ON ApartmentUnit.CompanyName = ApartmentBuilding.CompanyName AND ApartmentUnit.BuildingName = ApartmentBuilding.BuildingName \
        #        WHERE ApartmentUnit.BuildingName = %s AND ApartmentUnit.CompanyName = %s'
        query1 = f"""
            SELECT DISTINCT ApartmentUnit.CompanyName, ApartmentUnit.BuildingName, ApartmentUnit.unitNumber, ApartmentUnit.MonthlyRent, ApartmentUnit.squareFootage, ApartmentUnit.AvailableDateForMoveIn
            FROM ApartmentUnit
            JOIN ApartmentBuilding ON ApartmentUnit.CompanyName = ApartmentBuilding.CompanyName AND ApartmentUnit.BuildingName = ApartmentBuilding.BuildingName
            {x}
        """
        print (query1)
        
        add_ons = []
        
        if company_name:
            add_ons = add_ons  + [company_name]
        if building_name:
            add_ons = add_ons  + [building_name]
        if minimum_rent:
            add_ons = add_ons  + [minimum_rent]
        if maximum_rent:
            add_ons = add_ons  + [maximum_rent]
    
        #cursor.execute(query1,(building_name, company_name))
        cursor.execute(query1,add_ons)
        units = cursor.fetchall()


        cursor.close()
            
        #return render_template('search.html', user=user)

        #return render_template('search.html', user=user, units=units)

        return render_template('search.html', user=user, units=units,
                               company_name=company_name, building_name=building_name,
                              minimum_rent=minimum_rent, maximum_rent=maximum_rent)
        
    
if __name__ == '__main__':
    app.run(port=3000, debug=True)
