USE SinemaOtomasyonu;
GO

ALTER TABLE Seans ADD Dil NVARCHAR(20) DEFAULT 'Dublaj';
GO

-- Mevcut kayýtlarý güncellemek istersen (isteðe baðlý):
UPDATE Seans SET Dil = 'Dublaj' WHERE Dil IS NULL;
GO