"""
================================================================================
KELOMPOK C — SISTEM MANAJEMEN LAUNDRY
Modul: penyimpanan_riwayat.py (Fitur 5: Riwayat dan Penyimpanan Data)
================================================================================
Deskripsi:
Modul ini bertugas menangani seluruh mekanisme penyimpanan data (File I/O JSON),
pembacaan data saat aplikasi dijalankan, penampilan riwayat pesanan pelanggan,
penghitungan serta visualisasi total pendapatan laundry.

Ketentuan Materi yang diterapkan:
1. Variabel, Tipe Data, dan Operator (str, int, float, bool, operator aritmatika & logika).
2. Percabangan (if, elif, else) dan Perulangan (for, while).
3. Fungsi terstruktur dan modular.
4. Struktur Data:
   - List       : Menyimpan koleksi pesanan, pembayaran, pelanggan, dan layanan.
   - Tuple      : Menyimpan konstanta opsi menu dan label status yang immutable.
   - Set        : Menyimpan himpunan unik ID pelanggan, nomor transaksi lunas, dll.
   - Dictionary : Menyimpan detail objek transaksi, pelanggan, layanan, & ringkasan statistik.
5. Exception Handling & Penanganan I/O:
   - try-except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError).
   - Pembacaan & penyimpanan file JSON secara persisten dan aman.
   - Fitur ekspor laporan ke file teks (.txt).
6. Validasi Input agar tidak terjadi crash saat input pengguna salah.
7. Fitur CRUD: Menampilkan, Menambahkan (Backup/Catat), Mengubah, dan Menghapus riwayat.
================================================================================
"""

import json
import os
from datetime import datetime

# ==============================================================================
# 1. KONFIGURASI DIREKTORI & NAMA FILE PENYIMPANAN
# ==============================================================================
DIREKTORI_MODUL = os.path.dirname(os.path.abspath(__file__))
DIREKTORI_UTAMA = os.path.dirname(DIREKTORI_MODUL)

# Lokasi file JSON (fleksibel: memeriksa direktori Modul maupun direktori utama)
def _tentukan_path_file(nama_file_modul, nama_file_utama=None):
    if nama_file_utama is None:
        nama_file_utama = nama_file_modul
    path_di_modul = os.path.join(DIREKTORI_MODUL, nama_file_modul)
    path_di_utama = os.path.join(DIREKTORI_UTAMA, nama_file_utama)
    # Jika file sudah ada di folder utama, prioritaskan path tersebut
    if os.path.exists(path_di_utama):
        return path_di_utama
    # Jika ada di folder modul, gunakan path modul
    if os.path.exists(path_di_modul):
        return path_di_modul
    # Default lokasi simpan baru
    return path_di_modul

FILE_PELANGGAN = _tentukan_path_file("data_pelanggan.json", "data_pelanggan.json")
FILE_LAYANAN = _tentukan_path_file("layanan.json", "layanan.json")
FILE_PESANAN = _tentukan_path_file("pesanan.json", "pesanan.json")
FILE_PEMBAYARAN = _tentukan_path_file("riwayat_pembayaran.json", "riwayat_pembayaran.json")
FILE_EKSPOR_LAPORAN = os.path.join(DIREKTORI_MODUL, "laporan_pendapatan.txt")

# ==============================================================================
# 2. TUPLE KONSTANTA (Penerapan Struktur Data Tuple)
# ==============================================================================
PILIHAN_MENU_RIWAYAT = ("1", "2", "3", "4", "5", "6", "0")
STATUS_PESANAN_TUPLE = ("Diterima", "Diproses", "Selesai", "Diambil")
STATUS_BAYAR_TUPLE = ("Belum Lunas", "Lunas")
LEBAR_GARIS = 75

# Set kunci wajib untuk validasi integritas struktur data dictionary
KUNCI_WAJIB_PEMBAYARAN = {"id_pembayaran", "no_transaksi", "total_tagihan"}
KUNCI_WAJIB_PESANAN = {"berat_kg", "total"}


