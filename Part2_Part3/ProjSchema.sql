DROP TABLE IF EXISTS AmenitiesIn;
DROP TABLE IF EXISTS Provides;
DROP TABLE IF EXISTS Interests;
DROP TABLE IF EXISTS Pets;
DROP TABLE IF EXISTS PetPolicy;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Rooms;
DROP TABLE IF EXISTS ApartmentUnit;
DROP TABLE IF EXISTS ApartmentBuilding;
DROP TABLE IF EXISTS Amenities;


-- According to the ER diagram, phone and email are multi-valued attributes, so they should be represented by separate table(s); For simplicity, we are making them single-valued attributes here.
CREATE TABLE Users (
    username VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(20) NOT NULL,
    DOB date NOT NULL,
    gender TINYINT NOT NULL, -- 0 for male, 1 for female
    email VARCHAR(50),
    Phone VARCHAR(20),
    passwd VARCHAR(200) -- you may change this to larger size if not enough for hashed passwd
);
INSERT INTO Users (username, first_name, last_name, DOB, gender, email, Phone, passwd) VALUES
("JKim", 'Jake', 'Kim', '1990-02-20', 0, 'jake@gmail.com', '1123456789', 'JKimPassword'),
("MSmith", 'Matthew', 'Smith', '1999-10-01', 0, 'matthew@gmail.com', '1223456789', 'MSmithPassword'),
("CLee", 'Carol', 'Lee', '2000-08-10', 1, 'carol@gmail.com', '1233456789', 'CLeePassword'),
("RJane", 'Ruby', 'Jane', '1994-11-27', 1, 'ruby@gmail.com', '1234456789', 'RJanePassword'),
("JStone", 'Jeffery', 'Stone', '1980-01-05', 0, 'JStone@gmail.com', '1234556789', 'JStonePassword');
SELECT * FROM Users;

CREATE TABLE Pets (
   PetName VARCHAR(50) NOT NULL,
   PetType VARCHAR(50) NOT NULL,
   PetSize VARCHAR(20) NOT NULL,
   username VARCHAR(20) NOT NULL,
   FOREIGN KEY (username) REFERENCES Users (username),
   PRIMARY KEY (PetName,PetType,username)
);
INSERT INTO Pets (PetName, PetType, PetSize, username) VALUES
('Zuko', 'Dog', 'Medium', 'JKim'),
('Matt', 'Dog', 'Large', 'MSmith'),
('Mr. Meow', 'Cat', 'Small', 'CLee'),
('Whiskers', 'Cat', 'Medium', 'RJane'),
('Birdy', 'Bird', 'Small', 'JStone');
SELECT * FROM Pets;

CREATE TABLE ApartmentBuilding(
    CompanyName VARCHAR(50) NOT NULL,
    BuildingName VARCHAR(50) NOT NULL,
    AddrNum INT NOT NULL,
    AddrStreet VARCHAR(50) NOT NULL,
    AddrCity VARCHAR(50) NOT NULL,
    AddrState VARCHAR(5) NOT NULL,
    AddrZipCode VARCHAR(5) NOT NULL,
    YearBuilt YEAR NOT NULL,
    PRIMARY KEY (CompanyName, BuildingName)
);
INSERT INTO ApartmentBuilding (CompanyName, BuildingName, AddrNum, AddrStreet, AddrCity, AddrState, AddrZipCode, YearBuilt) VALUES
('Queens Apartments', 'Sky High Flushing', 123, 'Main Street', 'Flushing', 'NY', '11355', 2018),
('Brooklyn Properties', 'Jay Street Apartments', 456, 'Jay Street', 'Downtown Brooklyn', 'NY', '11201', 2004),
('Staten Island Realty', 'Ferry Residences', 789, 'Richmond Ave', 'Staten Island', 'NY', '10314', 1994);
SELECT * FROM ApartmentBuilding;

