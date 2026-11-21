import json
import os

import layanan  # file 1: dipakai untuk validasi, tampilan, dan data layanan

# DATA AWAL
FILE_PESANAN = os.path.join(layanan.FOLDER_PROGRAM, "pesanan.json")

# tuple: urutan status pesanan
STATUS_PESANAN = ("Diterima", "Diproses", "Selesai", "Diambil")

# set: kunci yang wajib ada di setiap pesanan
KUNCI_PESANAN = {"kode", "pelanggan", "layanan", "harga_per_kg", "berat_kg", "total", "status"}


# VALIDASI INPUT
def input_berat(pesan):
    while True:
        teks = input(pesan).strip().replace(",", ".")
        try:
            berat = float(teks)
        except ValueError:
            print("Berat harus berupa angka (contoh: 2.5), coba lagi.")
            continue

        if berat <= 0:
            print("Berat harus lebih dari 0.")
        elif berat > 1000:
            print("Berat tidak boleh lebih dari 1000 kg.")
        else:
            return round(berat, 2)


def input_telepon(pesan):
    while True:
        nomor = input(pesan).strip().replace(" ", "").replace("-", "")

        if not nomor.isdigit():
            print("Nomor telepon hanya boleh berisi angka (contoh: 081234567890).")
        elif len(nomor) < 9 or len(nomor) > 15:
            print("Nomor telepon harus 9 sampai 15 digit.")
        else:
            return nomor


# PENYIMPANAN DATA (FILE JSON)
def simpan_pesanan(data):
    try:
        with open(FILE_PESANAN, "w") as file:
            json.dump(data, file, indent=4)
        return True
    except OSError as error:
        print(f"Gagal menyimpan data pesanan: {error}")
        return False