# ==============================================================================
# 3. FUNGSI PEMBANTU (FORMATTING & VALIDASI INPUT)
# ==============================================================================
def format_rupiah(angka):
    """Mengubah angka (int/float) menjadi string berformat rupiah (contoh: Rp 25.000)."""
    try:
        nilai = int(round(float(angka)))
        return "Rp " + f"{nilai:,}".replace(",", ".")
    except (ValueError, TypeError):
        return "Rp 0"


def cetak_garis(panjang=LEBAR_GARIS, karakter="="):
    """Mencetak garis pemisah."""
    print(karakter * panjang)


def input_teks_valid(pesan, boleh_kosong=False):
    """Meminta input teks dengan validasi tidak boleh kosong."""
    while True:
        teks = input(pesan).strip()
        if teks or boleh_kosong:
            return teks
        print("[PERINGATAN] Input tidak boleh kosong! Silakan coba lagi.")


def input_pilihan_menu(pesan, opsi_valid):
    """Validasi input menu berdasarkan koleksi opsi (Tuple/Set)."""
    while True:
        pilihan = input(pesan).strip()
        if pilihan in opsi_valid:
            return pilihan
        print(f"[PERINGATAN] Pilihan tidak valid! Masukkan salah satu dari {list(opsi_valid)}.")


def konfirmasi_tindakan(pesan):
    """Menanyakan konfirmasi persetujuan (y/n)."""
    jawaban_ya = {"y", "ya", "yes"}
    jawaban_tidak = {"t", "tidak", "n", "no"}
    while True:
        jawaban = input(f"{pesan} (y/n): ").strip().lower()
        if jawaban in jawaban_ya:
            return True
        if jawaban in jawaban_tidak:
            return False
        print("[PERINGATAN] Jawab dengan 'y' (ya) atau 'n' (tidak)!")


# ==============================================================================
# 4. FUNGSI PENYIMPANAN DATA (FILE I/O DENGAN EXCEPTION HANDLING)
# ==============================================================================
def _baca_file_json(path_file, tipe_data_kosong=list):
    """Fungsi umum untuk membaca file JSON dengan proteksi Exception Handling."""
    if not os.path.exists(path_file):
        return tipe_data_kosong()
    try:
        with open(path_file, "r", encoding="utf-8") as berkas:
            data = json.load(berkas)
            return data
    except FileNotFoundError:
        return tipe_data_kosong()
    except json.JSONDecodeError:
        print(f"[PERINGATAN] File '{os.path.basename(path_file)}' rusak/tidak valid. Menggunakan data kosong.")
        return tipe_data_kosong()
    except OSError as err:
        print(f"[ERROR] Gagal membaca file '{os.path.basename(path_file)}': {err}")
        return tipe_data_kosong()


def _tulis_file_json(path_file, data):
    """Fungsi umum untuk menulis ke file JSON dengan proteksi Exception Handling."""
    try:
        # Pastikan direktori tujuan tersedia
        folder_tujuan = os.path.dirname(path_file)
        if folder_tujuan and not os.path.exists(folder_tujuan):
            os.makedirs(folder_tujuan, exist_ok=True)

        with open(path_file, "w", encoding="utf-8") as berkas:
            json.dump(data, berkas, indent=4, ensure_ascii=False)
        return True
    except (OSError, IOError) as err:
        print(f"[ERROR] Gagal menyimpan ke '{os.path.basename(path_file)}': {err}")
        return False


# --- Fungsi Simpan Spesifik Setiap Entitas ---
def simpan_data_pelanggan(daftar_pelanggan):
    """Menyimpan list data pelanggan ke file JSON."""
    sukses = _tulis_file_json(FILE_PELANGGAN, daftar_pelanggan)
    return sukses


def simpan_data_layanan(daftar_layanan):
    """Menyimpan list data layanan ke file JSON."""
    sukses = _tulis_file_json(FILE_LAYANAN, daftar_layanan)
    return sukses


def simpan_data_pesanan(daftar_pesanan):
    """Menyimpan list data pesanan ke file JSON."""
    sukses = _tulis_file_json(FILE_PESANAN, daftar_pesanan)
    return sukses