CREATE TABLE ApartmentUnit (
   UnitRentID INT NOT NULL AUTO_INCREMENT,
   CompanyName VARCHAR(50) NOT NULL,
   BuildingName VARCHAR(50) NOT NULL,
   unitNumber VARCHAR(10) NOT NULL,
   MonthlyRent INT NOT NULL,
   squareFootage INT NOT NULL,
   AvailableDateForMoveIn date NOT NULL,
   FOREIGN KEY (CompanyName,BuildingName) REFERENCES ApartmentBuilding (CompanyName,BuildingName),
   PRIMARY KEY (UnitRentID)
);
INSERT INTO ApartmentUnit (CompanyName, BuildingName, unitNumber, MonthlyRent, squareFootage, AvailableDateForMoveIn) VALUES
('Queens Apartments', 'Sky High Flushing', '101', 1300, 900, '2024-04-01'),
('Queens Apartments', 'Sky High Flushing', '102', 1600, 1000, '2024-05-15'),
('Brooklyn Properties', 'Jay Street Apartments', '103', 2000, 1400, '2024-07-11'),
('Brooklyn Properties', 'Jay Street Apartments', '104', 1700, 950, '2024-12-20'),
('Staten Island Realty', 'Ferry Residences', '201', 3000, 1200, '2024-08-05'),
('Staten Island Realty', 'Ferry Residences', '202', 3000, 1200, '2024-06-02');
SELECT * FROM ApartmentUnit;

CREATE TABLE Rooms(
    name VARCHAR(20) NOT NULL,
    squareFootage INT NOT NULL,
    description VARCHAR(50) NOT NULL,
    UnitRentID INT NOT NULL,
    FOREIGN KEY (UnitRentID) REFERENCES ApartmentUnit (UnitRentID),
    PRIMARY KEY (name,UnitRentID)
);
INSERT INTO Rooms (name, squareFootage, description, UnitRentID) VALUES
('Living Room', 400, 'Large living area', 1),
('Kitchen', 200, 'Modern kitchen', 1),
('Bedroom', 200, 'Warm bedroom', 1),
('Bathroom', 100, 'Modern bathroom', 1),

('Living Room', 400, 'Spacious living space', 2),
('Kitchen', 200, 'Colorful kitchen', 2),
('Bedroom', 250, 'Comfortable bedroom', 2),
('Bathroom', 150, 'White bathroom', 2),

('Living Room', 500, 'Open living area', 3),
('Kitchen', 300, 'Modern kitchen', 3),
('Bedroom', 350, 'Cozy bedroom', 3),
('Bathroom', 250, 'Contemporary bathroom', 3),

('Living Room', 300, 'Cozy living area', 4),
('Kitchen', 200, 'Compact kitchen', 4),
('Bedroom', 300, 'Warm bedroom', 4),
('Bathroom', 150, 'New bathroom', 4),

('Living Room', 500, 'Huge living area', 5),
('Kitchen', 300, 'Large kitchen', 5),
('Bedroom', 300, 'Spacious bedroom', 5),
('Bathroom', 100, 'Moden bathroom', 5),

('Living Room', 500, 'Huge living area', 6),
('Kitchen', 300, 'Large kitchen', 6),
('Bedroom', 300, 'Spacious bedroom', 6),
('Bathroom', 100, 'Moden bathroom', 6);
SELECT name, squareFootage, description, UnitRentID FROM Rooms ORDER BY UnitRentID;

CREATE TABLE PetPolicy(
    CompanyName VARCHAR(50) NOT NULL,
    BuildingName VARCHAR(50) NOT NULL,
    PetType VARCHAR(50) NOT NULL,
    PetSize VARCHAR(50) NOT NULL,
    isAllowed BOOLEAN NOT NULL,
    RegistrationFee INT,
    MonthlyFee INT,
    FOREIGN KEY (CompanyName,BuildingName) REFERENCES ApartmentBuilding (CompanyName,BuildingName),
    PRIMARY KEY (CompanyName,BuildingName,PetType,PetSize)
);
INSERT INTO PetPolicy (CompanyName, BuildingName, PetType, PetSize, isAllowed, RegistrationFee, MonthlyFee) VALUES
('Queens Apartments', 'Sky High Flushing', 'Dog', 'Small', true, 50, 25),
('Queens Apartments', 'Sky High Flushing', 'Dog', 'Medium', true, 100, 50),
('Queens Apartments', 'Sky High Flushing', 'Dog', 'Large', false, NULL, NULL),
('Queens Apartments', 'Sky High Flushing', 'Cat', 'Small', true, 25, 15),
('Queens Apartments', 'Sky High Flushing', 'Cat', 'Medium', true, 50, 30),
('Queens Apartments', 'Sky High Flushing', 'Cat', 'Large', false, NULL, NULL),
('Queens Apartments', 'Sky High Flushing', 'Bird', 'Small', true, 15, 10),
('Queens Apartments', 'Sky High Flushing', 'Bird', 'Medium', true, 45, 25),
('Queens Apartments', 'Sky High Flushing', 'Bird', 'Large', false, NULL, NULL),

