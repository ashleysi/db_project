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