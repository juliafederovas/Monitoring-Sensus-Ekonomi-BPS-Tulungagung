from django.urls import path
from . import views

urlpatterns = [
    path('', views.redirect_dashboard, name='home'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/petugas/', views.dashboard_petugas, name='dashboard_petugas'),
    path('wilayah/', views.daftar_wilayah, name='daftar_wilayah'),
    path('petugas/', views.daftar_petugas, name='daftar_petugas'),
    path('validasi/', views.validasi_laporan, name='validasi_laporan'),
    path('kendala/', views.analisis_kendala, name='analisis_kendala'),
    path('laporan/input/', views.input_laporan, name='input_laporan'),
    path('laporan/riwayat/', views.riwayat_laporan, name='riwayat_laporan'),
]