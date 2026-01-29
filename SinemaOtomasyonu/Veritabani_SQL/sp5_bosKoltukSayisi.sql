USE SinemaOtomasyonu
GO

--SP5: Belirli bir seans icin bos koltuk sayisini hesaplar
CREATE PROCEDURE sp_SeansKapasiteKontrolu (
	@SenasID INT,
	@BosKoltukSayisi INT OUTPUT
)
AS
BEGIN
	SET NOCOUNT ON;

	DECLARE @ToplamKapasite INT;
	DECLARE @SatilanBiletSayisi INT;

	--1. ADIM: Seansin yapildigi salonun toplam kapasitesini bul
	SELECT
		@ToplamKapasite=Sln.Kapasite
	FROM
		Seans S
	INNER JOIN
		Salon Sln ON S.SalonID=Sln.SalonID
	WHERE
		S.SeansID=@SenasID;

	--2.ADIM: Bu seans icin satilan bilet sayisini bul
	SELECT
		@SatilanBiletSayisi=COUNT(BiletID)
	FROM
		Bilet
	WHERE
		SeansID=@SenasID;

	--3.ADIM: Bos koltuk sayisini hesapla
	SET @BosKoltukSayisi=@ToplamKapasite - @SatilanBiletSayisi;

	--Eger kapasite bulunamazsa veya seans yoksa 0 dondorme
	SET @BosKoltukSayisi=ISNULL(@BosKoltukSayisi,0);
END
GO