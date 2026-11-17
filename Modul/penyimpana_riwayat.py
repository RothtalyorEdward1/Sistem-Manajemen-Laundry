import json
import os

# Tuple konstanta untuk direktori dan daftar file penyimpanan (bersifat tetap/immutable)
FOLDER_DATA = "data"
DAFTAR_FILE_JSON = (
    "pelanggan.json",
    "layanan.json",
    "pesanan.json",
    "pembayaran.json",
)


def pastikan_folder_data():
    """Memastikan folder 'data/' tersedia sebelum operasi baca/tulis file."""
    try:
        if not os.path.exists(FOLDER_DATA):
            os.makedirs(FOLDER_DATA)
    except OSError as error:
        print(f"[ERROR] Gagal membuat folder penyimpanan '{FOLDER_DATA}': {error}")


def _baca_file_json(nama_file):
    """Fungsi internal untuk membaca data dari file JSON dengan exception handling."""
    pastikan_folder_data()
    path_file = os.path.join(FOLDER_DATA, nama_file)

    try:
        with open(path_file, mode="r", encoding="utf-8") as file:
            data = json.load(file)
            # Pastikan data yang dibaca bertipe list
            if isinstance(data, list):
                return data
            return []
    except FileNotFoundError:
        # Jika file belum ada saat pertama kali dijalankan, buat file kosong default
        _tulis_file_json(nama_file, [])
        return []
    except json.JSONDecodeError:
        print(f"[PERINGATAN] Format file '{nama_file}' rusak/kosong. Memuat data kosong.")
        return []
    except IOError as error:
        print(f"[ERROR] Gagal membaca '{nama_file}': {error}")
        return []


