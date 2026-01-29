USE SinemaOtomasyonu;
GO

-- Koltuðu olmayan tüm salonlarý bul ve döngüye sok
DECLARE @SalonID INT;
DECLARE SalonCursor CURSOR FOR 
    SELECT SalonID FROM Salon WHERE SalonID NOT IN (SELECT DISTINCT SalonID FROM Koltuk);

OPEN SalonCursor;
FETCH NEXT FROM SalonCursor INTO @SalonID;

WHILE @@FETCH_STATUS = 0
BEGIN
    -- Her bir boþ salon için koltuklarý üret
    DECLARE @Harf CHAR(1) = 'A';
    DECLARE @SiraNo INT = 1;

    WHILE @SiraNo <= 5 -- 5 Sýra
    BEGIN
        DECLARE @SutunNo INT = 1;
        WHILE @SutunNo <= 10 -- 10 Sütun
        BEGIN
            INSERT INTO Koltuk (SalonID, Sira, Numara) 
            VALUES (@SalonID, @Harf, @SutunNo);
            
            SET @SutunNo = @SutunNo + 1;
        END
        SET @Harf = CHAR(ASCII(@Harf) + 1);
        SET @SiraNo = @SiraNo + 1;
    END

    FETCH NEXT FROM SalonCursor INTO @SalonID;
END

CLOSE SalonCursor;
DEALLOCATE SalonCursor;
GO