('Brooklyn Properties', 'Jay Street Apartments', 'Dog', 'Small', false, NULL, NULL),
('Brooklyn Properties', 'Jay Street Apartments', 'Dog', 'Medium', false, NULL, NULL),
('Brooklyn Properties', 'Jay Street Apartments', 'Dog', 'Large', false, NULL, NULL),
('Brooklyn Properties', 'Jay Street Apartments', 'Cat', 'Small', false, NULL, NULL),
('Brooklyn Properties', 'Jay Street Apartments', 'Cat', 'Medium', false, NULL, NULL),
('Brooklyn Properties', 'Jay Street Apartments', 'Cat', 'Large', false, NULL, NULL),
('Brooklyn Properties', 'Jay Street Apartments', 'Bird', 'Small', false, NULL, NULL),
('Brooklyn Properties', 'Jay Street Apartments', 'Bird', 'Medium', false, NULL, NULL),
('Brooklyn Properties', 'Jay Street Apartments', 'Bird', 'Large', false, NULL, NULL),

('Staten Island Realty', 'Ferry Residences', 'Dog', 'Small', true, 40, 30),
('Staten Island Realty', 'Ferry Residences', 'Dog', 'Medium', true, 60, 40),
('Staten Island Realty', 'Ferry Residences', 'Dog', 'Large', true, 85, 50),
('Staten Island Realty', 'Ferry Residences', 'Cat', 'Small', true, 30, 20),
('Staten Island Realty', 'Ferry Residences', 'Cat', 'Medium', true, 50, 30),
('Staten Island Realty', 'Ferry Residences', 'Cat', 'Large', true, 75, 40),
('Staten Island Realty', 'Ferry Residences', 'Bird', 'Small', true, 20, 10),
('Staten Island Realty', 'Ferry Residences', 'Bird', 'Medium', true, 40, 20),
('Staten Island Realty', 'Ferry Residences', 'Bird', 'Large', true, 65, 30);
SELECT * FROM PetPolicy;

CREATE TABLE Amenities(
    aType VARCHAR(50) NOT NULL,
    Description VARCHAR(100) NOT NULL,
    PRIMARY KEY (aType)
);
INSERT INTO Amenities (aType, Description) VALUES
('Indoor Swimming Pool', 'Indoor pool for residents'),
('Rooftop Swimming Pool', 'Rooftop pool for residents'),
('Gym', 'Fully equipped gym'),
('Parking', 'Basement parking garage available for residents'),
('Laundry', 'Laundry room for residents'),
('Playground', 'Outdoor playground area'),
('Community Center', 'Community center for small events, TV, and board games'),
('Security', '24/7 security surveillance and key access required'),
('Mailroom', 'Mailroom to pickup large packages'),
('BBQ Area', 'Outdoor barbecue area'),
('Elevators', 'Elevators to access resident floors'),
('Rooftop Deck', 'Rooftop deck with views of the city'),
('Oven', 'Full-size in-unit oven'),
('Dishwasher', 'In-unit built-in dishwasher'),
('Washer', 'In-unit washer'),
('Dryer', 'In-unit dryer'),
('Microwave', 'In-unit microwave'),
('Refrigerator', 'Full-size in-unit refrigerator'),
('Air Conditioning', 'In-unit central air conditioning'),
('Balcony', 'Private unit balcony'),
('Fireplace', 'In-unit fireplace');
SELECT * FROM Amenities;