def _tulis_file_json(nama_file, data):
    """Fungsi internal untuk menyimpan list/dictionary ke file JSON."""
    pastikan_folder_data()
    path_file = os.path.join(FOLDER_DATA, nama_file)

    try:
        with open(path_file, mode="w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return True
    except (IOError, TypeError) as error:
        print(f"[ERROR] Gagal menyimpan data ke '{nama_file}': {error}")
        return False


# =====================================================================
# BAGIAN A: PENYIMPANAN DATA (PELANGGAN, LAYANAN, PESANAN, PEMBAYARAN)
# =====================================================================

def simpan_data_pelanggan(daftar_pelanggan):
    """Menyimpan seluruh data pelanggan ke pelanggan.json."""
    return _tulis_file_json(DAFTAR_FILE_JSON[0], daftar_pelanggan)


def simpan_data_layanan(daftar_layanan):
    """Menyimpan seluruh data layanan laundry ke layanan.json."""
    return _tulis_file_json(DAFTAR_FILE_JSON[1], daftar_layanan)


def simpan_data_pesanan(daftar_pesanan):
    """Menyimpan seluruh data pesanan laundry ke pesanan.json."""
    return _tulis_file_json(DAFTAR_FILE_JSON[2], daftar_pesanan)


def simpan_riwayat_pembayaran(riwayat_pembayaran):
    """Menyimpan seluruh riwayat pembayaran ke pembayaran.json."""
    return _tulis_file_json(DAFTAR_FILE_JSON[3], riwayat_pembayaran)


def simpan_semua_data(daftar_pelanggan, daftar_layanan, daftar_pesanan, riwayat_pembayaran):
    """Menyimpan seluruh entitas data sekaligus."""
    hasil_simpan = (
        simpan_data_pelanggan(daftar_pelanggan),
        simpan_data_layanan(daftar_layanan),
        simpan_data_pesanan(daftar_pesanan),
        simpan_riwayat_pembayaran(riwayat_pembayaran),
    )
    if all(hasil_simpan):
        print("[INFO] Seluruh data berhasil disimpan ke penyimpanan lokal.")
        return True
    print("[PERINGATAN] Sebagian data gagal disimpan. Periksa pesan error di atas.")
    return False


# =====================================================================
# BAGIAN B: MEMBACA KEMBALI DATA SAAT APLIKASI DIJALANKAN
# =====================================================================

def muat_data_pelanggan():
    """Membaca kembali data pelanggan dari pelanggan.json."""
    return _baca_file_json(DAFTAR_FILE_JSON[0])


def muat_data_layanan():
    """Membaca kembali data layanan dari layanan.json."""
    return _baca_file_json(DAFTAR_FILE_JSON[1])


def muat_data_pesanan():
    """Membaca kembali data pesanan dari pesanan.json."""
    return _baca_file_json(DAFTAR_FILE_JSON[2])


def muat_riwayat_pembayaran():
    """Membaca kembali riwayat pembayaran dari pembayaran.json."""
    return _baca_file_json(DAFTAR_FILE_JSON[3])


def muat_semua_data():
    """Memuat seluruh data aplikasi saat program pertama kali dijalankan."""
    database = {
        "pelanggan": muat_data_pelanggan(),
        "layanan": muat_data_layanan(),
        "pesanan": muat_data_pesanan(),
        "pembayaran": muat_riwayat_pembayaran(),
    }
    return database


# =====================================================================
# BAGIAN C: RIWAYAT PESANAN PELANGGAN & TOTAL PENDAPATAN LAUNDRY
# =====================================================================

def tampilkan_riwayat_pesanan_pelanggan(
    daftar_pesanan, daftar_pelanggan, daftar_layanan, riwayat_pembayaran
):
    """Menampilkan riwayat pesanan pelanggan (semua atau filter berdasarkan ID pelanggan)."""
    print("\n" + "=" * 65)
    print("               RIWAYAT PESANAN PELANGGAN LAUNDRY")
    print("=" * 65)

    if not daftar_pesanan:
        print("Belum ada data pesanan yang tercatat.")
        return

    # Menggunakan Set untuk menyimpan ID pelanggan unik yang terdaftar
    id_pelanggan_terdaftar = {
        p.get("id_pelanggan", "").upper() for p in daftar_pelanggan
    }

    # Mapping dictionary agar pencarian nama pelanggan & layanan lebih cepat
    map_pelanggan = {
        p.get("id_pelanggan", "").upper(): p.get("nama", "Tidak Diketahui")
        for p in daftar_pelanggan
    }
    map_layanan = {
        l.get("id_layanan", "").upper(): l.get("nama_layanan", "Layanan Dihapus")
        for l in daftar_layanan
    }
    transaksi_lunas = {
        b.get("no_transaksi", "").upper() for b in riwayat_pembayaran
    }

    print("1. Tampilkan Riwayat Pesanan Berdasarkan ID Pelanggan")
    print("2. Tampilkan Seluruh Riwayat Pesanan")

    while True:
        pilihan = input("Pilih mode tampilan (1/2): ").strip()
        if pilihan in ("1", "2"):
            break
        print("[ERROR] Input tidak valid! Masukkan angka 1 atau 2.")

    pesanan_terfilter = []

    if pilihan == "1":
        id_cari = input("Masukkan ID Pelanggan (contoh: PLG001): ").strip().upper()
        if not id_cari:
            print("[ERROR] ID Pelanggan tidak boleh kosong.")
            return

        if id_cari not in id_pelanggan_terdaftar:
            print(f"[INFO] Pelanggan dengan ID '{id_cari}' tidak ditemukan dalam data pelanggan.")

        for pesanan in daftar_pesanan:
            if pesanan.get("id_pelanggan", "").upper() == id_cari:
                pesanan_terfilter.append(pesanan)
    else:
        pesanan_terfilter = daftar_pesanan

    if not pesanan_terfilter:
        print("\n[INFO] Tidak ada riwayat pesanan untuk kriteria tersebut.")
        return

    print("\n" + "-" * 95)
    print(
        f"{'No. TRX':<10} | {'Pelanggan':<18} | {'Layanan':<20} | "
        f"{'Berat':<7} | {'Total Biaya':<13} | {'Status':<10} | {'Bayar':<7}"
    )
    print("-" * 95)

    for item in pesanan_terfilter:
        no_trx = item.get("no_transaksi", "-")
        id_plg = item.get("id_pelanggan", "-").upper()
        id_lyn = item.get("id_layanan", "-").upper()

        nama_plg = f"{map_pelanggan.get(id_plg, 'Unknown')} ({id_plg})"
        nama_lyn = map_layanan.get(id_lyn, id_lyn)
        berat = f"{item.get('berat_kg', 0)} kg"
        total = f"Rp{item.get('total_biaya', 0):,.0f}"
        status_kerja = item.get("status", "-").capitalize()
        status_bayar = "Lunas" if no_trx.upper() in transaksi_lunas else "Belum"

        print(
            f"{no_trx:<10} | {nama_plg[:18]:<18} | {nama_lyn[:20]:<20} | "
            f"{berat:<7} | {total:<13} | {status_kerja:<10} | {status_bayar:<7}"
        )

    print("-" * 95)
    print(f"Total riwayat ditampilkan: {len(pesanan_terfilter)} transaksi.\n")


def tampilkan_total_pendapatan(riwayat_pembayaran, daftar_pesanan=None, daftar_layanan=None):
    """Menghitung dan menampilkan total pendapatan laundry dari riwayat pembayaran."""
    print("\n" + "=" * 60)
    print("             LAPORAN TOTAL PENDAPATAN LAUNDRY")
    print("=" * 60)

    if not riwayat_pembayaran:
        print("Belum ada transaksi pembayaran yang masuk.")
        print("Total Pendapatan Laundry: Rp0")
        print("=" * 60)
        return 0

    total_pendapatan = 0
    jumlah_transaksi_sah = 0

    for bayar in riwayat_pembayaran:
        # Pendapatan dihitung dari total_tagihan yang sudah dibayar lunas
        nilai_tagihan = bayar.get("total_tagihan", 0)
        if isinstance(nilai_tagihan, (int, float)) and nilai_tagihan > 0:
            total_pendapatan += nilai_tagihan
            jumlah_transaksi_sah += 1

    print(f"Jumlah Transaksi Lunas   : {jumlah_transaksi_sah} transaksi")
    print(f"Total Pendapatan Laundry : Rp{total_pendapatan:,.0f}")

    # Rincian tambahan per layanan jika data pesanan & layanan tersedia
    if daftar_pesanan and daftar_layanan:
        map_layanan = {
            l.get("id_layanan", "").upper(): l.get("nama_layanan", "Lainnya")
            for l in daftar_layanan
        }
        map_pesanan_ke_layanan = {
            p.get("no_transaksi", "").upper(): p.get("id_layanan", "").upper()
            for p in daftar_pesanan
        }
        pendapatan_per_layanan = {}

        for bayar in riwayat_pembayaran:
            no_trx = bayar.get("no_transaksi", "").upper()
            id_lyn = map_pesanan_ke_layanan.get(no_trx, "")
            nama_lyn = map_layanan.get(id_lyn, "Layanan Tidak Teridentifikasi")
            nominal = bayar.get("total_tagihan", 0)

            if isinstance(nominal, (int, float)) and nominal > 0:
                pendapatan_per_layanan[nama_lyn] = (
                    pendapatan_per_layanan.get(nama_lyn, 0) + nominal
                )

        if pendapatan_per_layanan:
            print("-" * 60)
            print("Rincian Pendapatan per Jenis Layanan:")
            for nama_layanan, subtotal in pendapatan_per_layanan.items():
                print(f"  - {nama_layanan:<30}: Rp{subtotal:,.0f}")

    print("=" * 60 + "\n")
    return total_pendapatan


# =====================================================================
# BAGIAN D: SUBMENU FITUR 5 (UNTUK DIPANGGIL DARI main.py)
# =====================================================================

def menu_riwayat_dan_penyimpanan(
    daftar_pelanggan, daftar_layanan, daftar_pesanan, riwayat_pembayaran
):
    """Submenu interaktif untuk Fitur 5: Riwayat dan Penyimpanan Data."""
    while True:
        print("\n=== MENU RIWAYAT & PENYIMPANAN DATA ===")
        print("1. Tampilkan Riwayat Pesanan Pelanggan")
        print("2. Tampilkan Total Pendapatan Laundry")
        print("3. Simpan Seluruh Data Sekarang")
        print("0. Kembali ke Menu Utama")

        pilihan = input("Pilih menu (0-3): ").strip()

        if pilihan == "1":
            tampilkan_riwayat_pesanan_pelanggan(
                daftar_pesanan, daftar_pelanggan, daftar_layanan, riwayat_pembayaran
            )
        elif pilihan == "2":
            tampilkan_total_pendapatan(
                riwayat_pembayaran, daftar_pesanan, daftar_layanan
            )
        elif pilihan == "3":
            simpan_semua_data(
                daftar_pelanggan, daftar_layanan, daftar_pesanan, riwayat_pembayaran
            )
        elif pilihan == "0":
            break
        else:
            print("[ERROR] Pilihan tidak valid! Silakan masukkan angka 0 sampai 3.")