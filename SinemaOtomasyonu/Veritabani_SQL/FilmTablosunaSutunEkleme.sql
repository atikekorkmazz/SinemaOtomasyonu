USE SinemaOtomasyonu;
GO

-- Film tablosuna VizyonBitisTarihi sütununu ekliyoruz
ALTER TABLE Film 
ADD VizyonBitisTarihi DATE;
GO