def muat_pesanan():
    try:
        with open(FILE_PESANAN, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except (ValueError, OSError):
        print("File pesanan.json tidak bisa dibaca, data dimulai dari kosong.")
        return []

    # pastikan isi file berupa list dan setiap pesanan punya kunci yang wajib
    if not isinstance(data, list):
        return []
    for pesanan in data:
        if not isinstance(pesanan, dict) or not KUNCI_PESANAN <= set(pesanan):
            print("Format pesanan.json tidak sesuai, data dimulai dari kosong.")
            return []
    return data


# FUNGSI BANTU
def buat_kode(data):
    return f"P{len(data) + 1:04d}"  # P001, P002, ...


def hitung_total(harga_per_kg, berat_kg):
    return int(round(harga_per_kg * berat_kg))


def pilih_nomor_pesanan(data, pesan):
    """Mengembalikan indeks list, atau None kalau batal."""
    nomor = layanan.input_angka(pesan + " (0 = batal): ", 0, len(data))
    if nomor == 0:
        return None
    return nomor - 1


# TAMPILAN
def tampilkan_daftar_pesanan(data):
    print()
    layanan.cetak_garis()
    print("DAFTAR PESANAN LAUNDRY")
    layanan.cetak_garis()

    if len(data) == 0:
        print("Belum ada pesanan.")
        layanan.cetak_garis()
        return

    print(f"{'No':<4}{'Kode':<6}{'Pelanggan':<16}{'Layanan':<14}{'Berat':<8}{'Total':<13}Status")
    print("-" * 70)

    nomor = 1
    for pesanan in data:
        berat = f"{pesanan['berat_kg']} kg"
        total = layanan.format_rupiah(pesanan["total"])
        print(
            f"{nomor:<4}{pesanan['kode']:<6}{pesanan['pelanggan'][:15]:<16}"
            f"{pesanan['layanan'][:13]:<14}{berat:<8}{total:<13}{pesanan['status']}"
        )
        nomor = nomor + 1

    print("-" * 70)


def tampilkan_detail(pesanan):
    print()
    layanan.cetak_garis()
    print(f"DETAIL PESANAN {pesanan['kode']}")
    layanan.cetak_garis()
    print(f"Nama Pelanggan : {pesanan['pelanggan']}")
    print(f"No. Telepon    : {pesanan.get('telepon', '-')}")
    print(f"Jenis Layanan  : {pesanan['layanan']}")
    print(f"Harga per kg   : {layanan.format_rupiah(pesanan['harga_per_kg'])}")
    print(f"Berat Pakaian  : {pesanan['berat_kg']} kg")
    print(f"Total Biaya    : {layanan.format_rupiah(pesanan['total'])}")
    print(f"Status         : {pesanan['status']}")
    layanan.cetak_garis()


# FITUR PESANAN
def tambah_pesanan(data, data_layanan):
    print("\n--- TAMBAH PESANAN ---")
    if len(data_layanan) == 0:
        print("Belum ada layanan. Tambahkan layanan dulu di menu Kelola Layanan.")
        return

    pelanggan = layanan.input_teks("Nama pelanggan        : ")
    telepon = input_telepon("No. telepon          : ")

    layanan.tampilkan_daftar(data_layanan)  # daftar layanan terbaru
    indeks = layanan.pilih_nomor_layanan(data_layanan, "Pilih nomor layanan")
    if indeks is None:
        print("Dibatalkan.")
        return
    jenis = data_layanan[indeks]

    berat = input_berat("Berat pakaian (kg)    : ")
    total = hitung_total(jenis["harga"], berat)

    print(f"\nLayanan : {jenis['nama']} ({layanan.format_rupiah(jenis['harga'])}/kg)")
    print(f"Total biaya: {layanan.format_rupiah(total)}")
    if not layanan.konfirmasi("Simpan pesanan ini?"):
        print("Pesanan dibatalkan.")
        return

    pesanan = {
        "kode": buat_kode(data),
        "pelanggan": pelanggan,
        "telepon": telepon,
        "layanan": jenis["nama"],
        "harga_per_kg": jenis["harga"],
        "berat_kg": berat,
        "total": total,
        "status": STATUS_PESANAN[0],
    }
    data.append(pesanan)

    if simpan_pesanan(data):
        print(f"Pesanan {pesanan['kode']} berhasil disimpan.")


def ubah_status(data):
    print("\n--- UBAH STATUS PESANAN ---")
    if len(data) == 0:
        print("Belum ada pesanan.")
        return

    tampilkan_daftar_pesanan(data)
    indeks = pilih_nomor_pesanan(data, "Nomor pesanan")
    if indeks is None:
        print("Dibatalkan.")
        return

    pesanan = data[indeks]
    print(f"\nStatus saat ini: {pesanan['status']}")
    nomor = 1
    for status in STATUS_PESANAN:
        print(f"{nomor}. {status}")
        nomor = nomor + 1

    pilihan = layanan.input_angka("Pilih status baru (0 = batal): ", 0, len(STATUS_PESANAN))
    if pilihan == 0:
        print("Dibatalkan.")
        return

    pesanan["status"] = STATUS_PESANAN[pilihan - 1]
    if simpan_pesanan(data):
        print(f"Status pesanan {pesanan['kode']} diubah menjadi '{pesanan['status']}'.")


def lihat_detail(data):
    print("\n--- DETAIL PESANAN ---")
    if len(data) == 0:
        print("Belum ada pesanan.")
        return

    tampilkan_daftar_pesanan(data)
    indeks = pilih_nomor_pesanan(data, "Nomor pesanan")
    if indeks is None:
        print("Dibatalkan.")
        return

    tampilkan_detail(data[indeks])


# SUBMENU PESANAN (dipanggil dari main.py)
def tampilkan_menu_pesanan():
    print()
    print("================================")
    print("MANAJEMEN PESANAN LAUNDRY")
    print("================================")
    print("1. Tambah Pesanan")
    print("2. Lihat Daftar Pesanan")
    print("3. Lihat Detail Pesanan")
    print("4. Ubah Status Pesanan")
    print("0. Kembali")
    print("================================")


def menu_pesanan(data_layanan):
    data = muat_pesanan()

    while True:
        tampilkan_menu_pesanan()
        pilihan = layanan.input_angka("Pilih menu: ", 0, 4)

        if pilihan == 1:
            tambah_pesanan(data, data_layanan)
        elif pilihan == 2:
            tampilkan_daftar_pesanan(data)
        elif pilihan == 3:
            lihat_detail(data)
        elif pilihan == 4:
            ubah_status(data)
        else:
            break
# bagian else diubah ke menu utama 

# Jika file ini dijalankan langsung
if __name__ == "__main__":
    try:
        menu_pesanan(layanan.muat_data())
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgram dihentikan. Data yang sudah disimpan tetap aman.")














# import json
# import os

# import layanan  # file 1: dipakai ulang untuk validasi, tampilan, dan data layanan


# # PENGATURAN DAN DATA AWAL

# FILE_PESANAN = os.path.join(layanan.FOLDER_PROGRAM, "pelanggan.json")

# # tuple berisi urutan status pesanan
# STATUS_PESANAN = ("Diterima", "Diproses", "Selesai", "Diambil")

# # set berisi kunci yang wajib ada di setiap pesanan
# # ("telepon" sengaja tidak wajib agar data lama tanpa telepon tetap terbaca)
# KUNCI_PESANAN = {"kode", "pelanggan", "layanan", "harga_per_kg", "berat_kg", "total", "status"}


# # VALIDASI INPUT

# def input_berat(pesan, maksimal=100):
#     """Minta berat dalam kg. Boleh desimal (contoh: 2.5 atau 2,5)."""
#     while True:
#         teks = input(pesan).strip().replace(",", ".")
#         try:
#             berat = float(teks)
#         except ValueError:
#             print("Berat harus berupa angka (contoh: 2.5), coba lagi.")
#             continue

#         if berat != berat or berat in (float("inf"), float("-inf")):
#             print("Berat tidak valid, coba lagi.")
#         elif berat <= 0:
#             print("Berat harus lebih dari 0.")
#         elif berat > maksimal:
#             print(f"Berat tidak boleh lebih dari {maksimal} kg.")
#         else:
#             return round(berat, 2)


# def input_telepon(pesan):
#     """Minta nomor telepon. Boleh diawali + dan boleh memakai spasi/strip."""
#     while True:
#         teks = input(pesan).strip()
#         nomor = teks.replace(" ", "").replace("-", "")
#         isi = nomor[1:] if nomor.startswith("+") else nomor

#         if not isi.isdigit():
#             print("Nomor telepon hanya boleh berisi angka (contoh: 081234567890).")
#         elif not 9 <= len(isi) <= 15:
#             print("Nomor telepon harus 9 sampai 15 digit.")
#         else:
#             return nomor


# # PENYIMPANAN DATA (FILE JSON)

# def simpan_pesanan(data):
#     try:
#         with open(FILE_PESANAN, "w") as file:
#             json.dump(data, file, indent=4)
#         return True
#     except OSError as error:
#         print(f"Gagal menyimpan data pesanan: {error}")
#         return False


# def pesanan_valid(data):
#     if not isinstance(data, list):
#         return False
#     for pesanan in data:
#         if not isinstance(pesanan, dict) or not KUNCI_PESANAN <= set(pesanan):
#             return False
#     return True


# def muat_pesanan():
#     try:
#         with open(FILE_PESANAN, "r") as file:
#             data = json.load(file)
#         if not pesanan_valid(data):
#             raise ValueError("Isi file tidak sesuai format")
#         return data

#     except FileNotFoundError:
#         return []

#     except ValueError:  # termasuk json.JSONDecodeError
#         print("File pelanggan rusak. File lama disimpan sebagai pelanggan.json.rusak.")
#         try:
#             os.replace(FILE_PESANAN, FILE_PESANAN + ".rusak")
#         except OSError:
#             pass
#         return []

#     except OSError as error:
#         print(f"Gagal membaca file pelanggan: {error}")
#         return []


# # FUNGSI BANTU

# def buat_kode(data):
#     """Buat kode pesanan berikutnya, contoh: P001, P002, ..."""
#     nomor_terpakai = [int(item["kode"][1:]) for item in data if item["kode"][1:].isdigit()]
#     nomor_baru = max(nomor_terpakai, default=0) + 1
#     return f"P{nomor_baru:03d}"


# def hitung_total(harga_per_kg, berat_kg):
#     """Total biaya = harga per kg x berat (dibulatkan ke rupiah)."""
#     return int(round(harga_per_kg * berat_kg))


# def pilih_nomor_pesanan(data, pesan):
#     """Minta nomor pesanan. Mengembalikan indeks list, atau None kalau batal."""
#     nomor = layanan.input_angka(pesan + " (0 = batal): ", 0, len(data))
#     if nomor == 0:
#         return None
#     return nomor - 1


# # TAMPILAN

# def tampilkan_daftar_pesanan(data):
#     """Tampilkan seluruh pesanan dalam bentuk tabel."""
#     print()
#     layanan.cetak_garis()
#     print("DAFTAR PESANAN LAUNDRY")
#     layanan.cetak_garis()

#     if len(data) == 0:
#         print("Belum ada pesanan.")
#         layanan.cetak_garis()
#         return

#     print(f"{'No':<4}{'Kode':<6}{'Pelanggan':<16}{'Layanan':<14}{'Berat':<8}{'Total':<13}Status")
#     print("-" * 70)

#     nomor = 1
#     for pesanan in data:
#         berat = f"{pesanan['berat_kg']} kg"
#         total = layanan.format_rupiah(pesanan["total"])
#         print(
#             f"{nomor:<4}{pesanan['kode']:<6}{pesanan['pelanggan'][:15]:<16}"
#             f"{pesanan['layanan'][:13]:<14}{berat:<8}{total:<13}{pesanan['status']}"
#         )
#         nomor = nomor + 1

#     print("-" * 70)


# def tampilkan_detail(pesanan):
#     print()
#     layanan.cetak_garis()
#     print(f"DETAIL PESANAN {pesanan['kode']}")
#     layanan.cetak_garis()
#     print(f"Nama Pelanggan : {pesanan['pelanggan']}")
#     print(f"No. Telepon    : {pesanan.get('telepon', '-')}")
#     print(f"Jenis Layanan  : {pesanan['layanan']}")
#     print(f"Harga per kg   : {layanan.format_rupiah(pesanan['harga_per_kg'])}")
#     print(f"Berat Pakaian  : {pesanan['berat_kg']} kg")
#     print(f"Total Biaya    : {layanan.format_rupiah(pesanan['total'])}")
#     print(f"Status         : {pesanan['status']}")
#     layanan.cetak_garis()


# # FITUR PESANAN

# def tambah_pesanan(data, data_layanan):
#     print("\n--- TAMBAH PESANAN ---")
#     if len(data_layanan) == 0:
#         print("Belum ada layanan. Tambahkan layanan dulu di menu Kelola Layanan.")
#         return

#     pelanggan = layanan.input_teks("Nama pelanggan        : ")
#     telepon = input_telepon("No. telepon          : ")

#     # daftar layanan terbaru (hasil tambah/ubah/hapus di menu Kelola Layanan)
#     layanan.tampilkan_daftar(data_layanan)
#     indeks = layanan.pilih_nomor_layanan(data_layanan, "Pilih nomor layanan")
#     if indeks is None:
#         print("Dibatalkan.")
#         return
#     jenis = data_layanan[indeks]

#     berat = input_berat("Berat pakaian (kg)    : ")
#     total = hitung_total(jenis["harga"], berat)

#     print(f"\nLayanan : {jenis['nama']} ({layanan.format_rupiah(jenis['harga'])}/kg)")
#     print(f"Total biaya: {layanan.format_rupiah(total)}")
#     if not layanan.konfirmasi("Simpan pesanan ini?"):
#         print("Pesanan dibatalkan.")
#         return

#     pesanan = {
#         "kode": buat_kode(data),
#         "pelanggan": pelanggan,
#         "telepon": telepon,
#         "layanan": jenis["nama"],
#         "harga_per_kg": jenis["harga"],  # harga disalin agar pesanan lama tidak berubah
#         "berat_kg": berat,
#         "total": total,
#         "status": STATUS_PESANAN[0],
#     }
#     data.append(pesanan)

#     if simpan_pesanan(data):
#         print(f"Pesanan {pesanan['kode']} berhasil disimpan.")


# def ubah_status(data):
#     print("\n--- UBAH STATUS PESANAN ---")
#     if len(data) == 0:
#         print("Belum ada pesanan.")
#         return

#     tampilkan_daftar_pesanan(data)
#     indeks = pilih_nomor_pesanan(data, "Nomor pesanan")
#     if indeks is None:
#         print("Dibatalkan.")
#         return

#     pesanan = data[indeks]
#     print(f"\nStatus saat ini: {pesanan['status']}")
#     for nomor, status in enumerate(STATUS_PESANAN, start=1):
#         print(f"{nomor}. {status}")

#     pilihan = layanan.input_angka("Pilih status baru (0 = batal): ", 0, len(STATUS_PESANAN))
#     if pilihan == 0:
#         print("Dibatalkan.")
#         return

#     pesanan["status"] = STATUS_PESANAN[pilihan - 1]
#     if simpan_pesanan(data):
#         print(f"Status pesanan {pesanan['kode']} diubah menjadi '{pesanan['status']}'.")


# def lihat_detail(data):
#     print("\n--- DETAIL PESANAN ---")
#     if len(data) == 0:
#         print("Belum ada pesanan.")
#         return

#     tampilkan_daftar_pesanan(data)
#     indeks = pilih_nomor_pesanan(data, "Nomor pesanan")
#     if indeks is None:
#         print("Dibatalkan.")
#         return

#     tampilkan_detail(data[indeks])


# # SUBMENU PESANAN (dipanggil dari main.py)

# def tampilkan_menu_pesanan():
#     print()
#     layanan.cetak_garis()
#     print("MANAJEMEN PESANAN LAUNDRY")
#     layanan.cetak_garis()
#     print("1. Tambah Pesanan")
#     print("2. Lihat Daftar Pesanan")
#     print("3. Lihat Detail Pesanan")
#     print("4. Ubah Status Pesanan")
#     print("0. Kembali")
#     layanan.cetak_garis()


# def menu_pesanan(data_layanan):
#     """Submenu pesanan. Dipanggil dari main.py lewat: pesanan.menu_pesanan(data_layanan)"""
#     data = muat_pesanan()  # data dibaca dari pelanggan.json

#     while True:
#         tampilkan_menu_pesanan()
#         pilihan = layanan.input_angka("Pilih menu: ", 0, 4)

#         if pilihan == 1:
#             tambah_pesanan(data, data_layanan)
#         elif pilihan == 2:
#             tampilkan_daftar_pesanan(data)
#         elif pilihan == 3:
#             lihat_detail(data)
#         elif pilihan == 4:
#             ubah_status(data)
#         else:  # pilihan == 0
#             break


# # Jika file ini dijalankan langsung, layanan dibaca dari layanan.json.
# if __name__ == "__main__":
#     try:
#         menu_pesanan(layanan.muat_data())
#     except (KeyboardInterrupt, EOFError):
#         print("\n\nProgram dihentikan. Data yang sudah disimpan tetap aman.")