def simpan_riwayat_pembayaran(riwayat_pembayaran):
    """Menyimpan list riwayat transaksi pembayaran ke file JSON."""
    sukses = _tulis_file_json(FILE_PEMBAYARAN, riwayat_pembayaran)
    return sukses


def simpan_semua_data(daftar_pelanggan, daftar_layanan, daftar_pesanan, riwayat_pembayaran):
    """Menyimpan seluruh data aplikasi ke file masing-masing sekaligus."""
    s1 = simpan_data_pelanggan(daftar_pelanggan)
    s2 = simpan_data_layanan(daftar_layanan)
    s3 = simpan_data_pesanan(daftar_pesanan)
    s4 = simpan_riwayat_pembayaran(riwayat_pembayaran)
    return all((s1, s2, s3, s4))


# --- Fungsi Baca / Muat Spesifik Setiap Entitas ---
def muat_data_pelanggan():
    """Membaca data pelanggan dari file JSON."""
    data = _baca_file_json(FILE_PELANGGAN, list)
    return data if isinstance(data, list) else []


def muat_data_layanan():
    """Membaca data layanan dari file JSON."""
    data = _baca_file_json(FILE_LAYANAN, list)
    return data if isinstance(data, list) else []


def muat_data_pesanan():
    """Membaca data pesanan dari file JSON."""
    data = _baca_file_json(FILE_PESANAN, list)
    return data if isinstance(data, list) else []


def muat_riwayat_pembayaran():
    """Membaca data riwayat pembayaran dari file JSON."""
    data = _baca_file_json(FILE_PEMBAYARAN, list)
    return data if isinstance(data, list) else []


def muat_semua_data():
    """
    Fitur Utama: Membaca kembali seluruh data ketika aplikasi dijalankan.
    Mengembalikan dictionary berisi 4 data utama:
    {'pelanggan': [...], 'layanan': [...], 'pesanan': [...], 'pembayaran': [...]}
    """
    pelanggan = muat_data_pelanggan()
    layanan = muat_data_layanan()
    pesanan = muat_data_pesanan()
    pembayaran = muat_riwayat_pembayaran()
    return {
        "pelanggan": pelanggan,
        "layanan": layanan,
        "pesanan": pesanan,
        "pembayaran": pembayaran,
    }


# Alias untuk kemudahan integrasi dengan modul teman
baca_data_pelanggan = muat_data_pelanggan
baca_data_layanan = muat_data_layanan
baca_data_pesanan = muat_data_pesanan
baca_riwayat_pembayaran = muat_riwayat_pembayaran


# ==============================================================================
# 5. FITUR RIWAYAT PESANAN (Menampilkan Seluruh & Filter Pelanggan)
# ==============================================================================
def _ambil_kode_pesanan(pesanan_dict):
    """Mengekstrak nomor kode/transaksi pesanan (fleksibel kode atau no_transaksi)."""
    return pesanan_dict.get("kode") or pesanan_dict.get("no_transaksi") or "-"


def _ambil_nama_pelanggan(pesanan_dict, daftar_pelanggan=None):
    """Mengekstrak nama pelanggan dari pesanan atau relasi id_pelanggan."""
    if "pelanggan" in pesanan_dict and pesanan_dict["pelanggan"]:
        return str(pesanan_dict["pelanggan"])
    if "nama_pelanggan" in pesanan_dict and pesanan_dict["nama_pelanggan"]:
        return str(pesanan_dict["nama_pelanggan"])

    id_plg = pesanan_dict.get("id_pelanggan")
    if id_plg and daftar_pelanggan:
        for p in daftar_pelanggan:
            if p.get("id") == id_plg or p.get("id_pelanggan") == id_plg:
                return p.get("nama") or p.get("nama_pelanggan") or id_plg
    return id_plg if id_plg else "Umum"


