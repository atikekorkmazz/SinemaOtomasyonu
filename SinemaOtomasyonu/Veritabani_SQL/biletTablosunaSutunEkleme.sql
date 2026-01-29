USE SinemaOtomasyonu;
GO

-- Tabloya Fiyat ve BiletTipi sütunlarýný ekliyoruz
ALTER TABLE Bilet ADD Fiyat DECIMAL(10,2);
ALTER TABLE Bilet ADD BiletTipi NVARCHAR(20);
GO