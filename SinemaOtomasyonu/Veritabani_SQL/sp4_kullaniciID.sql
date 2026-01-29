USE SinemaOtomasyonu
GO

--SP4: Belirli bir kullanýcýnýn aldýðý tüm biletleri detaylý listeleme
CREATE PROCEDURE sp_KullaniciBiletleriniListele (
	@KullaniciID INT
)
AS
BEGIN
	SET NOCOUNT ON;

	SELECT
		B.BiletID,
		F.Ad AS FilmAdi,
		L.Ad AS SalonAdi,
		S.Tarih AS SeansTarihi,
		S.Saat AS SeansSaati,
		Klt.Sira +CAST(Klt.Numara AS NVARCHAR(5)) AS Koltuk,
		S.Fiyat,
		B.SatisZamani
	FROM
		Bilet B
	INNER JOIN
		Seans S ON B.SeansID=S.SeansID
	INNER JOIN
		Film F ON S.FilmID=F.FilmID
	INNER JOIN
		Salon L ON S.SalonID=L.SalonID
	INNER JOIN
		Koltuk Klt ON B.KoltukID=Klt.KoltukID
	WHERE
		B.KullaniciID=@KullaniciID
	ORDER BY
		B.SatisZamani DESC;
END 
GO