def _ambil_status_bayar(pesanan_dict, riwayat_pembayaran=None):
    """Mengecek status pembayaran pesanan (Lunas / Belum Lunas)."""
    # 1. Cek langsung dari key status_bayar jika ada
    status = pesanan_dict.get("status_bayar", "")
    if isinstance(status, str) and status.lower() == "lunas":
        return "Lunas"

    # 2. Cek cross-check terhadap riwayat pembayaran menggunakan Set
    if riwayat_pembayaran:
        kode = _ambil_kode_pesanan(pesanan_dict).upper()
        # Penggunaan Set untuk pencarian cepat
        set_trx_lunas = {
            bayar.get("no_transaksi", "").upper()
            for bayar in riwayat_pembayaran
            if bayar.get("no_transaksi")
        }
        if kode in set_trx_lunas:
            return "Lunas"

    return "Belum Lunas"


def tampilkan_riwayat_pesanan(daftar_pesanan, riwayat_pembayaran=None, daftar_pelanggan=None):
    """
    Fitur 5.1: Menampilkan seluruh riwayat pesanan pelanggan dalam bentuk tabel terminal.
    """
    print()
    cetak_garis(85)
    print("                    RIWAYAT SELURUH PESANAN LAUNDRY")
    cetak_garis(85)

    if not daftar_pesanan:
        print("  [INFO] Belum ada data riwayat pesanan yang tercatat.")
        cetak_garis(85)
        return

    # Header tabel
    print(
        f"{'No':<4} {'Kode':<8} {'Pelanggan':<16} {'Layanan':<15} "
        f"{'Berat':<8} {'Total Biaya':<14} {'Status':<10} {'Bayar':<10}"
    )
    cetak_garis(85, "-")

    for i, pesanan in enumerate(daftar_pesanan, start=1):
        kode = _ambil_kode_pesanan(pesanan)
        nama = _ambil_nama_pelanggan(pesanan, daftar_pelanggan)
        layanan = pesanan.get("layanan") or pesanan.get("nama_layanan") or "-"
        berat = f"{pesanan.get('berat_kg', 0)} kg"
        total = format_rupiah(pesanan.get("total") or pesanan.get("total_biaya", 0))
        status_proses = pesanan.get("status", "Diterima")
        status_bayar = _ambil_status_bayar(pesanan, riwayat_pembayaran)

        print(
            f"{i:<4} {kode:<8} {nama[:15]:<16} {layanan[:14]:<15} "
            f"{berat:<8} {total:<14} {status_proses:<10} {status_bayar:<10}"
        )

    cetak_garis(85, "-")
    print(f"Total Riwayat: {len(daftar_pesanan)} pesanan tercatat.")
    cetak_garis(85)


def cari_riwayat_pelanggan(daftar_pesanan, riwayat_pembayaran=None, daftar_pelanggan=None):
    """
    Fitur 5.1 lanjutan: Menampilkan riwayat pesanan khusus untuk pelanggan tertentu.
    Menerapkan pencarian berdasarkan nama, ID pelanggan, atau nomor telepon.
    """
    print("\n--- CARI RIWAYAT PESANAN PELANGGAN ---")
    if not daftar_pesanan:
        print("[INFO] Belum ada riwayat pesanan untuk dicari.")
        return

    # Menampilkan daftar nama pelanggan unik yang pernah bertransaksi (Memakai Set)
    pelanggan_unik = set()
    for p in daftar_pesanan:
        nama = _ambil_nama_pelanggan(p, daftar_pelanggan)
        if nama:
            pelanggan_unik.add(nama)

    print(f"Pelanggan terdaftar yang memiliki riwayat: {', '.join(sorted(pelanggan_unik))}")
    keyword = input_teks_valid("Masukkan Nama / ID / No. HP Pelanggan: ").lower()

    hasil_filter = []
    for p in daftar_pesanan:
        nama = _ambil_nama_pelanggan(p, daftar_pelanggan).lower()
        id_plg = str(p.get("id_pelanggan", "")).lower()
        telepon = str(p.get("telepon", "")).lower()
        kode = _ambil_kode_pesanan(p).lower()

        if keyword in nama or keyword in id_plg or keyword in telepon or keyword in kode:
            hasil_filter.append(p)

    if not hasil_filter:
        print(f"[INFO] Tidak ditemukan riwayat pesanan untuk kata kunci '{keyword}'.")
        return

    print(f"\nDitemukan {len(hasil_filter)} pesanan sesuai pencarian:")
    tampilkan_riwayat_pesanan(hasil_filter, riwayat_pembayaran, daftar_pelanggan)


