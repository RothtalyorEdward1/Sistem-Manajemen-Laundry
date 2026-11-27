import json
import os
from datetime import datetime

DIREKTORI_MODUL = os.path.dirname(os.path.abspath(__file__))

FILE_PELANGGAN = os.path.join(DIREKTORI_MODUL, "data_pelanggan.json")
FILE_LAYANAN = os.path.join(DIREKTORI_MODUL, "layanan.json")
FILE_PESANAN = os.path.join(DIREKTORI_MODUL, "pesanan.json")
FILE_PEMBAYARAN = os.path.join(DIREKTORI_MODUL, "riwayat_pembayaran.json")
FILE_EKSPOR_LAPORAN = os.path.join(DIREKTORI_MODUL, "laporan_pendapatan.txt")


PILIHAN_MENU_RIWAYAT = ("1", "2", "3", "4", "0")
STATUS_PESANAN_TUPLE = ("Diterima", "Diproses", "Selesai", "Diambil")
STATUS_BAYAR_TUPLE = ("Belum Lunas", "Lunas")
LEBAR_GARIS = 75

KUNCI_WAJIB_PEMBAYARAN = {"id_pembayaran", "no_transaksi", "total_tagihan"}
KUNCI_WAJIB_PESANAN = {"berat_kg", "total"}


def format_rupiah(angka):
    try:
        nilai = int(round(float(angka)))
        return "Rp " + f"{nilai:,}".replace(",", ".")
    except (ValueError, TypeError):
        return "Rp 0"

def cetak_garis(panjang=LEBAR_GARIS, karakter="="):
    print(karakter * panjang)

def input_teks_valid(pesan, boleh_kosong=False):
    while True:
        teks = input(pesan).strip()
        if teks or boleh_kosong:
            return teks
        print("[PERINGATAN] Input tidak boleh kosong! Silakan coba lagi.")

def input_pilihan_menu(pesan, opsi_valid):
    while True:
        pilihan = input(pesan).strip()
        if pilihan in opsi_valid:
            return pilihan
        print(f"[PERINGATAN] Pilihan tidak valid! Masukkan salah satu dari {list(opsi_valid)}.")

def konfirmasi_tindakan(pesan):
    jawaban_ya = {"y", "ya", "yes"}
    jawaban_tidak = {"t", "tidak", "n", "no"}
    while True:
        jawaban = input(f"{pesan} (y/n): ").strip().lower()
        if jawaban in jawaban_ya:
            return True
        if jawaban in jawaban_tidak:
            return False
        print("[PERINGATAN] Jawab dengan 'y' (ya) atau 'n' (tidak)!")

def _baca_file_json(path_file, tipe_data_kosong=list):
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
    try:
        folder_tujuan = os.path.dirname(path_file)
        if folder_tujuan and not os.path.exists(folder_tujuan):
            os.makedirs(folder_tujuan, exist_ok=True)

        with open(path_file, "w", encoding="utf-8") as berkas:
            json.dump(data, berkas, indent=4, ensure_ascii=False)
        return True
    except (OSError, IOError) as err:
        print(f"[ERROR] Gagal menyimpan ke '{os.path.basename(path_file)}': {err}")
        return False


def simpan_data_pelanggan(daftar_pelanggan):
    sukses = _tulis_file_json(FILE_PELANGGAN, daftar_pelanggan)
    return sukses

def simpan_data_layanan(daftar_layanan):
    sukses = _tulis_file_json(FILE_LAYANAN, daftar_layanan)
    return sukses

def simpan_data_pesanan(daftar_pesanan):
    sukses = _tulis_file_json(FILE_PESANAN, daftar_pesanan)
    return sukses

def simpan_riwayat_pembayaran(riwayat_pembayaran):
    sukses = _tulis_file_json(FILE_PEMBAYARAN, riwayat_pembayaran)
    return sukses

def simpan_semua_data(daftar_pelanggan, daftar_layanan, daftar_pesanan, riwayat_pembayaran):
    s1 = simpan_data_pelanggan(daftar_pelanggan)
    s2 = simpan_data_layanan(daftar_layanan)
    s3 = simpan_data_pesanan(daftar_pesanan)
    s4 = simpan_riwayat_pembayaran(riwayat_pembayaran)
    return all((s1, s2, s3, s4))


def muat_data_pelanggan():
    data = _baca_file_json(FILE_PELANGGAN, list)
    return data if isinstance(data, list) else []

