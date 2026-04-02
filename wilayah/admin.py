from django.contrib import admin
from .models import Wilayah

@admin.register(Wilayah)
class WilayahAdmin(admin.ModelAdmin):
    list_display = ['kode_wilayah', 'nama_kecamatan', 'nama_kelurahan', 'target_usaha']
    search_fields = ['kode_wilayah', 'nama_kecamatan', 'nama_kelurahan']