USE SinemaOtomasyonu
GO

--1.LOG TABLOSU:Satis logu
CREATE TABLE SeansSatisLog (
	LogID INT PRIMARY KEY IDENTITY(1,1),
	SeansID INT NOT NULL UNIQUE,
	SatilanAdet INT DEFAULT 0,
	FOREIGN KEY (SeansID) REFERENCES Seans(SeansID)
);
GO
--TRG1: Bilet satisi sonrasi satis adedi loglama(INSERT)
CREATE TRIGGER trg_BiletSatisiSonrasiLoglama
ON Bilet
AFTER INSERT
AS
BEGIN
	SET NOCOUNT ON;

	DECLARE @YeniSeansID INT;
	SELECT @YeniSeansID=SeansID FROM inserted;

	--Log tablosunu guncelle/ekle
	IF EXISTS (SELECT 1 FROM SeansSatisLog WHERE SeansID=@YeniSeansID)
	BEGIN
		UPDATE SeansSatisLog
		SET SatilanAdet=SatilanAdet+1
		WHERE SeansID=@YeniSeansID;
	END 
	ELSE
	BEGIN
		INSERT INTO SeansSatisLog(SeansID,SatilanAdet)
		SELECT SeansID, COUNT(*) FROM inserted GROUP BY SeansID;
	END
END 
GO

--------------------------------------------------------------------------

--2.LOG TABLOSU: Seans Arsivi
CREATE TABLE SeansArsivi (
	ArsivID INT PRIMARY KEY IDENTITY(1,1),
	SeansID INT NOT NULL,
	FilmID INT NOT NULL,
	SalonID INT NOT NULL,
	Tarih DATE NOT NULL,
	Saat TIME NOT NULL,
	Fiyat DECIMAL(5,2) NOT NULL,
	ArsivlenmeTarihi DATETIME DEFAULT GETDATE()
);
GO
--TRG2: Seans silinince arsivleme (delete)
CREATE TRIGGER trg_SeansSilininceArsivle
ON SEANS
AFTER DELETE
AS
BEGIN
	SET NOCOUNT ON;
	--silinen kayitlari (deleted tablosundan) arsiv tablosuna ekel
	INSERT INTO SeansArsivi (SeansID,FilmID,SalonID,Tarih,Saat,Fiyat)
	SELECT
		d.SeansID, d.FilmID, d.SalonID, d.Tarih, d.Saat, d.Fiyat
	FROM deleted d;
END
GO

--------------------------------------------------------------------------

--3.LOG TABLOSU: Fiyat degisikligi logu
CREATE TABLE SeansFiyatLog (
	LogID INT PRIMARY KEY IDENTITY(1,1),
	SeansID INT NOT NULL,
	EskiFiyat DECIMAL(5,2),
	YeniFiyat DECIMAL(5,2),
	DegisiklikTarihi DATETIME DEFAULT GETDATE()
);
GO
--TRG3: Seans fiyati guncelleme denetimi
CREATE TRIGGER trg_SeansFiyatiGuncelleme
ON SEANS 
AFTER UPDATE
AS
BEGIN
	SET NOCOUNT ON;
	--Fiyat sutunu degistiyse
	IF UPDATE(Fiyat)
	BEGIN
		INSERT INTO SeansFiyatLog (SeansID,EskiFiyat,YeniFiyat)
		SELECT
			i.SeansID,
			d.Fiyat AS EskiFiyat,
			i.Fiyat AS YeniFiyat
		FROM inserted i
		INNER JOIN deleted d ON i.SeansID=d.SeansID;
	END
END
GO

---------------------------------------------------------------------------

--4.LOG TABLOSU: Kapasite uyarisi logu
CREATE TABLE KapasiteUyariLog (
	LogID INT PRIMARY KEY IDENTITY(1,1),
	SalonID INT NOT NULL,
	EskiKapasite INT,
	YeniKapasite INT,
	UyariSeviyesi NVARCHAR(50),
	DegisiklikTarihi DATETIME DEFAULT GETDATE()
);
GO
--TRG4: Salon kapasitesi uyarisi 
CREATE TRIGGER trg_KapasiteDegisimiKontrol
ON Salon
AFTER UPDATE
AS
BEGIN
	SET NOCOUNT ON;
	--Kapasite sutunu degistiyse
	IF UPDATE(Kapasite)
	BEGIN
		INSERT INTO KapasiteUyariLog (SalonID, EskiKapasite,YeniKapasite,UyariSeviyesi)
		SELECT
			i.SalonID,
			d.Kapasite AS EskiKapasite,
			i.Kapasite AS YeniKapasite,
			CASE
				WHEN i.Kapasite<50 AND d.Kapasite>=50 THEN 'KRÝTÝK DÜÞÜÞ UYARISI'
				WHEN i.Kapasite< d.Kapasite THEN 'Kapasite Azaltýldý'
				ELSE 'Kapasite Artýrýldý'
			END
		FROM inserted i
		INNER JOIN deleted d ON i.SalonID=d.SalonID
		WHERE i.Kapasite <> d.Kapasite;
	END
END
GO