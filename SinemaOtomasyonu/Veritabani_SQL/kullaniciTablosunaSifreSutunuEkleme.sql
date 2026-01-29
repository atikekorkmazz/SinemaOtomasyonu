USE SinemaOtomasyonu;
GO

-- Eðer yoksa Sifre sütununu ekle
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('Kullanici') AND name = 'Sifre')
BEGIN
    ALTER TABLE Kullanici ADD Sifre NVARCHAR(100);
END
GO