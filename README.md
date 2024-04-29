# Database Project

Group Members: Samantha Augustin, Steven Granaturov, Ashley Simons

# Roomio Application Overview

## Features Status

### ✅ Completed Features

- **Login & User Session Handle**:

  - Users can register a new account.
  - Only registered users are allowed to log in.
  - Passwords are salted and hashed at the database level.
  - User sessions are created upon successful login.

- **Search Certain Apartment Units**:

  - Search apartment units by building name and company name.
  - Display list of units for rent including details like monthly rent, square footage, and available move-in date.
  - System checks if pets are allowed based on the user's registered pets.

- **Register Pet**:

  - Users can register pets associated with their accounts.
  - Users can edit information of registered pets.
  - Users can view their pets and all assosciated information

- **Estimate Monthly Rent**:

  - Users can input a zipcode and the number of rooms.
  - The application calculates the average monthly rent based on the requirements.

- **Favorite**:

  - Users can add units to their favorites for quick access.

  - **Display Unit and Building Info**:
  - Search and display detailed information about buildings and units.
  - View pet policies for every unit

  - **Necessary Security Mechanisms**:
  - Implementing mechanisms to prevent SQL Injection and XSS attacks.

### 🚧 Work In Progress

- **More Advanced Search of Units**:

  - Advanced search options including amenities and expected monthly rent.

- **Post and View Interests**:

  - Viewing and posting interests in specific apartment units.

### ❌ Not Complete

- **Search Interest**:

  - Search for an interest in a certain unit based on move-in date and roommate count.

- **Extra View on the Rent Price**:

  - Display the average price of similar units within the same city.

- **Recommend System**:
  - Recommend similar units within and outside the same buildings based on user-defined criteria.

## Setup Instructions

- \*\* Setup Instructions:
- Please drop all tables
- Recreate all tables + Favorites table with Schema below.
- Insert all values from sample_data.txt
- Passwords for all those accounts is 'password'

Favorite table:
CREATE TABLE Favorite (
FavoriteID INT AUTO_INCREMENT PRIMARY KEY,
Username VARCHAR(20) NOT NULL,
UnitRentID INT NOT NULL,
FOREIGN KEY (Username) REFERENCES Users(username),
FOREIGN KEY (UnitRentID) REFERENCES ApartmentUnit(UnitRentID),
UNIQUE (Username, UnitRentID)
);
