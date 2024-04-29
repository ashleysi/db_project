from flask import Flask, render_template, request, session, url_for, redirect, jsonify, flash
from passlib.hash import pbkdf2_sha256
import pymysql.cursors
import re

app = Flask(__name__)

app.secret_key = 'steven'

conn = pymysql.connect(
    host='127.0.0.1',
    #host='localhost',
    port=3306,
    user='root',
    password='Database',
    db='Roomio2',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

@app.route('/')
def homepage():
    return render_template('index.html')

def get_db_connection():
    return pymysql.connect(host='127.0.0.1', user='root', password='Database', db='Roomio2', cursorclass=pymysql.cursors.DictCursor)

@app.template_filter()
def format_currency(value):
    return f"${value:,.2f}"

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    username = request.form['username']
    submitted_password = request.form['password']  # The password submitted by the user during login

    cursor = conn.cursor()

    # Query to get the stored hashed password for the given username
    # This is a paramaterized query which prevent SQL injection because it treats the input as DATA not an executable
    # This line takes the username as %s serving as the temporary placeholder
    query = 'SELECT passwd FROM Users WHERE username = %s'
    # In this line, the actual username value from the database is used (must be a tuple even with only one parameter)
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
    
    # Check to see if theres a special character from the user input on the registration page
    def check_input(username, first_name, last_name, email, phone):
        # If there's a special character return false (the input is not valid)
        if not all (current_character.isalnum() or current_character.isspace() for current_character in [username, first_name, last_name]):
            return False
        return True

    # Check to see if theres a special character from the user input on the registration page
    if not check_input(username, first_name, last_name, email, phone):
        input_error = "Username, first name and last name cannot have special characters."
        return render_template('register.html', error=input_error)

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
        return render_template('index.html')

@app.route('/home')
def home():
    user = session.get('username')
    if not user:
        print("Redirecting to login: 'username' not in session")  # Debug: log redirect reason
        return redirect(url_for('login'))
    return render_template('home.html', username=user)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.clear()
    return redirect('/')


@app.route('/edit_pet', methods=['GET', 'POST'])
def edit_pet():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if no user is logged in

    conn = get_db_connection()
    if request.method == 'POST':
        pet_name_type = request.form['pet']
        new_pet_size = request.form['new_pet_size']
        owner_username = session['username']
        
        pet_name, pet_type = pet_name_type.split('-')

        cursor = conn.cursor()
        query = 'UPDATE Pets SET PetSize = %s WHERE PetName = %s AND PetType = %s AND username = %s'
        cursor.execute(query, (new_pet_size, pet_name, pet_type, owner_username))
        conn.commit()
        cursor.close()
    else:
        owner_username = session.get('username')
        cursor = conn.cursor()
        query = 'SELECT PetName, PetType, PetSize FROM Pets WHERE username = %s'
        cursor.execute(query, (owner_username,))
        pets = cursor.fetchall()
        cursor.close()

    conn.close()
    return render_template('edit_pet.html', pets=pets)

@app.route('/edit_pet_detail', methods=['GET', 'POST'])
def edit_pet_detail():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if no user is logged in

    username = session['username']
    conn = get_db_connection()

    if request.method == 'POST':
        pet_name = request.form['pet_name']
        pet_type = request.form['pet_type']
        new_pet_size = request.form['pet_size']
        original_pet_name = request.args.get('pet_name')
        original_pet_type = request.args.get('pet_type')

        cursor = conn.cursor()
        # Check for any other pets with the same new name and type that aren't the current pet
        cursor.execute('SELECT 1 FROM Pets WHERE PetName = %s AND PetType = %s AND username = %s AND NOT (PetName = %s AND PetType = %s)',
                       (pet_name, pet_type, username, original_pet_name, original_pet_type))
        if cursor.fetchone():
            flash("Duplicate pet detected. Please choose a different name or type.", 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('edit_pet'))
        
        # Update the pet details in the database if no duplicate is found
        cursor.execute('''
            UPDATE Pets
            SET PetName = %s, PetType = %s, PetSize = %s
            WHERE PetName = %s AND PetType = %s AND username = %s
        ''', (pet_name, pet_type, new_pet_size, original_pet_name, original_pet_type, username))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Pet details updated successfully.', 'success')
        return redirect(url_for('edit_pet'))

    # For GET requests, fetch the current pet details
    pet_name = request.args.get('pet_name')
    pet_type = request.args.get('pet_type')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Pets WHERE PetName = %s AND PetType = %s AND username = %s',
                   (pet_name, pet_type, username))
    pet = cursor.fetchone()
    cursor.close()
    conn.close()

    if pet is None:
        return "Pet not found", 404

    return render_template('edit_pet_detail.html', pet=pet)

