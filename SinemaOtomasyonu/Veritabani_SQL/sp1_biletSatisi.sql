USE SinemaOtomasyonu
GO

--SP1: Yeni Bilet Satisi Gerceklestirme
CREATE PROCEDURE sp_BiletSatisi (
	@SeansID INT,
	@KoltukID INT,
	@KullaniciID INT =NULL, --misafir bilet alabilir
	@Sonuc NVARCHAR(100) OUTPUT
)
AS
BEGIN
	--1.ADIM: Ayný seansta bu koltuðun satýlýp satýlmadýðýný kontrol et
	IF EXISTS (
		SELECT 1
		FROM Bilet
		WHERE SeansID = @SeansID AND KoltukID = @KoltukID
	)
	BEGIN
		SET @Sonuc='HATA: Bu koltuk zaten satýlmýþtýr.';
		RETURN;
	END

	--2.ADIM: Satisi gerceklestir
	INSERT INTO Bilet (SeansID, KoltukID,KullaniciID)
	VALUES (@SeansID,@KoltukID,@KullaniciID);

	SET @Sonuc='BAÞARILI: Bilet satýþý tamamlandý.';
END 
GO