# ==============================================================================
# 6. FITUR RIWAYAT PEMBAYARAN & TOTAL PENDAPATAN LAUNDRY
# ==============================================================================
def tampilkan_riwayat_pembayaran(riwayat_pembayaran):
    """
    Fitur 5.4: Menampilkan riwayat transaksi pembayaran kasir yang sudah lunas.
    """
    print()
    cetak_garis(92)
    print("                        RIWAYAT PEMBAYARAN KASIR")
    cetak_garis(92)

    if not riwayat_pembayaran:
        print("  [INFO] Belum ada catatan riwayat pembayaran.")
        cetak_garis(92)
        return

    print(
        f"{'No':<4} {'ID Bayar':<9} {'No. TRX':<9} {'Pelanggan':<16} "
        f"{'Layanan':<14} {'Tagihan':<13} {'Dibayar':<13} {'Waktu':<19}"
    )
    cetak_garis(92, "-")

    total_kas_masuk = 0
    for i, bayar in enumerate(riwayat_pembayaran, start=1):
        id_bayar = bayar.get("id_pembayaran", f"PAY{i:03d}")
        no_trx = bayar.get("no_transaksi", "-")
        nama = bayar.get("nama_pelanggan", "-")
        layanan = bayar.get("nama_layanan", "-")
        tagihan = bayar.get("total_tagihan", bayar.get("nominal_bayar", 0))
        dibayar = bayar.get("nominal_bayar", 0)
        waktu = str(bayar.get("waktu_bayar", "-"))[:19]

        total_kas_masuk += tagihan

        print(
            f"{i:<4} {id_bayar:<9} {no_trx:<9} {nama[:15]:<16} "
            f"{layanan[:13]:<14} {format_rupiah(tagihan):<13} {format_rupiah(dibayar):<13} {waktu:<19}"
        )

    cetak_garis(92, "-")
    print(f"Total Pembayaran Tercatat: {len(riwayat_pembayaran)} transaksi.")
    print(f"Total Nominal Kas Diterima : {format_rupiah(total_kas_masuk)}")
    cetak_garis(92)


def hitung_statistik_pendapatan(riwayat_pembayaran, daftar_pesanan=None):
    """
    Menghitung statistik pendapatan laundry secara komprehensif.
    Mengembalikan Dictionary berisi rincian finansial.
    """
    total_biaya_kotor = 0.0
    total_diskon = 0.0
    total_pendapatan_bersih = 0.0
    jumlah_transaksi = len(riwayat_pembayaran)

    # Dictionary untuk agregasi pendapatan per jenis layanan
    pendapatan_per_layanan = {}

    if riwayat_pembayaran:
        for b in riwayat_pembayaran:
            biaya_awal = float(b.get("biaya_awal", 0))
            diskon = float(b.get("nominal_diskon", 0))
            tagihan = float(b.get("total_tagihan", b.get("nominal_bayar", 0)))
            layanan = b.get("nama_layanan", "Lainnya")

            total_biaya_kotor += biaya_awal if biaya_awal > 0 else tagihan
            total_diskon += diskon
            total_pendapatan_bersih += tagihan

            # Agregasi per kategori layanan
            if layanan not in pendapatan_per_layanan:
                pendapatan_per_layanan[layanan] = {"frekuensi": 0, "total": 0.0}
            pendapatan_per_layanan[layanan]["frekuensi"] += 1
            pendapatan_per_layanan[layanan]["total"] += tagihan

    # Fallback jika riwayat_pembayaran kosong tapi daftar_pesanan ada yang lunas
    elif daftar_pesanan:
        for p in daftar_pesanan:
            status_bayar = str(p.get("status_bayar", "")).lower()
            if status_bayar == "lunas":
                nilai = float(p.get("total", p.get("total_biaya", 0)))
                layanan = p.get("layanan", "Lainnya")
                total_biaya_kotor += nilai
                total_pendapatan_bersih += nilai
                jumlah_transaksi += 1

                if layanan not in pendapatan_per_layanan:
                    pendapatan_per_layanan[layanan] = {"frekuensi": 0, "total": 0.0}
                pendapatan_per_layanan[layanan]["frekuensi"] += 1
                pendapatan_per_layanan[layanan]["total"] += nilai

    rata_rata = (
        (total_pendapatan_bersih / jumlah_transaksi) if jumlah_transaksi > 0 else 0.0
    )

    return {
        "jumlah_transaksi": jumlah_transaksi,
        "biaya_kotor": total_biaya_kotor,
        "total_diskon": total_diskon,
        "pendapatan_bersih": total_pendapatan_bersih,
        "rata_rata": rata_rata,
        "per_layanan": pendapatan_per_layanan,
    }