@app.route('/add_pet', methods=['GET', 'POST'])
def add_pet():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        pet_name = request.form['pet_name']
        pet_type = request.form['pet_type']
        pet_size = request.form['pet_size']
        username = session['username']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check for duplicate pet entry
        cursor.execute('SELECT 1 FROM Pets WHERE PetName = %s AND PetType = %s AND username = %s',
                       (pet_name, pet_type, username))
        if cursor.fetchone():
            flash("A pet with this name and type already exists.", "error")
            cursor.close()
            conn.close()
            return redirect(url_for('edit_pet'))

        # Proceed to insert the new pet if no duplicate found
        query = 'INSERT INTO Pets (PetName, PetType, PetSize, username) VALUES (%s, %s, %s, %s)'
        cursor.execute(query, (pet_name, pet_type, pet_size, username))
        conn.commit()
        cursor.close()
        conn.close()

        flash("New pet added successfully.", "success")
        return redirect(url_for('edit_pet'))

    return render_template('add_pet.html')


@app.route('/delete_pet', methods=['POST'])
def delete_pet():
    if 'username' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    pet_name = request.form['pet_name']
    pet_type = request.form['pet_type']
    username = session['username']

    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'DELETE FROM Pets WHERE PetName = %s AND PetType = %s AND username = %s'
    cursor.execute(query, (pet_name, pet_type, username))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('edit_pet'))


@app.route('/user_pets')
def user_pets():
    owner_username = session.get('username')  # Get the logged-in user's username from the session
    cursor = conn.cursor()
    query = 'SELECT PetName, PetType FROM Pets WHERE username = %s'
    cursor.execute(query, (owner_username,))
    pets = cursor.fetchall()  # Fetch all pets for the logged-in user
    cursor.close()
    return render_template('user_pets.html', pets=pets)

@app.route('/search2')
def search2():
    return render_template('search2.html')

@app.route('/search2_results', methods=['POST'])
def search2_results():
    conn = get_db_connection()
    cursor = conn.cursor()

    state = request.form.get('state')
    city = request.form.get('city')
    zipCode = request.form.get('zipCode')
    yearBuilt = request.form.get('yearBuilt')
    
    # Start with the base query
    query = 'SELECT * FROM ApartmentBuilding'

    # List to hold the conditions
    conditions = []

    if state:
        conditions.append(f"AddrState = '{state}'")
    if city:
        conditions.append(f"AddrCity = '{city}'")
    if zipCode:
        conditions.append(f"AddrZipCode = '{zipCode}'")
    if yearBuilt:
        conditions.append(f"YearBuilt = {yearBuilt}")

    # Only add WHERE clause if there are conditions
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        print("Error executing query:", e)
        return jsonify({"error": str(e)})
    finally:
        cursor.close()

@app.route('/view/units')
def view_units():
    if 'username' not in session:
        return 'Please log in to view this page', 401  # Redirect or handle not logged in users

    username = session['username']  # Retrieve the logged-in user's username
    conn = get_db_connection()
    company_name = request.args.get('companyName')
    building_name = request.args.get('buildingName')

    cursor = conn.cursor()
    # Fetch unit details and interests
    query = """
        SELECT AU.UnitRentID, AU.unitNumber, AU.MonthlyRent, AU.squareFootage, AU.AvailableDateForMoveIn,
               IF(EXISTS(SELECT 1 FROM Favorite WHERE Favorite.UnitRentID = AU.UnitRentID AND Favorite.Username = %s), 1, 0) AS IsFavorited,
               GROUP_CONCAT(DISTINCT CONCAT(U.first_name, ' ', U.last_name, ': ', I.RoommateCnt, ' roommates, moving in on ', I.MoveInDate) ORDER BY I.MoveInDate DESC SEPARATOR '; ') AS Interests
        FROM ApartmentUnit AU
        LEFT JOIN Interests I ON AU.UnitRentID = I.UnitRentID
        LEFT JOIN Users U ON I.username = U.username
        WHERE AU.CompanyName = %s AND AU.BuildingName = %s
        GROUP BY AU.UnitRentID
    """
    cursor.execute(query, (username, company_name, building_name))
    units = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('view_units.html', units=units, company_name=company_name, building_name=building_name)


