USE SinemaOtomasyonu
GO

--SP2: Belirli bir tarihteki tüm aktif seanslarý ve salon adýyla birlikte getirme
CREATE PROCEDURE sp_AktifSeanslarGetir (
	@Tarih DATE
)
AS
BEGIN
	SET NOCOUNT ON;

	SELECT
		S.SeansID,
		F.Ad AS FilmAdi,
		L.Ad AS SalonAdi,
		S.Tarih,
		S.Saat,
		S.Fiyat
	FROM
		Seans S
	INNER JOIN
		Film F ON S.FilmID=F.FilmID
	INNER JOIN
		Salon L ON S.SalonID=L.SalonID
	WHERE
		S.Tarih=@Tarih
	ORDER BY
		S.Saat;
END 
GO