def tampilkan_total_pendapatan(riwayat_pembayaran, daftar_pesanan=None):
    """
    Fitur 5.2: Menampilkan total pendapatan laundry beserta rincian dan analisisnya.
    """
    stats = hitung_statistik_pendapatan(riwayat_pembayaran, daftar_pesanan)

    print()
    cetak_garis(60)
    print("            LAPORAN TOTAL PENDAPATAN LAUNDRY")
    cetak_garis(60)
    print(f"  Jumlah Transaksi Lunas   : {stats['jumlah_transaksi']} transaksi")
    print(f"  Pendapatan Kotor (Awal)  : {format_rupiah(stats['biaya_kotor'])}")
    print(f"  Total Potongan Diskon    : -{format_rupiah(stats['total_diskon'])}")
    cetak_garis(60, "-")
    print(f"  TOTAL PENDAPATAN BERSIH  : {format_rupiah(stats['pendapatan_bersih'])}")
    print(f"  Rata-rata per Transaksi  : {format_rupiah(stats['rata_rata'])}")
    cetak_garis(60, "-")

    print("\n  Rincian Pendapatan per Jenis Layanan:")
    if stats["per_layanan"]:
        for lyn, info in stats["per_layanan"].items():
            print(f"   • {lyn:<20} : {info['frekuensi']:>2} order | Total: {format_rupiah(info['total'])}")
    else:
        print("   (Belum ada data transaksi layanan yang lunas)")

    cetak_garis(60)

    # Tawaran opsi ekspor ke file teks (.txt)
    if stats["jumlah_transaksi"] > 0:
        if konfirmasi_tindakan("Apakah Anda ingin mengekspor laporan pendapatan ke file .txt?"):
            ekspor_laporan_pendapatan(stats)


def ekspor_laporan_pendapatan(stats):
    """Mengekspor ringkasan pendapatan ke file teks laporan_pendapatan.txt (Penerapan I/O .txt)."""
    try:
        waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(FILE_EKSPOR_LAPORAN, "w", encoding="utf-8") as berkas:
            berkas.write("============================================================\n")
            berkas.write("            LAPORAN KEUANGAN & PENDAPATAN LAUNDRY\n")
            berkas.write(f"            Tanggal Cetak: {waktu_sekarang}\n")
            berkas.write("============================================================\n\n")
            berkas.write(f"Jumlah Transaksi Lunas : {stats['jumlah_transaksi']}\n")
            berkas.write(f"Pendapatan Kotor       : {format_rupiah(stats['biaya_kotor'])}\n")
            berkas.write(f"Total Diskon Diberikan : {format_rupiah(stats['total_diskon'])}\n")
            berkas.write(f"TOTAL PENDAPATAN BERSIH: {format_rupiah(stats['pendapatan_bersih'])}\n")
            berkas.write(f"Rata-rata per Transaksi: {format_rupiah(stats['rata_rata'])}\n\n")
            berkas.write("Rincian per Layanan:\n")
            for lyn, info in stats["per_layanan"].items():
                berkas.write(f"- {lyn:<20}: {info['frekuensi']} order ({format_rupiah(info['total'])})\n")
            berkas.write("\n============================================================\n")
        print(f"[SUKSES] Laporan berhasil diekspor ke: {FILE_EKSPOR_LAPORAN}")
    except OSError as err:
        print(f"[ERROR] Gagal mengekspor laporan: {err}")


