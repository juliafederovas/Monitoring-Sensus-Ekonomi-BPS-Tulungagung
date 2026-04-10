from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from progres.models import Petugas, ProgresHarian, Kendala
from wilayah.models import Wilayah
from sensus.models import SensusEkonomi

def redirect_dashboard(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard_admin')
        return redirect('dashboard_petugas')
    return redirect('login')

@login_required
def dashboard_admin(request):
    from wilayah.models import Wilayah
    from sensus.models import SensusEkonomi
    from django.db.models import Sum

    total_wilayah = Wilayah.objects.count()
    total_petugas = Petugas.objects.filter(status_aktif=True).count()
    total_laporan = ProgresHarian.objects.count()
    total_kendala = Kendala.objects.count()
    laporan_terbaru = ProgresHarian.objects.order_by('-created_at')[:5]
    kendala_terbaru = Kendala.objects.order_by('-created_at')[:5]

    # Data untuk grafik progres per wilayah
    wilayah_list = Wilayah.objects.all()
    grafik_labels = []
    grafik_selesai = []
    grafik_target = []
    grafik_bermasalah = []

    for w in wilayah_list:
        total_selesai = ProgresHarian.objects.filter(
            wilayah=w
        ).aggregate(Sum('jumlah_selesai'))['jumlah_selesai__sum'] or 0

        total_bermasalah = ProgresHarian.objects.filter(
            wilayah=w
        ).aggregate(Sum('jumlah_bermasalah'))['jumlah_bermasalah__sum'] or 0

        grafik_labels.append(f"{w.nama_kecamatan}-{w.nama_kelurahan}")
        grafik_selesai.append(total_selesai)
        grafik_target.append(w.target_usaha)
        grafik_bermasalah.append(total_bermasalah)

    # Data untuk grafik jenis kendala
    kendala_labels = []
    kendala_data = []
    jenis_list = [
        ('tidak_ditemukan', 'Tidak Ditemukan'),
        ('menolak', 'Pemilik Menolak'),
        ('alamat_salah', 'Alamat Salah'),
        ('tutup', 'Usaha Tutup'),
        ('akses_jalan', 'Akses Jalan'),
        ('cuaca', 'Cuaca'),
        ('lainnya', 'Lainnya'),
    ]
    for kode, label in jenis_list:
        jumlah = Kendala.objects.filter(jenis_kendala=kode).count()
        if jumlah > 0:
            kendala_labels.append(label)
            kendala_data.append(jumlah)

    # Progres bar per wilayah
    progres_wilayah = []
    for i, w in enumerate(wilayah_list):
        target = grafik_target[i]
        selesai = grafik_selesai[i]
        persen = round((selesai / target * 100), 1) if target > 0 else 0
        progres_wilayah.append({
            'label': grafik_labels[i],
            'selesai': selesai,
            'target': target,
            'persen': persen,
        })

    context = {
        'total_wilayah': total_wilayah,
        'total_petugas': total_petugas,
        'total_laporan': total_laporan,
        'total_kendala': total_kendala,
        'laporan_terbaru': laporan_terbaru,
        'kendala_terbaru': kendala_terbaru,
        'grafik_labels': grafik_labels,
        'grafik_selesai': grafik_selesai,
        'grafik_target': grafik_target,
        'grafik_bermasalah': grafik_bermasalah,
        'kendala_labels': kendala_labels,
        'kendala_data': kendala_data,
        'progres_wilayah': progres_wilayah,
        'wilayah_range': range(len(grafik_labels)),
    }
    return render(request, 'dashboard/admin.html', context)

@login_required
def dashboard_petugas(request):
    try:
        petugas = Petugas.objects.get(user=request.user)
        laporan = ProgresHarian.objects.filter(petugas=petugas).order_by('-tanggal_laporan')[:7]
        total_selesai = sum([l.jumlah_selesai for l in laporan])
        total_bermasalah = sum([l.jumlah_bermasalah for l in laporan])
    except Petugas.DoesNotExist:
        laporan = []
        total_selesai = 0
        total_bermasalah = 0
    context = {
        'laporan': laporan,
        'total_selesai': total_selesai,
        'total_bermasalah': total_bermasalah,
    }
    return render(request, 'dashboard/petugas.html', context)

@login_required
def daftar_wilayah(request):
    wilayah = Wilayah.objects.all()
    return render(request, 'dashboard/wilayah.html', {'wilayah': wilayah})

@login_required
def daftar_petugas(request):
    petugas = Petugas.objects.all()
    return render(request, 'dashboard/petugas_list.html', {'petugas': petugas})

@login_required
def validasi_laporan(request):
    if request.method == 'POST':
        laporan_id = request.POST.get('laporan_id')
        aksi = request.POST.get('aksi')
        try:
            laporan = ProgresHarian.objects.get(id=laporan_id)
            if aksi == 'approve':
                laporan.status_validasi = 'disetujui'
                laporan.validator = request.user
                laporan.save()
                messages.success(request, f'Laporan {laporan.petugas.nama} berhasil disetujui!')
            elif aksi == 'reject':
                laporan.status_validasi = 'ditolak'
                laporan.validator = request.user
                laporan.save()
                messages.warning(request, f'Laporan {laporan.petugas.nama} ditolak!')
        except Exception as e:
            messages.error(request, f'Gagal memproses validasi: {e}')
        return redirect('validasi_laporan')

    laporan_menunggu = ProgresHarian.objects.filter(
        status_validasi='menunggu'
    ).order_by('-created_at')

    laporan_selesai = ProgresHarian.objects.filter(
        status_validasi__in=['disetujui', 'ditolak']
    ).order_by('-updated_at')[:10]

    context = {
        'laporan_menunggu': laporan_menunggu,
        'laporan_selesai': laporan_selesai,
    }
    return render(request, 'dashboard/validasi.html', context)

@login_required
def analisis_kendala(request):
    kendala = Kendala.objects.all().order_by('-created_at')
    return render(request, 'dashboard/kendala.html', {'kendala': kendala})

@login_required
def input_laporan(request):
    from wilayah.models import Wilayah
    if request.method == 'POST':
        try:
            petugas = Petugas.objects.get(user=request.user)
            wilayah = Wilayah.objects.get(id=request.POST['wilayah'])

            # Simpan progres harian
            progres = ProgresHarian.objects.create(
                petugas=petugas,
                wilayah=wilayah,
                tanggal_laporan=request.POST['tanggal_laporan'],
                jumlah_selesai=request.POST['jumlah_selesai'],
                jumlah_bermasalah=request.POST['jumlah_bermasalah'],
                catatan=request.POST.get('catatan', ''),
            )

            # Simpan kendala kalau ada
            jenis_list = request.POST.getlist('jenis_kendala[]')
            deskripsi_list = request.POST.getlist('deskripsi_kendala[]')

            for i, jenis in enumerate(jenis_list):
                deskripsi = deskripsi_list[i] if i < len(deskripsi_list) else ''
                if jenis and deskripsi:
                    Kendala.objects.create(
                        progres=progres,
                        jenis_kendala=jenis,
                        deskripsi=deskripsi,
                    )

            messages.success(request, 'Laporan dan kendala berhasil disimpan!')
            return redirect('dashboard_petugas')

        except Exception as e:
            messages.error(request, f'Gagal menyimpan laporan: {e}')

    wilayah_list = Wilayah.objects.all()
    return render(request, 'dashboard/input_laporan.html', {'wilayah_list': wilayah_list})

@login_required
def riwayat_laporan(request):
    try:
        petugas = Petugas.objects.get(user=request.user)
        laporan = ProgresHarian.objects.filter(petugas=petugas).order_by('-tanggal_laporan')
    except Petugas.DoesNotExist:
        laporan = []
    return render(request, 'dashboard/riwayat.html', {'laporan': laporan})