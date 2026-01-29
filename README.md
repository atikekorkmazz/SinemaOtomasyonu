# Sinema Otomasyonu Web Uygulaması
**Veri Tabanı Yönetim Sistemleri Dersi Projesi**

Bu proje, bir sinema işletmesinin temel operasyonlarını web tabanlı olarak
yönetmesini sağlayan bir **sinema otomasyonu sistemidir**. Film listeleme,
seans seçimi, koltuk takibi ve bilet satış işlemleri gerçekleştirilebilmektedir.

---

## 1️ Proje Hakkında

Bu proje, Veri Tabanı Yönetim Sistemleri dersinde öğrenilen;

- İlişkisel veritabanı tasarımı  
- Stored Procedure  
- Trigger  
- Function  
- View  

kavramlarının **gerçek bir senaryo** üzerinde uygulanmasını amaçlamaktadır.

Uygulama backend tarafında **Python tabanlı Django framework’ü**, veritabanı
tarafında ise **Microsoft SQL Server** kullanılarak geliştirilmiştir.

---

## 2️ Sistem Gereksinimleri

Projeyi çalıştırabilmek için aşağıdaki yazılımlar gereklidir:

- Python **3.10** veya üzeri  
- Microsoft SQL Server **2019** veya üzeri  
- pip (Python paket yöneticisi)

Kullanılan veritabanı ve bağlantı kütüphaneleri:

- `pyodbc`
- `django-mssql-backend`

---

## 3️ Proje Klasör Yapısı

SinemaOtomasyonu/
├── SinemaOtomasyonu_VeriTabani.sql
├── docs/
├── SinemaOtomasyonu/
│ ├── manage.py
│ ├── sinema_proje/
│ │ ├── settings.py
│ │ ├── urls.py
│ │ └── ...
│ ├── sinema_app/
│ ├── templates/
│ │ ├── sinema_app/
│ │ │ ├── gise.html
│ │ │ ├── index.html
│ │ │ └── ...
│ │ └── admin/
│ ├── models.py
│ ├── views.py
│ └── ...
└── Veritabani_SQL/

`Veritabani_SQL` klasörü içerisinde:

- Tablolar  
- Stored Procedure’ler  
- Trigger’lar  
- Function ve View tanımları  

bulunmaktadır.

---

## 4️ Veritabanı Kurulumu

1. Microsoft SQL Server üzerinde yeni bir veritabanı oluşturulur.
2. `Veritabani_SQL` klasörü içerisindeki SQL dosyaları aşağıdaki sırayla çalıştırılır:
   - Tabloların oluşturulması  
   - Stored Procedure’lerin oluşturulması  
   - Function ve View’ların oluşturulması  
   - Trigger’ların oluşturulması  
3. Tüm SQL komutlarının hatasız çalıştığından emin olunmalıdır.

---

## 5️ Uygulama Ayarları

Django ayarları `settings.py` dosyası içerisinde bulunmaktadır.

Veritabanı bağlantısı için aşağıdaki bilgiler tanımlanmalıdır:

- Veritabanı adı  
- Sunucu adı  
- Kullanıcı adı  
- Şifre  
- ODBC Driver bilgisi  

Bağlantı işlemleri `pyodbc` ve `django-mssql-backend` kullanılarak
gerçekleştirilmektedir.

---

## 6️ Uygulamanın Çalıştırılması

Terminal veya Komut İstemi açılır ve aşağıdaki adımlar izlenir:

```bash
cd proje_klasoru_adi
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver

Uygulamaya tarayıcı üzerinden erişilir:

http://127.0.0.1:8000/