# ==============================================================================
# 7. FITUR MANAJEMEN RIWAYAT (CRUD: UBAH & HAPUS RIWAYAT)
# ==============================================================================
def ubah_status_riwayat_pesanan(daftar_pesanan):
    """Fitur Ubah (CRUD): Memperbarui status pesanan langsung dari riwayat."""
    print("\n--- UBAH STATUS PENGERJAAN PESANAN ---")
    if not daftar_pesanan:
        print("[INFO] Tidak ada data pesanan untuk diubah.")
        return

    tampilkan_riwayat_pesanan(daftar_pesanan)
    target = input_teks_valid("Masukkan Kode Pesanan yang akan diubah (0 = batal): ").upper()
    if target == "0":
        print("[INFO] Perubahan dibatalkan.")
        return

    pesanan_target = None
    for p in daftar_pesanan:
        if _ambil_kode_pesanan(p).upper() == target:
            pesanan_target = p
            break

    if not pesanan_target:
        print(f"[ERROR] Kode pesanan '{target}' tidak ditemukan.")
        return

    print(f"\nStatus pesanan saat ini: {pesanan_target.get('status', 'Diterima')}")
    print("Pilih status baru:")
    for idx, st in enumerate(STATUS_PESANAN_TUPLE, start=1):
        print(f"{idx}. {st}")

    pilihan = input_pilihan_menu("Pilih nomor status (1-4): ", ("1", "2", "3", "4"))
    status_baru = STATUS_PESANAN_TUPLE[int(pilihan) - 1]

    pesanan_target["status"] = status_baru
    if simpan_data_pesanan(daftar_pesanan):
        print(f"[SUKSES] Status pesanan '{target}' berhasil diubah menjadi '{status_baru}'!")


def hapus_riwayat_transaksi(riwayat_pembayaran, daftar_pesanan):
    """Fitur Hapus (CRUD): Menghapus catatan riwayat pembayaran atau pesanan dengan konfirmasi."""
    print("\n--- HAPUS DATA RIWAYAT ---")
    print("1. Hapus Catatan Riwayat Pembayaran Kasir")
    print("2. Hapus Catatan Riwayat Pesanan")
    print("0. Batal")

    pilihan = input_pilihan_menu("Pilih jenis data yang ingin dihapus (0-2): ", ("0", "1", "2"))
    if pilihan == "0":
        print("[INFO] Tindakan dibatalkan.")
        return

    if pilihan == "1":
        if not riwayat_pembayaran:
            print("[INFO] Riwayat pembayaran sudah kosong.")
            return
        tampilkan_riwayat_pembayaran(riwayat_pembayaran)
        id_hapus = input_teks_valid("Masukkan ID Pembayaran yang ingin dihapus (contoh: PAY001): ").upper()

        terpilih = None
        for b in riwayat_pembayaran:
            if b.get("id_pembayaran", "").upper() == id_hapus:
                terpilih = b
                break

        if not terpilih:
            print(f"[ERROR] ID Pembayaran '{id_hapus}' tidak ditemukan.")
            return

        if konfirmasi_tindakan(f"Yakin ingin menghapus pembayaran {id_hapus} ({terpilih.get('nama_pelanggan')})?"):
            riwayat_pembayaran.remove(terpilih)
            simpan_riwayat_pembayaran(riwayat_pembayaran)
            print(f"[SUKSES] Riwayat pembayaran '{id_hapus}' berhasil dihapus.")

    elif pilihan == "2":
        if not daftar_pesanan:
            print("[INFO] Riwayat pesanan sudah kosong.")
            return
        tampilkan_riwayat_pesanan(daftar_pesanan)
        kode_hapus = input_teks_valid("Masukkan Kode Pesanan yang ingin dihapus: ").upper()

        terpilih = None
        for p in daftar_pesanan:
            if _ambil_kode_pesanan(p).upper() == kode_hapus:
                terpilih = p
                break

        if not terpilih:
            print(f"[ERROR] Pesanan dengan kode '{kode_hapus}' tidak ditemukan.")
            return

        if konfirmasi_tindakan(f"Yakin ingin menghapus pesanan {kode_hapus}?"):
            daftar_pesanan.remove(terpilih)
            simpan_data_pesanan(daftar_pesanan)
            print(f"[SUKSES] Pesanan '{kode_hapus}' berhasil dihapus.")


