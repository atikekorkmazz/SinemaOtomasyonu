# sinema_proje/urls.py (Ana Dağıtıcı)

from django.contrib import admin
from django.urls import path, include # 'include' eklediğimizden emin olalım

urlpatterns = [
    path('admin/', admin.site.urls), # Django'nun hazır admin paneli [cite: 7]
    path('', include('sinema_app.urls')), # Tüm boş (ana dizin) istekleri uygulamaya gönder
]