def muat_data_layanan():
    data = _baca_file_json(FILE_LAYANAN, list)
    return data if isinstance(data, list) else []

def muat_data_pesanan():
    data = _baca_file_json(FILE_PESANAN, list)
    return data if isinstance(data, list) else []

def muat_riwayat_pembayaran():
    data = _baca_file_json(FILE_PEMBAYARAN, list)
    return data if isinstance(data, list) else []

def muat_semua_data():
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

baca_data_pelanggan = muat_data_pelanggan
baca_data_layanan = muat_data_layanan
baca_data_pesanan = muat_data_pesanan
baca_riwayat_pembayaran = muat_riwayat_pembayaran


def _ambil_kode_pesanan(pesanan_dict):
    return pesanan_dict.get("kode") or pesanan_dict.get("no_transaksi") or "-"

def _ambil_nama_pelanggan(pesanan_dict, daftar_pelanggan=None):
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
    status = pesanan_dict.get("status_bayar", "")
    if isinstance(status, str) and status.lower() == "lunas":
        return "Lunas"
 
    if riwayat_pembayaran:
        kode = _ambil_kode_pesanan(pesanan_dict).upper()
        set_trx_lunas = {
            bayar.get("no_transaksi", "").upper()
            for bayar in riwayat_pembayaran
            if bayar.get("no_transaksi")
        }
        if kode in set_trx_lunas:
            return "Lunas"

    return "Belum Lunas"


def tampilkan_riwayat_pesanan(daftar_pesanan, riwayat_pembayaran=None, daftar_pelanggan=None):
    print()
    cetak_garis(85)
    print("                    RIWAYAT SELURUH PESANAN LAUNDRY")
    cetak_garis(85)

    if not daftar_pesanan:
        print("  [INFO] Belum ada data riwayat pesanan yang tercatat.")
        cetak_garis(85)
        return

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
    print("\n--- CARI RIWAYAT PESANAN PELANGGAN ---")
    if not daftar_pesanan:
        print("[INFO] Belum ada riwayat pesanan untuk dicari.")
        return

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


def tampilkan_riwayat_pembayaran(riwayat_pembayaran):
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
    total_biaya_kotor = 0.0
    total_diskon = 0.0
    total_pendapatan_bersih = 0.0
    jumlah_transaksi = len(riwayat_pembayaran)

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

            if layanan not in pendapatan_per_layanan:
                pendapatan_per_layanan[layanan] = {"frekuensi": 0, "total": 0.0}
            pendapatan_per_layanan[layanan]["frekuensi"] += 1
            pendapatan_per_layanan[layanan]["total"] += tagihan

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

    if stats["jumlah_transaksi"] > 0:
        if konfirmasi_tindakan("Apakah Anda ingin mengekspor laporan pendapatan ke file .txt?"):
            ekspor_laporan_pendapatan(stats)


def ekspor_laporan_pendapatan(stats):
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


def tampilkan_header_menu():
    print()
    cetak_garis(56)
    print("       FITUR 5: RIWAYAT DAN PENYIMPANAN DATA")
    cetak_garis(56)
    print("  1. Tampilkan Seluruh Riwayat Pesanan")
    print("  2. Cari Riwayat Pesanan Berdasarkan Pelanggan")
    print("  3. Tampilkan Riwayat Pembayaran Kasir")
    print("  4. Tampilkan Total Pendapatan Laundry")
    print("  0. Kembali ke Menu Utama")
    cetak_garis(56)


def menu_riwayat(daftar_pelanggan=None, daftar_layanan=None, daftar_pesanan=None, riwayat_pembayaran=None): 
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
        pilihan = input_pilihan_menu("Pilih menu (0-4): ", PILIHAN_MENU_RIWAYAT)
        if pilihan == "1":
            tampilkan_riwayat_pesanan(daftar_pesanan, riwayat_pembayaran, daftar_pelanggan)
        elif pilihan == "2":
            cari_riwayat_pelanggan(daftar_pesanan, riwayat_pembayaran, daftar_pelanggan)
        elif pilihan == "3":
            tampilkan_riwayat_pembayaran(riwayat_pembayaran)
        elif pilihan == "4":
            tampilkan_total_pendapatan(riwayat_pembayaran, daftar_pesanan)
        elif pilihan == "0":
            print("\n[INFO] Kembali ke menu utama...")
            break


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
