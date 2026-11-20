import layanan  # file 1
import pesanan  # file 2


def menu_layanan(data_layanan):
    """Submenu layanan: memakai fungsi-fungsi dari file 1 tanpa mengubahnya."""
    while True:
        layanan.tampilkan_menu()
        pilihan = layanan.input_angka("Pilih menu: ", 0, 4)

        if pilihan == 1:
            layanan.tampilkan_daftar(data_layanan)
        elif pilihan == 2:
            layanan.tambah_layanan(data_layanan)
        elif pilihan == 3:
            layanan.ubah_layanan(data_layanan)
        elif pilihan == 4:
            layanan.hapus_layanan(data_layanan)
        else:  # pilihan == 0
            break


def tampilkan_menu_utama():
    print()
    layanan.cetak_garis()
    print("APLIKASI LAUNDRY")
    layanan.cetak_garis()
    print("1. Kelola Layanan")
    print("2. Kelola Pesanan")
    print("0. Keluar")
    layanan.cetak_garis()


def main():
    data_layanan = layanan.muat_data()  # data layanan dibaca dari layanan.json

    while True:
        tampilkan_menu_utama()
        pilihan = layanan.input_angka("Pilih menu: ", 0, 2)

        if pilihan == 1:
            menu_layanan(data_layanan)
        elif pilihan == 2:
            pesanan.menu_pesanan(data_layanan)  # list yang sama, jadi selalu terbaru
        else:  # pilihan == 0
            break

    print("\nTerima kasih, sampai jumpa!")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgram dihentikan. Data yang sudah disimpan tetap aman.")