
-----

# Keycard Booking System

Et enkelt API for å administrere brukere, utstyr og reservasjoner.

## Teknologier

  - **Backend:** Python med [FastAPI](https://fastapi.tiangolo.com/)
  - **Database:** MySQL

-----

## Databasestruktur

Systemet består av tre hovedtabeller: **Users**, **Items** og **Reservations**. Nedenfor er en detaljert beskrivelse av hver tabell og dens kolonner.

### 1\. Users

Denne tabellen lagrer informasjon om brukerne som kan booke utstyr.

| Kolonnenavn | Datatype | Beskrivelse |
| :--- | :--- | :--- |
| `UserID` | VARCHAR(50) | **Primary Key.** En unik identifikator for brukeren. |
| `EmailAddress`| VARCHAR(100) | Brukerens e-postadresse. Må være unik. |
| `CreationDate`| TIMESTAMP | Tidsstempel for når brukeren ble opprettet. |



```sql
CREATE TABLE Users (
    UserID VARCHAR(50) PRIMARY KEY,
    EmailAddress VARCHAR(100) UNIQUE NOT NULL,
    CreationDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```



-----

### 2\. Items

Denne tabellen inneholder en oversikt over alt utstyr som kan reserveres.

| Kolonnenavn | Datatype | Beskrivelse |
| :--- | :--- | :--- |
| `ItemID` | INT | **Primary Key.** En unik ID for gjenstanden. |
| `ItemType` | VARCHAR(100) | Type gjenstand (f.eks. "Projektor", "Webkamera"). |
| `Description` | TEXT | En valgfri, mer detaljert beskrivelse av gjenstanden. |
| `Status` | BOOLEAN | **`1` (true)** for tilgjengelig, **`0` (false)** for utilgjengelig. Standard er `1`.|



```sql
CREATE TABLE Items (
    ItemID INT PRIMARY KEY AUTO_INCREMENT,
    ItemType VARCHAR(100) NOT NULL,
    Description TEXT,
    Status BOOLEAN DEFAULT 1
);
```



-----

### 3\. Reservations

Denne tabellen kobler brukere og gjenstander sammen for å lage en reservasjon.

| Kolonnenavn | Datatype | Beskrivelse |
| :--- | :--- | :--- |
| `ReservationID` | INT | **Primary Key.** En unik ID for reservasjonen. |
| `ItemID` | INT | **Foreign Key.** Peker til `ItemID` i `Items`-tabellen. |
| `UserID` | VARCHAR(50) | **Foreign Key.** Peker til `UserID` i `Users`-tabellen. |
| `ReservationStartTime` | DATETIME | Starttidspunkt for reservasjonen. |
| `ReservationEndTime` | DATETIME | Sluttidspunkt for reservasjonen. Må være etter starttid. |
| `IsActive` | BOOLEAN | Om reservasjonen er aktiv eller kansellert. Standard er `1` (true). |
| `CreatedAt` | TIMESTAMP | Tidsstempel for når reservasjonen ble opprettet. |



```sql
CREATE TABLE Reservations (
    ReservationID INT PRIMARY KEY AUTO_INCREMENT,
    ItemID INT NOT NULL,
    UserID VARCHAR(50) NOT NULL,
    ReservationStartTime DATETIME NOT NULL,
    ReservationEndTime DATETIME NOT NULL,
    IsActive BOOLEAN NOT NULL DEFAULT TRUE,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ItemID) REFERENCES Items(ItemID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    CONSTRAINT CHK_ReservationTime CHECK (ReservationEndTime > ReservationStartTime)
);
```