CREATE TABLE Interests(
    username VARCHAR(50) NOT NULL,
    UnitRentID INT NOT NULL,
    RoommateCnt TINYINT NOT NULL,
    MoveInDate date NOT NULL,
    FOREIGN KEY (username) REFERENCES Users (username),
    FOREIGN KEY (UnitRentID) REFERENCES ApartmentUnit (UnitRentID),
    PRIMARY KEY (username, UnitRentID)
);
INSERT INTO Interests (username, UnitRentID, RoommateCnt, MoveInDate) VALUES
('CLee', 1, 1, '2024-02-08'),
('JKim', 2, 0, '2024-12-15'),
('JStone', 3, 2, '2024-11-20'),
('MSmith', 4, 1, '2024-06-11'),
('RJane', 5, 4, '2024-08-05');
SELECT * FROM Interests;

CREATE TABLE AmenitiesIn(
    aType VARCHAR(20) NOT NULL,
    UnitRentID INT NOT NULL,
    FOREIGN KEY (aType) REFERENCES Amenities (aType),
    FOREIGN KEY (UnitRentID) REFERENCES ApartmentUnit (UnitRentID),
    PRIMARY KEY (aType, UnitRentID)
);
INSERT INTO AmenitiesIn (aType, UnitRentID) VALUES
('Oven', 1),
('Dishwasher', 1),
('Washer', 1),
('Dryer', 1),
('Air Conditioning', 1),
('Balcony', 1),

('Oven', 2),
('Microwave', 2),
('Refrigerator', 2),
('Air Conditioning', 2),
('Balcony', 2),

('Oven', 3),
('Dishwasher', 3),
('Washer', 3),
('Dryer', 3),
('Air Conditioning', 3),
('Refrigerator', 3),
('Fireplace', 3),

('Oven', 4),
('Dishwasher', 4),
('Washer', 4),
('Dryer', 4),
('Air Conditioning', 4),
('Refrigerator', 4),
('Fireplace', 4),

('Oven', 5),
('Dishwasher', 5),
('Air Conditioning', 5),
('Balcony', 5),

('Oven', 6),
('Dishwasher', 6),
('Air Conditioning', 6),
('Balcony', 6);
SELECT * FROM AmenitiesIn;


CREATE TABLE Provides(
    aType VARCHAR(50) NOT NULL,
    CompanyName VARCHAR(50) NOT NULL,
    BuildingName VARCHAR(50) NOT NULL,
    Fee INT NOT NULL,
    waitingList INT NOT NULL,
    FOREIGN KEY (aType) REFERENCES Amenities (aType),
    FOREIGN KEY (CompanyName,BuildingName) REFERENCES ApartmentBuilding (CompanyName,BuildingName),
    PRIMARY KEY (CompanyName,BuildingName,aType)
);
INSERT INTO Provides (aType, CompanyName, BuildingName, Fee, waitingList) VALUES
('Indoor Swimming Pool', 'Queens Apartments', 'Sky High Flushing', 50, 0),
('Rooftop Swimming Pool', 'Brooklyn Properties', 'Jay Street Apartments', 100, 0),
('Gym', 'Staten Island Realty', 'Ferry Residences', 10, 0),
('Parking', 'Queens Apartments', 'Sky High Flushing', 150, 20),
('Laundry', 'Brooklyn Properties', 'Jay Street Apartments', 0, 0),
('Playground', 'Staten Island Realty', 'Ferry Residences', 0, 0),
('Community Center', 'Queens Apartments', 'Sky High Flushing', 0, 0),
('Security', 'Brooklyn Properties', 'Jay Street Apartments', 0, 0),
('Mailroom', 'Staten Island Realty', 'Ferry Residences', 0, 0),
('BBQ Area', 'Queens Apartments', 'Sky High Flushing', 0, 0),
('Elevators', 'Brooklyn Properties', 'Jay Street Apartments', 0, 0),
('Rooftop Deck', 'Staten Island Realty', 'Ferry Residences', 0, 0);
SELECT * FROM Provides;