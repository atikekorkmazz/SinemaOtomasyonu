USE SinemaOtomasyonu;
GO

-- Eðer daha önce yanlýþ ekleme yaptýysan temizlemek için (Opsiyonel):
-- DELETE FROM Koltuk WHERE SalonID = 1;

DECLARE @Harf CHAR(1) = 'A'
DECLARE @SiraNo INT = 1
DECLARE @SutunNo INT = 1

WHILE @SiraNo <= 5 -- 5 sýra (A, B, C, D, E)
BEGIN
    SET @SutunNo = 1                                            
    WHILE @SutunNo <= 10 -- Her sýrada 10 koltuk
    BEGIN
        INSERT INTO Koltuk (SalonID, Sira, Numara) 
        VALUES (1, @Harf, @SutunNo);
        
        SET @SutunNo = @SutunNo + 1
    END
    SET @Harf = CHAR(ASCII(@Harf) + 1)
    SET @SiraNo = @SiraNo + 1
END
GO