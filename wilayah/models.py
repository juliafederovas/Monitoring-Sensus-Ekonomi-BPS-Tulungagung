from django.db import models
import uuid

class Wilayah(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kode_wilayah = models.CharField(max_length=20, unique=True)
    nama_kecamatan = models.CharField(max_length=100)
    nama_kelurahan = models.CharField(max_length=100)
    target_usaha = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nama_kecamatan} - {self.nama_kelurahan}"

    class Meta:
        verbose_name = 'Wilayah'
        verbose_name_plural = 'Data Wilayah'