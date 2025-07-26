# Keycard Booking System

## Technologies
Python: FastAPI
MySQL


## Database Structure

### 3 tables:
- Users
- Items
- Reservation system

#### Users:

CREATE TABLE Users (
    UserID VARCHAR(50) PRIMARY KEY,
    EmailAddress VARCHAR(100) UNIQUE NOT NULL,
    CreationDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


#### Items:

CREATE TABLE Items (
    ItemID INT PRIMARY KEY AUTO_INCREMENT, -- En unik, automatisk ID for hver gjenstand
    ItemType VARCHAR(100) NOT NULL,        -- F.eks. "Romnøkkel", "Bilnøkkel", " "Låseskapnøkkel"
    Description TEXT,                      -- Valgfri lengre beskrivelse av gjenstanden
    Status VARCHAR(50) DEFAULT 'Available' -- F.eks. 'Available', 'In Use', 'Maintenance', 'Lost'
);


#### Reservations:

CREATE TABLE Reservations (
    ReservationID INT PRIMARY KEY AUTO_INCREMENT,
    ItemID INT NOT NULL,                 -- Hvilken gjenstand som er reservert (Fremmednøkkel til Items)
    UserID VARCHAR(50) NOT NULL,         -- Hvem som har reservert gjenstanden (Fremmednøkkel til Users)
    ReservationStartTime DATETIME NOT NULL,
    ReservationEndTime DATETIME NOT NULL,
    IsActive BOOLEAN NOT NULL DEFAULT TRUE, -- TRUE hvis reservasjonen er aktiv, FALSE hvis avsluttet/kansellert
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ItemID) REFERENCES Items(ItemID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    CONSTRAINT CHK_ReservationTime CHECK (ReservationEndTime > ReservationStartTime)
);