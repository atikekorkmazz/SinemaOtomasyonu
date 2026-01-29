USE SinemaOtomasyonu;
GO

--SP3: Belirli bir filmin toplam hasilatini hesaplama
CREATE PROCEDURE sp_FilmHasilatiniHesapla (
	@FilmID INT,
	@ToplamHasýlat DECIMAL(10,2) OUTPUT
)
AS
BEGIN
	SET NOCOUNT ON;

	SELECT
		@ToplamHasýlat=SUM(S.Fiyat)
	FROM 
		Bilet B
	INNER JOIN
		Seans S ON B.SeansID=S.SeansID
	WHERE
		S.FilmID=@FilmID;

	--Eger sonuc NULL ise (henuz satis yoksa) sifir yap
	SET @ToplamHasýlat=ISNULL(@ToplamHasýlat,0.00);
END 
GO
