USE SinemaOtomasyonu;
GO

-- Film tablosuna Afiþ sütunu ekle
ALTER TABLE Film ADD PosterPath NVARCHAR(MAX); 
GO

-- Seans tablosuna Dil sütunu ekle
ALTER TABLE Seans ADD Dil NVARCHAR(20) DEFAULT 'Dublaj';
GO