# ==============================================================================
# 8. SUBMENU INTERAKTIF RIWAYAT & PENYIMPANAN DATA
# ==============================================================================
def tampilkan_header_menu():
    """Menampilkan antarmuka judul menu submenu riwayat."""
    print()
    cetak_garis(56)
    print("       FITUR 5: RIWAYAT DAN PENYIMPANAN DATA")
    cetak_garis(56)
    print("  1. Tampilkan Seluruh Riwayat Pesanan")
    print("  2. Cari Riwayat Pesanan Berdasarkan Pelanggan")
    print("  3. Tampilkan Riwayat Pembayaran Kasir")
    print("  4. Tampilkan Total Pendapatan Laundry")
    print("  5. Ubah Status Pengerjaan Pesanan")
    print("  6. Hapus Data Riwayat (Pesanan/Pembayaran)")
    print("  0. Kembali ke Menu Utama")
    cetak_garis(56)


def menu_riwayat(daftar_pelanggan=None, daftar_layanan=None, daftar_pesanan=None, riwayat_pembayaran=None):
    """
    Submenu utama Fitur 5: Riwayat dan Penyimpanan Data.
    Dapat menerima data dari main.py atau memuat secara mandiri dari file JSON.
    """
    # Membaca kembali data ketika dijalankan jika parameter belum diisi
    if daftar_pelanggan is None:
        daftar_pelanggan = muat_data_pelanggan()
    if daftar_layanan is None:
        daftar_layanan = muat_data_layanan()
    if daftar_pesanan is None:
        daftar_pesanan = muat_data_pesanan()
    if riwayat_pembayaran is None:
        riwayat_pembayaran = muat_riwayat_pembayaran()

    while True:
        tampilkan_header_menu()
        pilihan = input_pilihan_menu("Pilih menu (0-6): ", PILIHAN_MENU_RIWAYAT)

        if pilihan == "1":
            tampilkan_riwayat_pesanan(daftar_pesanan, riwayat_pembayaran, daftar_pelanggan)
        elif pilihan == "2":
            cari_riwayat_pelanggan(daftar_pesanan, riwayat_pembayaran, daftar_pelanggan)
        elif pilihan == "3":
            tampilkan_riwayat_pembayaran(riwayat_pembayaran)
        elif pilihan == "4":
            tampilkan_total_pendapatan(riwayat_pembayaran, daftar_pesanan)
        elif pilihan == "5":
            ubah_status_riwayat_pesanan(daftar_pesanan)
        elif pilihan == "6":
            hapus_riwayat_transaksi(riwayat_pembayaran, daftar_pesanan)
        elif pilihan == "0":
            print("\n[INFO] Kembali ke menu utama...")
            break


# ==============================================================================
# 9. EKSEKUSI MANDIRI (UNTUK PENGUJIAN LANGSUNG DI TERMINAL)
# ==============================================================================
if __name__ == "__main__":
    try:
        print("\n[MEMUAT DATA SISTEM LAUNDRY DARI PENYIMPANAN FILE JSON...]")
        data_sistem = muat_semua_data()
        print(
            f"Data Termuat: {len(data_sistem['pelanggan'])} Pelanggan, "
            f"{len(data_sistem['layanan'])} Layanan, "
            f"{len(data_sistem['pesanan'])} Pesanan, "
            f"{len(data_sistem['pembayaran'])} Riwayat Pembayaran."
        )

        menu_riwayat(
            daftar_pelanggan=data_sistem["pelanggan"],
            daftar_layanan=data_sistem["layanan"],
            daftar_pesanan=data_sistem["pesanan"],
            riwayat_pembayaran=data_sistem["pembayaran"],
        )
    except (KeyboardInterrupt, EOFError):
        print("\n\n[INFO] Program dihentikan oleh pengguna. Seluruh data tetap tersimpan dengan aman.")
