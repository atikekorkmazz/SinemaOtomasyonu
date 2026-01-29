USE SinemaOtomasyonu;
GO

----------FONKSÝYONLAR

--FN1: Vizyon süresi hesaplama (kac gun kaldý-gecti)
CREATE FUNCTION fn_VizyonSuresiHesapla (@VizyonTarihi DATE)
RETURNS INT 
AS 
BEGIN
	DECLARE @GunSayisi INT;
	--bugunun tarihi ile vizyon tarihi arasindaki farki gün olarak hesaplar
	SELECT @GunSayisi = DATEDIFF(day, GETDATE(), @VizyonTarihi);
	RETURN @GunSayisi;
END 
GO

--FN2: Kullanici adi ve soyadini birleþtirme
CREATE FUNCTION fn_TamAdiGetir (@KullaniciID INT)
RETURNS NVARCHAR(101)
AS
BEGIN
	DECLARE @TamAd NVARCHAR(101);
	SELECT @TamAd =K.Ad + ' ' + K.Soyad
	FROM Kullanici K
	WHERE K.KullaniciID=@KullaniciID;
	RETURN @TamAd;
END
GO

--FN3: Bos koltuklarin toplam fiyatini hesaplama(potansiyel gelir)
CREATE FUNCTION fn_PotansiyelGelirHesapla (@SeansID INT)
RETURNS DECIMAL (10,2)
AS
BEGIN
	DECLARE @BosKoltukSayisi INT;
	DECLARE @SeansFiyati DECIMAL(5,2);
	DECLARE @PotansiyelGelir DECIMAL(10,2);

	--TRG1 ile oluþturulan SeansSatisLog tablosundan yararlanilir
	SELECT 
		@SeansFiyati = S.Fiyat,
		@BosKoltukSayisi = (Sln.Kapasite - ISNULL(T.SatilanAdet,0))
	FROM Seans S
	INNER JOIN Salon Sln ON S.SalonID=Sln.SalonID
	LEFT JOIN SeansSatisLog T ON S.SeansID=T.SeansID
	WHERE S.SeansID=@SeansID;

	SET @PotansiyelGelir=@BosKoltukSayisi * @SeansFiyati;
	RETURN ISNULL(@PotansiyelGelir, 0.00);
END 
GO



--------------------------------VIEW
--VIEW1: Aktif seans detaylarini ve kalan koltuk sayisini gosterme
CREATE VIEW vw_AktifSeansDetaylari 
AS
SELECT
	S.SeansID,
	F.Ad AS FilmAdi,
	Sln.Ad AS SalonAdi,
	S.Tarih,
	S.Saat,
	S.Fiyat,
	(Sln.Kapasite - ISNULL(T.SatilanAdet, 0)) AS KalanKoltukSayisi
FROM
	Seans S
INNER JOIN
	Film F ON S.FilmID=F.FilmID
INNER JOIN
	Salon Sln ON S.SalonID=Sln.SalonID
LEFT JOIN
	SeansSatisLog T ON S.SeansID = T.SeansID
WHERE
	S.Tarih >= GETDATE();   --sadece bugunun seanslarini gosterir
GO