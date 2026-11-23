"""
================================================================================
KELOMPOK C — SISTEM MANAJEMEN LAUNDRY
File Utama: main.py
================================================================================
Aplikasi Terminal / Command Line Interface (CLI) untuk manajemen laundry:
1. Pengelolaan Pelanggan
2. Pengelolaan Layanan
3. Pengelolaan Pesanan
4. Transaksi & Pembayaran Kasir
5. Riwayat dan Penyimpanan Data
================================================================================
"""

import os
import sys

# Menambahkan direktori 'Modul' ke sys.path agar impor modul berjalan lancar
file_path_bersih = __file__.strip("\"' ")
DIREKTORI_UTAMA = os.path.dirname(os.path.abspath(file_path_bersih))
DIREKTORI_MODUL = os.path.join(DIREKTORI_UTAMA, "Modul")

if os.path.exists(DIREKTORI_MODUL) and DIREKTORI_MODUL not in sys.path:
    sys.path.insert(0, DIREKTORI_MODUL)
if DIREKTORI_UTAMA not in sys.path:
    sys.path.insert(0, DIREKTORI_UTAMA)

# Impor Modul Aplikasi
try:
    import penyimpanan_riwayat
    import pelanggan
    import layanan
    import pesanan
    import pembayaran
except ImportError as e:
    import traceback
    print(f"[ERROR] Gagal memuat modul: {e}")
    traceback.print_exc()
    sys.exit(1)


def cetak_banner():
    """Menampilkan banner selamat datang di terminal."""
    print("=" * 65)
    print("      SELAMAT DATANG DI SISTEM MANAJEMEN LAUNDRY (KELOMPOK C)    ")
    print("=" * 65)


def tampilkan_menu_utama():
    """Menampilkan pilihan menu utama sistem laundry."""
    print("\n" + "=" * 50)
    print("                  MENU UTAMA")
    print("=" * 50)
    print("  1. Manajemen Pelanggan (Kelola Pelanggan)")
    print("  2. Manajemen Layanan (Tarif & Estimasi)")
    print("  3. Manajemen Pesanan (Buat & Pantau Status)")
    print("  4. Transaksi & Pembayaran Kasir (Hitung Diskon)")
    print("  5. Riwayat dan Penyimpanan Data (Laporan & Kas)")
    print("  0. Simpan Seluruh Data & Keluar")
    print("=" * 50)


def main():
    """Fungsi utama pengatur alur sistem manajemen laundry."""
    cetak_banner()

    # Membaca kembali data ketika aplikasi dijalankan (Ketentuan Fitur 5)
    print("[INFO] Membaca data tersimpan dari file...")
    data_sistem = penyimpanan_riwayat.muat_semua_data()
    print(
        f"[INFO] Data berhasil dimuat: "
        f"{len(data_sistem['pelanggan'])} Pelanggan, "
        f"{len(data_sistem['layanan'])} Layanan, "
        f"{len(data_sistem['pesanan'])} Pesanan, "
        f"{len(data_sistem['pembayaran'])} Riwayat Pembayaran.\n"
    )

    opsi_menu_utama = ("1", "2", "3", "4", "5", "0")

    while True:
        tampilkan_menu_utama()
        pilihan = input("Pilih Menu (0-5): ").strip()

        if pilihan not in opsi_menu_utama:
            print("[PERINGATAN] Pilihan tidak valid! Silakan masukkan angka 0 sampai 5.")
            continue

        if pilihan == "1":
            # 1. Manajemen Pelanggan
            pelanggan.menu_pelanggan()
            # Sinkronisasi data pelanggan terbaru
            data_sistem["pelanggan"] = penyimpanan_riwayat.muat_data_pelanggan()

        elif pilihan == "2":
            # 2. Manajemen Layanan
            layanan.main()
            # Sinkronisasi data layanan terbaru
            data_sistem["layanan"] = penyimpanan_riwayat.muat_data_layanan()

        elif pilihan == "3":
            # 3. Manajemen Pesanan (memerlukan data layanan terbaru)
            data_sistem["layanan"] = penyimpanan_riwayat.muat_data_layanan()
            pesanan.menu_pesanan(data_sistem["layanan"])
            # Sinkronisasi data pesanan terbaru
            data_sistem["pesanan"] = penyimpanan_riwayat.muat_data_pesanan()

        elif pilihan == "4":
            # 4. Transaksi Pembayaran Kasir
            data_sistem["pelanggan"] = penyimpanan_riwayat.muat_data_pelanggan()
            data_sistem["layanan"] = penyimpanan_riwayat.muat_data_layanan()
            data_sistem["pesanan"] = penyimpanan_riwayat.muat_data_pesanan()
            data_sistem["pembayaran"] = penyimpanan_riwayat.muat_riwayat_pembayaran()

            pembayaran.menu_pembayaran(
                daftar_pelanggan=data_sistem["pelanggan"],
                daftar_layanan=data_sistem["layanan"],
                daftar_pesanan=data_sistem["pesanan"],
                riwayat_pembayaran=data_sistem["pembayaran"],
            )

        elif pilihan == "5":
            # 5. Riwayat dan Penyimpanan Data
            data_sistem["pelanggan"] = penyimpanan_riwayat.muat_data_pelanggan()
            data_sistem["layanan"] = penyimpanan_riwayat.muat_data_layanan()
            data_sistem["pesanan"] = penyimpanan_riwayat.muat_data_pesanan()
            data_sistem["pembayaran"] = penyimpanan_riwayat.muat_riwayat_pembayaran()

            penyimpanan_riwayat.menu_riwayat(
                daftar_pelanggan=data_sistem["pelanggan"],
                daftar_layanan=data_sistem["layanan"],
                daftar_pesanan=data_sistem["pesanan"],
                riwayat_pembayaran=data_sistem["pembayaran"],
            )

        elif pilihan == "0":
            # 0. Simpan & Keluar
            print("\n[INFO] Menyimpan seluruh data sistem...")
            penyimpanan_riwayat.simpan_semua_data(
                daftar_pelanggan=data_sistem["pelanggan"],
                daftar_layanan=data_sistem["layanan"],
                daftar_pesanan=data_sistem["pesanan"],
                riwayat_pembayaran=data_sistem["pembayaran"],
            )
            print("[INFO] Seluruh data berhasil disimpan dengan aman.")
            print("Terima kasih telah menggunakan Sistem Manajemen Laundry!\n")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\n[INFO] Program dihentikan. Data yang tersimpan tetap aman di file JSON.")