@app.route('/view_pet_policy')
def view_pet_policy():
    unit_rent_id = request.args.get('unitRentID')
    if not unit_rent_id:
        return 'No unit specified', 400

    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT PP.PetType, PP.PetSize, PP.isAllowed, PP.RegistrationFee, PP.MonthlyFee
        FROM PetPolicy PP
        JOIN ApartmentUnit AU ON PP.CompanyName = AU.CompanyName AND PP.BuildingName = AU.BuildingName
        WHERE AU.UnitRentID = %s
    """
    cursor.execute(query, (unit_rent_id,))
    pet_policies = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('view_pet_policy.html', pet_policies=pet_policies, unit_rent_id=unit_rent_id)



@app.route('/estimate')
def estimate():
    return render_template('estimate.html')

@app.route('/get-zipcodes')
def get_zipcodes():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT DISTINCT AddrZipCode FROM ApartmentBuilding')
            zipcodes = cursor.fetchall()
            return jsonify([zipcode['AddrZipCode'] for zipcode in zipcodes])
    finally:
        conn.close()

@app.route('/calculate-average', methods=['POST'])
def calculate_average():
    zipcode = request.form['zipcode']
    bedrooms = int(request.form['bedrooms'])
    bathrooms = int(request.form['bathrooms'])
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            query = """
            SELECT AVG(U.MonthlyRent) AS AverageRent
            FROM ApartmentUnit U
            JOIN ApartmentBuilding B ON U.CompanyName = B.CompanyName AND U.BuildingName = B.BuildingName
            WHERE B.AddrZipCode = %s
            AND (
                SELECT COUNT(*)
                FROM Rooms R
                WHERE R.UnitRentID = U.UnitRentID AND R.name LIKE 'bedroom%%'
            ) = %s
            AND (
                SELECT COUNT(*)
                FROM Rooms R
                WHERE R.UnitRentID = U.UnitRentID AND R.name LIKE 'bathroom%%'
            ) = %s
            """
            cursor.execute(query, (zipcode, bedrooms, bathrooms))
            result = cursor.fetchone()
            average_rent = result['AverageRent'] if result['AverageRent'] else 0
            print("Average rent calculated:", average_rent)
            return jsonify({'averageRent': result['AverageRent'] if result['AverageRent'] else 0})
    finally:
        conn.close()

@app.route('/fetch-units', methods=['POST'])
def fetch_units():
    zipcode = request.form['zipcode']
    bedrooms = int(request.form['bedrooms'])
    bathrooms = int(request.form['bathrooms'])
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            query = """
            SELECT U.UnitRentID, U.unitNumber, U.MonthlyRent, U.squareFootage, U.AvailableDateForMoveIn
            FROM ApartmentUnit U
            JOIN ApartmentBuilding B ON U.CompanyName = B.CompanyName AND U.BuildingName = B.BuildingName
            WHERE B.AddrZipCode = %s
            AND (
                SELECT COUNT(*)
                FROM Rooms R
                WHERE R.UnitRentID = U.UnitRentID AND R.name LIKE 'bedroom%%'
            ) = %s
            AND (
                SELECT COUNT(*)
                FROM Rooms R
                WHERE R.UnitRentID = U.UnitRentID AND R.name LIKE 'bathroom%%'
            ) = %s
            """
            cursor.execute(query, (zipcode, bedrooms, bathrooms))
            units = cursor.fetchall()
            return jsonify(units)
    finally:
        conn.close()

@app.route('/add_to_favorites', methods=['POST'])
def add_to_favorites():
    if 'username' not in session:
        return jsonify({"success": False, "message": "User not logged in"}), 401  # HTTP 401 for Unauthorized access

    username = session['username']
    unit_rent_id = request.json['unit_rent_id']

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Favorite (Username, UnitRentID) VALUES (%s, %s)"
            cursor.execute(sql, (username, unit_rent_id))
        connection.commit()
        return jsonify({"success": True, "message": "Added to favorites"})
    except pymysql.err.IntegrityError as e:
        connection.rollback()  # Rollback in case of error
        return jsonify({"success": False, "message": "Could not add to favorites: " + str(e)})
    finally:
        connection.close()


@app.route('/favorites')
def favorites():
    if 'username' not in session:
        return 'Please log in to view this page.', 401  # HTTP 401 for Unauthorized access

    username = session['username']
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''
            SELECT ApartmentUnit.* FROM Favorite
            JOIN ApartmentUnit ON Favorite.UnitRentID = ApartmentUnit.UnitRentID
            WHERE Favorite.Username = %s
            '''
            cursor.execute(sql, (username,))
            favorite_units = cursor.fetchall()
            return render_template('favorites.html', favorite_units=favorite_units)
    except Exception as e:
        print("Error fetching favorite units:", e)
        return render_template('favorites.html', favorite_units=None)
    finally:
        connection.close()


@app.route('/unfavorite/<int:unit_id>', methods=['POST'])
def unfavorite(unit_id):
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM Favorite WHERE UnitRentID = %s', (unit_id,))
        conn.commit()
        return redirect(url_for('favorites'))
    except Exception as e:
        print("Error unfavorite unit:", e)
        return redirect(url_for('favorites'))
    finally:
        cursor.close()

@app.route('/search', methods = ['GET'])
def search():
    user = session['username']
    company_name = request.args.get('company_name')
    building_name = request.args.get('building_name')
    pet_y_n = request.args.get('pet_y_n', type=bool)
    minimum_rent = request.args.get('minimum_rent', type=int)
    maximum_rent = request.args.get('maximum_rent', type=int)

    query_pet_type = f"""
        SELECT PetType 
        FROM Pets NATURAL JOIN Users
        WHERE Users.username = '{user}'
    """
    
    query_pet_size = f"""
        SELECT PetSize
        FROM Pets NATURAL JOIN Users
        WHERE Users.username = '{user}'
    """
    
    cursor = conn.cursor()
    
    cursor.execute(query_pet_type)
    pet_type1 = cursor.fetchall()
    #print(pet_type1)
    pet_type2 = pet_type1[0]['PetType']
    #print(pet_type2)
    
    cursor.execute(query_pet_size)
    pet_size1 = cursor.fetchall()
    pet_size2 = pet_size1[0]['PetSize']
    
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
            AND PetPolicy.PetType = '{pet_type2}' AND PetPolicy.PetSize = '{pet_size2}'
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


@app.route('/comments')
def show_comments():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'SELECT username, comment, created_at, company_name, building_name FROM usercomments'
        cursor.execute(query)
        comments = cursor.fetchall()
        conn.close()
        return render_template('comments.html', usercomments=comments)
    except Exception as e:
        return str(e)


@app.route('/comment_page', methods=['GET', 'POST'])
def leave_comment():
    # Initialize default values or fetch from the session or request parameters as fallback
    company_name = request.args.get('companyName', 'DefaultCompany')
    building_name = request.args.get('buildingName', 'DefaultBuilding')

    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()

        username = session.get('username')
        comment_text = request.form['comment']
        # Override defaults with POST data if present
        company_name = request.form.get('companyName', company_name)
        building_name = request.form.get('buildingName', building_name)
        
        query = "INSERT INTO usercomments (username, comment, company_name, building_name) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (username, comment_text, company_name, building_name))
        conn.commit()
        conn.close()

        # Go to comments page, now showing the new comment
        return redirect(url_for('show_comments'))

    # For GET requests, render the form with the company and building names available
    return render_template('comment_page.html', company_name=company_name, building_name=building_name)


if __name__ == '__main__':
    app.run(debug=True)
