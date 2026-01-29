USE SinemaOtomasyonu;
GO

-- 2A: FILM TABLOSU
CREATE TABLE Film (
    FilmID INT PRIMARY KEY IDENTITY(1,1),
    Ad NVARCHAR(100) NOT NULL,
    Tur NVARCHAR(50),
    Sure INT, 
    Aciklama NVARCHAR(MAX),
    VizyonTarihi DATE
);
GO

-- 2B: SALON TABLOSU
CREATE TABLE Salon (
    SalonID INT PRIMARY KEY IDENTITY(1,1),
    Ad NVARCHAR(50) NOT NULL UNIQUE,
    Kapasite INT NOT NULL
);
GO

-- 2C: KULLANICI TABLOSU
CREATE TABLE Kullanici (
    KullaniciID INT PRIMARY KEY IDENTITY(1,1),
    Ad NVARCHAR(50) NOT NULL,
    Soyad NVARCHAR(50) NOT NULL,
    Eposta NVARCHAR(100) UNIQUE,
    Rol NVARCHAR(10) DEFAULT 'Musteri' 
);
GO

-- 2D: KOLTUK TABLOSU (Salon FK içerir)
CREATE TABLE Koltuk (
    KoltukID INT PRIMARY KEY IDENTITY(1,1),
    SalonID INT NOT NULL,
    Sira NVARCHAR(2) NOT NULL,
    Numara INT NOT NULL,
    
    FOREIGN KEY (SalonID) REFERENCES Salon(SalonID),
    UNIQUE (SalonID, Sira, Numara) 
);
GO

-- 2E: SEANS TABLOSU (Film ve Salon FK içerir)
CREATE TABLE Seans (
    SeansID INT PRIMARY KEY IDENTITY(1,1),
    FilmID INT NOT NULL,
    SalonID INT NOT NULL,
    Tarih DATE NOT NULL,
    Saat TIME NOT NULL,
    Fiyat DECIMAL(5, 2) NOT NULL,
    
    FOREIGN KEY (FilmID) REFERENCES Film(FilmID),
    FOREIGN KEY (SalonID) REFERENCES Salon(SalonID),
    
    UNIQUE (SalonID, Tarih, Saat)
);
GO

-- 2F: BILET TABLOSU (Seans, Koltuk, Kullanici FK içerir)
CREATE TABLE Bilet (
    BiletID INT PRIMARY KEY IDENTITY(1,1),
    SeansID INT NOT NULL,
    KoltukID INT NOT NULL,
    KullaniciID INT, 
    SatisZamani DATETIME DEFAULT GETDATE(),
    
    FOREIGN KEY (SeansID) REFERENCES Seans(SeansID),
    FOREIGN KEY (KoltukID) REFERENCES Koltuk(KoltukID),
    FOREIGN KEY (KullaniciID) REFERENCES Kullanici(KullaniciID),
    
    UNIQUE (SeansID, KoltukID) 
);
GO