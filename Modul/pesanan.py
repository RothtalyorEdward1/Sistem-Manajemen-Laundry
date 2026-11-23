
import json
import os
import layanan
from datetime import datetime


# ==========================================
# PENGATURAN DATA
# ==========================================

FOLDER_PROGRAM = os.path.dirname(os.path.abspath(__file__))

FILE_PESANAN = os.path.join(FOLDER_PROGRAM, "pesanan.json")
FILE_PELANGGAN = os.path.join(FOLDER_PROGRAM, "data_pelanggan.json")

STATUS_PESANAN = (
    "Diterima",
    "Diproses",
    "Selesai",
    "Diambil"
)

STATUS_VALID = {
    "diterima",
    "diproses",
    "selesai",
    "diambil"
}


# ==========================================
# MEMBACA DAN MENYIMPAN DATA
# ==========================================

def baca_pesanan():
    if not os.path.exists(FILE_PESANAN):
        return []

    try:
        with open(FILE_PESANAN, "r") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("Format data tidak sesuai.")

        return data

    except (json.JSONDecodeError, ValueError):
        print("File pesanan bermasalah.")
        return []

    except OSError as error:
        print("Gagal membaca data:", error)
        return []


def simpan_pesanan(data):
    try:
        with open(FILE_PESANAN, "w") as file:
            json.dump(data, file, indent=4)

        return True

    except OSError as error:
        print("Gagal menyimpan pesanan:", error)
        return False


def baca_pelanggan():
    try:
        with open(FILE_PELANGGAN, "r") as file:
            data = json.load(file)

        if not isinstance(data, list):
            return []

        return data

    except FileNotFoundError:
        print("Data pelanggan belum tersedia.")
        return []

    except (json.JSONDecodeError, OSError):
        print("Gagal membaca data pelanggan.")
        return []


# ==========================================
# VALIDASI INPUT
# ==========================================

def input_teks(pesan):
    while True:
        teks = input(pesan).strip()

        if teks != "":
            return teks

        print("Input tidak boleh kosong!")


def input_angka(pesan, minimal=0):
    while True:
        try:
            angka = int(input(pesan))

            if angka < minimal:
                print("Angka minimal adalah", minimal)
            else:
                return angka

        except ValueError:
            print("Masukkan angka bulat yang benar!")


def input_berat(pesan):
    while True:
        try:
            berat = float(input(pesan).replace(",", "."))

            if berat <= 0:
                print("Berat harus lebih dari 0 kg!")
            else:
                return berat

        except ValueError:
            print("Masukkan berat dalam angka!")


def format_rupiah(angka):
    return "Rp " + f"{angka:,.0f}".replace(",", ".")


# ==========================================
# MEMBUAT KODE PESANAN
# ==========================================

def buat_id_pesanan(data):
    id_terpakai = set()

    for pesanan in data:
        id_terpakai.add(pesanan["id"])

    nomor = 1

    while True:
        id_baru = f"ORD{nomor:03d}"

        if id_baru not in id_terpakai:
            return id_baru

        nomor += 1


# ==========================================
# MENCARI DATA
# ==========================================

def cari_pelanggan(data, kode):
    for pelanggan in data:
        if pelanggan["id"] == kode:
            return pelanggan

    return None


def cari_pesanan(data, kode):
    for pesanan in data:
        if pesanan["id"] == kode:
            return pesanan

    return None


# ==========================================
# MENAMPILKAN DAFTAR PESANAN
# ==========================================

def tampilkan_daftar_pesanan(data):

    print("\n" + "=" * 60)
    print("DAFTAR PESANAN LAUNDRY")
    print("=" * 60)

    if len(data) == 0:
        print("Belum ada pesanan.")
        return

    print(
        f"{'No':<5}"
        f"{'Kode':<12}"
        f"{'Pelanggan':<25}"
        f"{'Status':<15}"
    )

    print("-" * 60)

    for nomor, pesanan in enumerate(data, start=1):

        print(
            f"{nomor:<5}"
            f"{pesanan['id']:<12}"
            f"{pesanan['nama_pelanggan']:<25}"
            f"{pesanan['status']:<15}"
        )

    print("-" * 60)
    print("Total pesanan:", len(data))


# ==========================================
# MENAMBAH PESANAN
# ==========================================

def tambah_pesanan(data):

    print("\n" + "=" * 40)
    print("TAMBAH PESANAN LAUNDRY")
    print("=" * 40)

    # Mengambil data pelanggan
    pelanggan_data = baca_pelanggan()

    if len(pelanggan_data) == 0:
        print("Belum ada pelanggan. Tambahkan pelanggan dahulu.")
        return

    kode_pelanggan = input_teks(
        "Masukkan kode pelanggan: "
    ).upper()

    pelanggan = cari_pelanggan(
        pelanggan_data,
        kode_pelanggan
    )

    if pelanggan is None:
        print("Kode pelanggan tidak ditemukan!")
        return

    print("\nData Pelanggan")
    print("Kode    :", pelanggan["id"])
    print("Nama    :", pelanggan["nama"])
    print("Telepon :", pelanggan["telepon"])
    print("Alamat  :", pelanggan["alamat"])

    # Mengambil daftar layanan dari layanan.py
    daftar_layanan = layanan.muat_data()

    if len(daftar_layanan) == 0:
        print("Belum tersedia layanan laundry.")
        return

    daftar_barang = []

    # Menampilkan pilihan layanan
    while True:

        layanan.tampilkan_daftar(daftar_layanan)

        print("\nPilih layanan yang ingin ditambahkan.")
        print("Masukkan 0 jika sudah selesai memilih.")

        nomor = input_angka(
            "Nomor layanan: ",
            minimal=0
        )

        if nomor == 0:

            if len(daftar_barang) == 0:
                print("Minimal pilih satu layanan!")
                continue

            break

        if nomor > len(daftar_layanan):
            print("Nomor layanan tidak tersedia!")
            continue

        jenis = daftar_layanan[nomor - 1]

        berat = input_berat(
            "Masukkan berat pakaian (kg): "
        )

        subtotal = berat * jenis["harga"]

        # Menyimpan setiap layanan ke dalam list
        barang = {
            "nama_layanan": jenis["nama"],
            "berat": berat,
            "harga_per_kg": jenis["harga"],
            "estimasi_jam": jenis["estimasi_jam"],
            "subtotal": subtotal
        }

        daftar_barang.append(barang)

        print("\nLayanan berhasil ditambahkan!")
        print("Layanan :", jenis["nama"])
        print("Berat   :", berat, "kg")
        print("Subtotal:", format_rupiah(subtotal))

        tambah_lagi = input(
            "\nTambah jenis layanan lain? (y/t): "
        ).strip().lower()

        if tambah_lagi in ("t", "tidak", "n"):
            break

        elif tambah_lagi not in ("y", "ya"):
            print("Jawaban tidak valid.")

    # Membuat data pesanan
    pesanan_baru = {
        "id": buat_id_pesanan(data),
        "pelanggan_id": pelanggan["id"],
        "nama_pelanggan": pelanggan["nama"],
        "telepon": pelanggan["telepon"],
        "alamat": pelanggan["alamat"],
        "daftar_layanan": daftar_barang,
        "status": "Diterima",
        "tanggal": datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )
    }

    # Menyimpan transaksi
    data.append(pesanan_baru)

    if simpan_pesanan(data):

        print("\nPesanan berhasil disimpan!")
        tampilkan_struk(pesanan_baru)

    else:
        data.remove(pesanan_baru)


# ==========================================
# MENAMPILKAN STRUK
# ==========================================

def tampilkan_struk(pesanan):

    print("\n")
    print("=" * 50)
    print("              STRUK LAUNDRY")
    print("=" * 50)

    print("Kode Pesanan :", pesanan["id"])
    print("Kode Pelanggan:", pesanan["pelanggan_id"])
    print("Nama Pelanggan:", pesanan["nama_pelanggan"])
    print("Tanggal       :", pesanan["tanggal"])

    print("-" * 50)

    print("RINCIAN LAYANAN")

    for nomor, barang in enumerate(
        pesanan["daftar_layanan"], start=1
    ):

        print(f"\n{nomor}. {barang['nama_layanan']}")
        print("   Berat       :", barang["berat"], "kg")
        print(
            "   Harga/kg   :",
            format_rupiah(barang["harga_per_kg"])
        )
        print(
            "   Subtotal   :",
            format_rupiah(barang["subtotal"])
        )

    print("-" * 50)

    print("Status Pesanan   :", pesanan["status"])

    print("=" * 50)
    print("       TERIMA KASIH TELAH MENGGUNAKAN")
    print("             JASA LAUNDRY KAMI")
    print("=" * 50)


# ==========================================
# MELIHAT DETAIL PESANAN
# ==========================================

def detail_pesanan(data):

    print("\n--- DETAIL PESANAN ---")

    if len(data) == 0:
        print("Belum ada pesanan.")
        return

    kode = input_teks(
        "Masukkan kode pesanan: "
    ).upper()

    pesanan = cari_pesanan(data, kode)

    if pesanan is None:
        print("Pesanan tidak ditemukan!")
        return

    tampilkan_struk(pesanan)


# ==========================================
# MENGUBAH STATUS PESANAN
# ==========================================

def ubah_status(data):

    print("\n--- UBAH STATUS PESANAN ---")

    if len(data) == 0:
        print("Belum ada pesanan.")
        return

    tampilkan_daftar_pesanan(data)

    kode = input_teks(
        "\nMasukkan kode pesanan: "
    ).upper()

    pesanan = cari_pesanan(data, kode)

    if pesanan is None:
        print("Kode pesanan tidak ditemukan!")
        return

    print("\nKode Pesanan :", pesanan["id"])
    print("Pelanggan    :", pesanan["nama_pelanggan"])
    print("Status Lama  :", pesanan["status"])

    print("\nPilihan Status")

    for nomor, status in enumerate(
        STATUS_PESANAN, start=1
    ):
        print(f"{nomor}. {status}")

    pilihan = input_angka(
        "Pilih status baru: ",
        minimal=1
    )

    if pilihan > len(STATUS_PESANAN):
        print("Pilihan status tidak tersedia!")
        return

    status_baru = STATUS_PESANAN[pilihan - 1]

    if pesanan["status"].lower() == status_baru.lower():
        print("Status pesanan sudah menggunakan status tersebut.")
        return

    pesanan["status"] = status_baru

    if simpan_pesanan(data):
        print("\nStatus pesanan berhasil diubah!")
        print("Status baru:", status_baru)


# ==========================================
# MENGHAPUS PESANAN
# ==========================================

def hapus_pesanan(data):

    print("\n--- HAPUS PESANAN ---")

    if len(data) == 0:
        print("Belum ada pesanan.")
        return

    tampilkan_daftar_pesanan(data)

    kode = input_teks(
        "\nMasukkan kode pesanan yang dihapus: "
    ).upper()

    pesanan = cari_pesanan(data, kode)

    if pesanan is None:
        print("Pesanan tidak ditemukan!")
        return

    print("Pelanggan:", pesanan["nama_pelanggan"])

    yakin = input(
        "Yakin ingin menghapus pesanan? (y/t): "
    ).strip().lower()

    if yakin in ("y", "ya"):

        indeks = data.index(pesanan)
        data.pop(indeks)

        if simpan_pesanan(data):
            print("Pesanan berhasil dihapus.")

        else:
            data.insert(indeks, pesanan)

    else:
        print("Penghapusan dibatalkan.")


# ==========================================
# MENU UTAMA PESANAN
# ==========================================

def tampilkan_menu():

    print("\n" + "=" * 40)
    print("       MANAJEMEN PESANAN LAUNDRY")
    print("=" * 40)

    print("1. Tambah Pesanan")
    print("2. Lihat Daftar Pesanan")
    print("3. Lihat Detail Pesanan")
    print("4. Ubah Status Pesanan")
    print("5. Hapus Pesanan")
    print("0. Kembali")

    print("=" * 40)


# ==========================================
# PROGRAM UTAMA
# ==========================================

def main():

    data = baca_pesanan()

    while True:

        tampilkan_menu()

        pilihan = input(
            "Pilih menu: "
        ).strip()

        if pilihan == "1":

            tambah_pesanan(data)

        elif pilihan == "2":

            tampilkan_daftar_pesanan(data)

        elif pilihan == "3":

            detail_pesanan(data)

        elif pilihan == "4":

            ubah_status(data)

        elif pilihan == "5":

            hapus_pesanan(data)

        elif pilihan == "0":

            break

        else:

            print("Pilihan tidak valid!")

    print("\nKembali ke menu sebelumnya.")


if __name__ == "__main__":

    try:
        main()

    except (KeyboardInterrupt, EOFError):
        print("\nProgram dihentikan.")


# import json
# import os
# import layanan
# from datetime import datetime


# # ==========================================
# # PENGATURAN DATA
# # ==========================================

# FOLDER_PROGRAM = os.path.dirname(os.path.abspath(__file__))

# FILE_PESANAN = os.path.join(FOLDER_PROGRAM, "pesanan.json")
# FILE_PELANGGAN = os.path.join(FOLDER_PROGRAM, "data_pelanggan.json")

# STATUS_PESANAN = (
#     "Diterima",
#     "Diproses",
#     "Selesai",
#     "Diambil"
# )

# STATUS_VALID = {
#     "diterima",
#     "diproses",
#     "selesai",
#     "diambil"
# }


# # ==========================================
# # MEMBACA DAN MENYIMPAN DATA
# # ==========================================

# def baca_pesanan():
#     if not os.path.exists(FILE_PESANAN):
#         return []

#     try:
#         with open(FILE_PESANAN, "r") as file:
#             data = json.load(file)

#         if not isinstance(data, list):
#             raise ValueError("Format data tidak sesuai.")

#         return data

#     except (json.JSONDecodeError, ValueError):
#         print("File pesanan bermasalah.")
#         return []

#     except OSError as error:
#         print("Gagal membaca data:", error)
#         return []


# def simpan_pesanan(data):
#     try:
#         with open(FILE_PESANAN, "w") as file:
#             json.dump(data, file, indent=4)

#         return True

#     except OSError as error:
#         print("Gagal menyimpan pesanan:", error)
#         return False


# def baca_pelanggan():
#     try:
#         with open(FILE_PELANGGAN, "r") as file:
#             data = json.load(file)

#         if not isinstance(data, list):
#             return []

#         return data

#     except FileNotFoundError:
#         print("Data pelanggan belum tersedia.")
#         return []

#     except (json.JSONDecodeError, OSError):
#         print("Gagal membaca data pelanggan.")
#         return []


# # ==========================================
# # VALIDASI INPUT
# # ==========================================

# def input_teks(pesan):
#     while True:
#         teks = input(pesan).strip()

#         if teks != "":
#             return teks

#         print("Input tidak boleh kosong!")


# def input_angka(pesan, minimal=0):
#     while True:
#         try:
#             angka = int(input(pesan))

#             if angka < minimal:
#                 print("Angka minimal adalah", minimal)
#             else:
#                 return angka

#         except ValueError:
#             print("Masukkan angka bulat yang benar!")


# def input_berat(pesan):
#     while True:
#         try:
#             berat = float(input(pesan).replace(",", "."))

#             if berat <= 0:
#                 print("Berat harus lebih dari 0 kg!")
#             else:
#                 return berat

#         except ValueError:
#             print("Masukkan berat dalam angka!")


# def format_rupiah(angka):
#     return "Rp " + f"{angka:,.0f}".replace(",", ".")


# # ==========================================
# # MEMBUAT KODE UNIK PESANAN
# # ==========================================

# def buat_id_pesanan(data, pelanggan_data):

#     # Mengumpulkan seluruh ID yang sudah digunakan
#     id_terpakai = set()

#     for pelanggan in pelanggan_data:
#         id_terpakai.add(pelanggan["id"])

#     for pesanan in data:
#         id_terpakai.add(pesanan["id"])

#     nomor = 1

#     while True:

#         # Format kode sama dengan pelanggan.py
#         id_baru = f"P{nomor:03d}"

#         if id_baru not in id_terpakai:
#             return id_baru

#         nomor += 1


# # ==========================================
# # MENCARI DATA
# # ==========================================

# def cari_pelanggan(data, kode):

#     for pelanggan in data:
#         if pelanggan["id"] == kode:
#             return pelanggan

#     return None


# def cari_pesanan(data, kode):

#     for pesanan in data:
#         if pesanan["id"] == kode:
#             return pesanan

#     return None


# # ==========================================
# # MENAMPILKAN DAFTAR PESANAN
# # ==========================================

# def tampilkan_daftar_pesanan(data):

#     print("\n" + "=" * 75)
#     print("DAFTAR PESANAN LAUNDRY")
#     print("=" * 75)

#     if len(data) == 0:
#         print("Belum ada pesanan.")
#         return

#     print(
#         f"{'No':<5}"
#         f"{'Kode':<12}"
#         f"{'Pelanggan':<20}"
#         f"{'Total':<18}"
#         f"{'Status':<15}"
#     )

#     print("-" * 75)

#     for nomor, pesanan in enumerate(data, start=1):

#         print(
#             f"{nomor:<5}"
#             f"{pesanan['id']:<12}"
#             f"{pesanan['nama_pelanggan']:<20}"
#             f"{format_rupiah(pesanan['total']):<18}"
#             f"{pesanan['status']:<15}"
#         )

#     print("-" * 75)
#     print("Total pesanan:", len(data))


# # ==========================================
# # MENAMBAH PESANAN
# # ==========================================

# def tambah_pesanan(data):

#     print("\n" + "=" * 40)
#     print("TAMBAH PESANAN LAUNDRY")
#     print("=" * 40)

#     # Membaca data pelanggan
#     pelanggan_data = baca_pelanggan()

#     if len(pelanggan_data) == 0:
#         print("Belum ada pelanggan. Tambahkan pelanggan dahulu.")
#         return

#     # Meminta kode pelanggan
#     kode_pelanggan = input_teks(
#         "Masukkan kode pelanggan: "
#     ).upper()

#     pelanggan = cari_pelanggan(
#         pelanggan_data,
#         kode_pelanggan
#     )

#     if pelanggan is None:
#         print("Kode pelanggan tidak ditemukan!")
#         return

#     # Menampilkan informasi pelanggan
#     print("\nData Pelanggan")
#     print("Kode    :", pelanggan["id"])
#     print("Nama    :", pelanggan["nama"])
#     print("Telepon :", pelanggan["telepon"])
#     print("Alamat  :", pelanggan["alamat"])

#     # Mengambil daftar layanan dari layanan.py
#     daftar_layanan = layanan.muat_data()

#     if len(daftar_layanan) == 0:
#         print("Belum tersedia layanan laundry.")
#         return

#     daftar_barang = []

#     # Memilih lebih dari satu layanan
#     while True:

#         layanan.tampilkan_daftar(daftar_layanan)

#         print("\nPilih layanan yang ingin ditambahkan.")
#         print("Masukkan 0 jika sudah selesai memilih.")

#         nomor = input_angka(
#             "Nomor layanan: ",
#             minimal=0
#         )

#         if nomor == 0:

#             if len(daftar_barang) == 0:
#                 print("Minimal pilih satu layanan!")
#                 continue

#             break

#         if nomor > len(daftar_layanan):
#             print("Nomor layanan tidak tersedia!")
#             continue

#         jenis = daftar_layanan[nomor - 1]

#         # Memasukkan berat pakaian
#         berat = input_berat(
#             "Masukkan berat pakaian (kg): "
#         )

#         # Menghitung subtotal
#         subtotal = round(berat * jenis["harga"])

#         # Menyimpan layanan ke dalam list
#         barang = {
#             "nama_layanan": jenis["nama"],
#             "berat": berat,
#             "harga_per_kg": jenis["harga"],
#             "estimasi_jam": jenis["estimasi_jam"],
#             "subtotal": subtotal
#         }

#         daftar_barang.append(barang)

#         print("\nLayanan berhasil ditambahkan!")
#         print("Layanan :", jenis["nama"])
#         print("Berat   :", berat, "kg")
#         print("Subtotal:", format_rupiah(subtotal))

#         tambah_lagi = input(
#             "\nTambah jenis layanan lain? (y/t): "
#         ).strip().lower()

#         if tambah_lagi in ("t", "tidak", "n"):
#             break

#         elif tambah_lagi not in ("y", "ya"):
#             print("Jawaban tidak valid.")

#     # ======================================
#     # MENGHITUNG TOTAL PEMBAYARAN
#     # ======================================

#     total = 0

#     for barang in daftar_barang:
#         total += barang["subtotal"]

#     # Menampilkan rincian pembayaran
#     print("\n" + "=" * 45)
#     print("RINCIAN PEMBAYARAN")
#     print("=" * 45)

#     for nomor, barang in enumerate(daftar_barang, start=1):

#         print(f"\n{nomor}. {barang['nama_layanan']}")

#         print(
#             f"   {barang['berat']} kg x "
#             f"{format_rupiah(barang['harga_per_kg'])}"
#         )

#         print(
#             "   Subtotal:",
#             format_rupiah(barang["subtotal"])
#         )

#     print("-" * 45)
#     print("TOTAL:", format_rupiah(total))

#     # ======================================
#     # PROSES PEMBAYARAN
#     # ======================================

#     while True:

#         bayar = input_angka(
#             "Uang pembayaran: ",
#             minimal=0
#         )

#         if bayar < total:

#             print("Uang pembayaran tidak mencukupi!")

#             print(
#                 "Kekurangan:",
#                 format_rupiah(total - bayar)
#             )

#         else:
#             break

#     # Menghitung kembalian
#     kembalian = bayar - total

#     # ======================================
#     # MEMBUAT DATA PESANAN
#     # ======================================

#     pesanan_baru = {

#         "id": buat_id_pesanan(data, pelanggan_data),

#         "pelanggan_id": pelanggan["id"],

#         "nama_pelanggan": pelanggan["nama"],

#         "telepon": pelanggan["telepon"],

#         "alamat": pelanggan["alamat"],

#         "daftar_layanan": daftar_barang,

#         "total": total,

#         "bayar": bayar,

#         "kembalian": kembalian,

#         "status": "Diterima",

#         "tanggal": datetime.now().strftime(
#             "%d-%m-%Y %H:%M:%S"
#         )
#     }

#     # Menyimpan transaksi
#     data.append(pesanan_baru)

#     if simpan_pesanan(data):

#         print("\nPembayaran berhasil!")

#         # Menampilkan struk
#         tampilkan_struk(pesanan_baru)

#     else:
#         data.remove(pesanan_baru)


# # ==========================================
# # MENAMPILKAN STRUK PESANAN
# # ==========================================

# def tampilkan_struk(pesanan):

#     print("\n")
#     print("=" * 50)
#     print("              STRUK LAUNDRY")
#     print("=" * 50)

#     print("Kode Pesanan   :", pesanan["id"])
#     print("Kode Pelanggan :", pesanan["pelanggan_id"])
#     print("Nama Pelanggan :", pesanan["nama_pelanggan"])
#     print("Tanggal        :", pesanan["tanggal"])

#     print("-" * 50)

#     print("RINCIAN LAYANAN")

#     for nomor, barang in enumerate(
#         pesanan["daftar_layanan"],
#         start=1
#     ):

#         print(f"\n{nomor}. {barang['nama_layanan']}")

#         print("   Berat       :", barang["berat"], "kg")

#         print(
#             "   Harga/kg    :",
#             format_rupiah(barang["harga_per_kg"])
#         )

#         print(
#             "   Subtotal    :",
#             format_rupiah(barang["subtotal"])
#         )

#     print("-" * 50)

#     print(
#         "Total Pembayaran :",
#         format_rupiah(pesanan["total"])
#     )

#     print(
#         "Uang Pembayaran  :",
#         format_rupiah(pesanan["bayar"])
#     )

#     print(
#         "Kembalian        :",
#         format_rupiah(pesanan["kembalian"])
#     )

#     print("-" * 50)

#     print("Status Pesanan   :", pesanan["status"])

#     print("=" * 50)
#     print("       TERIMA KASIH TELAH MENGGUNAKAN")
#     print("             JASA LAUNDRY KAMI")
#     print("=" * 50)


# # ==========================================
# # MELIHAT DETAIL PESANAN
# # ==========================================

# def detail_pesanan(data):

#     print("\n--- DETAIL PESANAN ---")

#     if len(data) == 0:
#         print("Belum ada pesanan.")
#         return

#     kode = input_teks(
#         "Masukkan kode pesanan: "
#     ).upper()

#     pesanan = cari_pesanan(data, kode)

#     if pesanan is None:
#         print("Pesanan tidak ditemukan!")
#         return

#     tampilkan_struk(pesanan)


# # ==========================================
# # MENGUBAH STATUS PESANAN
# # ==========================================

# def ubah_status(data):

#     print("\n--- UBAH STATUS PESANAN ---")

#     if len(data) == 0:
#         print("Belum ada pesanan.")
#         return

#     tampilkan_daftar_pesanan(data)

#     kode = input_teks(
#         "\nMasukkan kode pesanan: "
#     ).upper()

#     pesanan = cari_pesanan(data, kode)

#     if pesanan is None:
#         print("Kode pesanan tidak ditemukan!")
#         return

#     print("\nKode Pesanan :", pesanan["id"])
#     print("Pelanggan    :", pesanan["nama_pelanggan"])
#     print("Status Lama  :", pesanan["status"])

#     print("\nPilihan Status")

#     for nomor, status in enumerate(
#         STATUS_PESANAN,
#         start=1
#     ):
#         print(f"{nomor}. {status}")

#     pilihan = input_angka(
#         "Pilih status baru: ",
#         minimal=1
#     )

#     if pilihan > len(STATUS_PESANAN):
#         print("Pilihan status tidak tersedia!")
#         return

#     status_baru = STATUS_PESANAN[pilihan - 1]

#     if pesanan["status"].lower() == status_baru.lower():

#         print("Status pesanan sudah menggunakan status tersebut.")
#         return

#     pesanan["status"] = status_baru

#     if simpan_pesanan(data):

#         print("\nStatus pesanan berhasil diubah!")
#         print("Status baru:", status_baru)


# # ==========================================
# # MENGHAPUS PESANAN
# # ==========================================

# def hapus_pesanan(data):

#     print("\n--- HAPUS PESANAN ---")

#     if len(data) == 0:
#         print("Belum ada pesanan.")
#         return

#     tampilkan_daftar_pesanan(data)

#     kode = input_teks(
#         "\nMasukkan kode pesanan yang dihapus: "
#     ).upper()

#     pesanan = cari_pesanan(data, kode)

#     if pesanan is None:
#         print("Pesanan tidak ditemukan!")
#         return

#     print("Pelanggan:", pesanan["nama_pelanggan"])

#     print(
#         "Total:",
#         format_rupiah(pesanan["total"])
#     )

#     yakin = input(
#         "Yakin ingin menghapus pesanan? (y/t): "
#     ).strip().lower()

#     if yakin in ("y", "ya"):

#         indeks = data.index(pesanan)

#         data.pop(indeks)

#         if simpan_pesanan(data):

#             print("Pesanan berhasil dihapus.")

#         else:

#             data.insert(indeks, pesanan)

#     else:

#         print("Penghapusan dibatalkan.")


# # ==========================================
# # MENU UTAMA PESANAN
# # ==========================================

# def tampilkan_menu():

#     print("\n" + "=" * 40)
#     print("       MANAJEMEN PESANAN LAUNDRY")
#     print("=" * 40)

#     print("1. Tambah Pesanan")
#     print("2. Lihat Daftar Pesanan")
#     print("3. Lihat Detail Pesanan")
#     print("4. Ubah Status Pesanan")
#     print("5. Hapus Pesanan")
#     print("0. Kembali")

#     print("=" * 40)


# # ==========================================
# # PROGRAM UTAMA
# # ==========================================

# def main():

#     data = baca_pesanan()

#     while True:

#         tampilkan_menu()

#         pilihan = input(
#             "Pilih menu: "
#         ).strip()

#         if pilihan == "1":

#             tambah_pesanan(data)

#         elif pilihan == "2":

#             tampilkan_daftar_pesanan(data)

#         elif pilihan == "3":

#             detail_pesanan(data)

#         elif pilihan == "4":

#             ubah_status(data)

#         elif pilihan == "5":

#             hapus_pesanan(data)

#         elif pilihan == "0":

#             break

#         else:

#             print("Pilihan tidak valid!")

#     print("\nKembali ke menu sebelumnya.")


# # ==========================================
# # MENJALANKAN PROGRAM
# # ==========================================

# if __name__ == "__main__":

#     try:
#         main()

#     except (KeyboardInterrupt, EOFError):

#         print("\nProgram dihentikan.")



# import json
# import os
# from datetime import datetime

# import layanan
# import pelanggan


# # ==========================================
# # PENGATURAN PROGRAM
# # ==========================================

# FOLDER_PROGRAM = os.path.dirname(os.path.abspath(__file__))

# FILE_PELANGGAN = os.path.join(FOLDER_PROGRAM, "data_pelanggan.json")
# FILE_PESANAN = os.path.join(FOLDER_PROGRAM, "pesanan.json")

# LEBAR_GARIS = 52

# # Tuple untuk menyimpan pilihan status
# DAFTAR_STATUS = (
#     "Diterima",
#     "Diproses",
#     "Selesai",
#     "Diambil"
# )

# # Set untuk validasi status
# STATUS_VALID = set(DAFTAR_STATUS)

# JAWABAN_YA = {"y", "ya"}
# JAWABAN_TIDAK = {"t", "tidak", "n"}


# # ==========================================
# # VALIDASI INPUT
# # ==========================================

# def input_teks(pesan):
#     while True:
#         teks = input(pesan).strip()

#         if teks != "":
#             return teks

#         print("Input tidak boleh kosong!")


# def input_angka(pesan, minimal=0):
#     while True:
#         teks = input(pesan).strip()

#         try:
#             angka = int(teks)

#             if angka < minimal:
#                 print(f"Angka minimal adalah {minimal}.")
#             else:
#                 return angka

#         except ValueError:
#             print("Masukkan angka bulat yang benar!")


# def input_berat(pesan):
#     while True:
#         teks = input(pesan).strip().replace(",", ".")

#         try:
#             berat = float(teks)

#             if berat <= 0:
#                 print("Berat harus lebih dari 0 kg!")
#             else:
#                 return berat

#         except ValueError:
#             print("Masukkan berat dalam angka, contoh: 2.5")


# def konfirmasi(pesan):
#     while True:
#         jawaban = input(pesan + " (y/t): ").strip().lower()

#         if jawaban in JAWABAN_YA:
#             return True

#         elif jawaban in JAWABAN_TIDAK:
#             return False

#         print("Masukkan y untuk ya atau t untuk tidak.")


# # ==========================================
# # PENYIMPANAN DATA JSON
# # ==========================================

# def muat_pelanggan():
#     try:
#         with open(FILE_PELANGGAN, "r") as file:
#             data = json.load(file)

#         if not isinstance(data, list):
#             raise ValueError("Format data pelanggan tidak valid.")

#         return data

#     except FileNotFoundError:
#         print("Data pelanggan belum tersedia.")
#         return []

#     except (json.JSONDecodeError, ValueError) as error:
#         print("Data pelanggan bermasalah:", error)
#         return []

#     except OSError as error:
#         print("Gagal membaca data pelanggan:", error)
#         return []


# def muat_pesanan():
#     try:
#         with open(FILE_PESANAN, "r") as file:
#             data = json.load(file)

#         if not isinstance(data, list):
#             raise ValueError("Format data pesanan tidak valid.")

#         return data

#     except FileNotFoundError:
#         return []

#     except (json.JSONDecodeError, ValueError) as error:
#         print("Data pesanan bermasalah:", error)
#         return []

#     except OSError as error:
#         print("Gagal membaca data pesanan:", error)
#         return []


# def simpan_pesanan(data):
#     try:
#         with open(FILE_PESANAN, "w") as file:
#             json.dump(data, file, indent=4)

#         return True

#     except OSError as error:
#         print("Gagal menyimpan pesanan:", error)
#         return False


# # ==========================================
# # FUNGSI BANTU
# # ==========================================

# def cetak_garis():
#     print("=" * LEBAR_GARIS)


# def format_rupiah(angka):
#     return "Rp " + f"{angka:,.0f}".replace(",", ".")


# def buat_id_pesanan(data):
#     # Set untuk menyimpan ID pesanan yang sudah digunakan
#     id_terpakai = {item["id_pesanan"] for item in data}

#     nomor = 1

#     while True:
#         id_baru = "L" + str(nomor).zfill(3)

#         if id_baru not in id_terpakai:
#             return id_baru

#         nomor += 1


# def cari_pesanan(data, id_cari):
#     for pesanan in data:
#         if pesanan["id_pesanan"] == id_cari:
#             return pesanan

#     return None


# def cari_data_pelanggan(id_pelanggan):
#     data = muat_pelanggan()

#     return pelanggan.cari_pelanggan(
#         data,
#         id_pelanggan.upper()
#     )


# # ==========================================
# # FITUR 1: TAMBAH PESANAN
# # ==========================================

# def tambah_pesanan(data):
#     print("\n--- TAMBAH PESANAN LAUNDRY ---")

#     # Memeriksa ID pelanggan
#     id_pelanggan = input_teks(
#         "Masukkan ID pelanggan: "
#     ).upper()

#     data_pelanggan = cari_data_pelanggan(id_pelanggan)

#     if data_pelanggan is None:
#         print("ID pelanggan tidak ditemukan!")
#         return

#     print("\nData pelanggan ditemukan.")
#     print("ID      :", data_pelanggan["id"])
#     print("Nama    :", data_pelanggan["nama"])
#     print("Telepon :", data_pelanggan["telepon"])
#     print("Alamat  :", data_pelanggan["alamat"])

#     # Mengambil layanan dari layanan.py
#     data_layanan = layanan.muat_data()

#     if len(data_layanan) == 0:
#         print("Belum ada layanan laundry tersedia.")
#         return

#     keranjang = []
#     layanan_dipilih = set()

#     while True:
#         # Menampilkan layanan
#         layanan.tampilkan_daftar(data_layanan)

#         nomor = input_angka(
#             "\nPilih nomor layanan (0 = selesai memilih): ",
#             0
#         )

#         if nomor == 0:
#             break

#         if nomor > len(data_layanan):
#             print("Nomor layanan tidak tersedia!")
#             continue

#         indeks = nomor - 1

#         jenis = data_layanan[indeks]
#         nama_layanan = jenis["nama"]

#         # Mencegah layanan yang sama dipilih dua kali
#         if nama_layanan.lower() in layanan_dipilih:
#             print("Layanan tersebut sudah dipilih!")
#             continue

#         berat = input_berat(
#             f"Masukkan berat pakaian untuk {nama_layanan} (kg): "
#         )

#         harga = jenis["harga"]

#         subtotal = round(harga * berat)

#         # Dictionary untuk setiap layanan dalam keranjang
#         item = {
#             "nama_layanan": nama_layanan,
#             "harga_per_kg": harga,
#             "berat": berat,
#             "estimasi_jam": jenis["estimasi_jam"],
#             "subtotal": subtotal
#         }

#         keranjang.append(item)
#         layanan_dipilih.add(nama_layanan.lower())

#         print("Layanan berhasil dimasukkan ke keranjang.")
#         print("Subtotal:", format_rupiah(subtotal))

#         if not konfirmasi("\nTambah layanan lainnya?"):
#             break

#     if len(keranjang) == 0:
#         print("Pesanan dibatalkan karena belum ada layanan.")
#         return

#     # Menghitung total seluruh layanan
#     total = 0

#     print("\n--- RINCIAN PESANAN ---")

#     for nomor, item in enumerate(keranjang, start=1):
#         print(
#             f"{nomor}. {item['nama_layanan']} | "
#             f"{item['berat']} kg | "
#             f"{format_rupiah(item['subtotal'])}"
#         )

#         total += item["subtotal"]

#     print("-" * 52)
#     print("Total pembayaran:", format_rupiah(total))

#     # Proses pembayaran
#     while True:
#         bayar = input_angka(
#             "\nMasukkan uang pembayaran: ",
#             0
#         )

#         if bayar < total:
#             print("Uang pembayaran tidak mencukupi!")
#             print("Kekurangan:", format_rupiah(total - bayar))

#             if not konfirmasi("Ulangi pembayaran?"):
#                 print("Transaksi dibatalkan.")
#                 return

#         else:
#             break

#     kembalian = bayar - total

#     # Membuat data pesanan
#     id_pesanan = buat_id_pesanan(data)

#     pesanan_baru = {
#         "id_pesanan": id_pesanan,
#         "id_pelanggan": data_pelanggan["id"],
#         "nama_pelanggan": data_pelanggan["nama"],
#         "telepon": data_pelanggan["telepon"],
#         "alamat": data_pelanggan["alamat"],
#         "tanggal": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
#         "daftar_layanan": keranjang,
#         "total": total,
#         "bayar": bayar,
#         "kembalian": kembalian,
#         "status": "Diterima"
#     }

#     data.append(pesanan_baru)

#     if simpan_pesanan(data):
#         print("\nPembayaran berhasil!")
#         tampilkan_struk(pesanan_baru)

#     else:
#         data.pop()
#         print("Transaksi tidak dapat disimpan.")


# # ==========================================
# # FITUR 2: MENAMPILKAN DAFTAR PESANAN
# # ==========================================

# def tampilkan_daftar_pesanan(data):
#     print("\n--- DAFTAR PESANAN LAUNDRY ---")
#     cetak_garis()

#     if len(data) == 0:
#         print("Belum ada pesanan.")
#         cetak_garis()
#         return

#     print(
#         f"{'ID':<9}"
#         f"{'Pelanggan':<17}"
#         f"{'Total':<15}"
#         f"{'Status'}"
#     )

#     cetak_garis()

#     for pesanan in data:
#         print(
#             f"{pesanan['id_pesanan']:<9}"
#             f"{pesanan['nama_pelanggan']:<17}"
#             f"{format_rupiah(pesanan['total']):<15}"
#             f"{pesanan['status']}"
#         )

#     cetak_garis()
#     print("Total pesanan:", len(data))


# # ==========================================
# # FITUR 3: MENAMPILKAN STRUK
# # ==========================================

# def tampilkan_struk(pesanan):
#     print("\n")
#     cetak_garis()
#     print("              STRUK LAUNDRY")
#     cetak_garis()

#     print("ID Pesanan :", pesanan["id_pesanan"])
#     print("Tanggal    :", pesanan["tanggal"])

#     cetak_garis()

#     print("ID Pelanggan :", pesanan["id_pelanggan"])
#     print("Nama         :", pesanan["nama_pelanggan"])
#     print("Telepon      :", pesanan["telepon"])
#     print("Alamat       :", pesanan["alamat"])

#     cetak_garis()
#     print("DETAIL LAYANAN")
#     cetak_garis()

#     for nomor, item in enumerate(
#         pesanan["daftar_layanan"], start=1
#     ):
#         print(f"{nomor}. {item['nama_layanan']}")
#         print("   Harga/kg :", format_rupiah(item["harga_per_kg"]))
#         print("   Berat    :", item["berat"], "kg")
#         print("   Subtotal :", format_rupiah(item["subtotal"]))
#         print("   Estimasi :", item["estimasi_jam"], "jam")

#     cetak_garis()

#     print("Total      :", format_rupiah(pesanan["total"]))
#     print("Pembayaran :", format_rupiah(pesanan["bayar"]))
#     print("Kembalian  :", format_rupiah(pesanan["kembalian"]))
#     print("Status     :", pesanan["status"])

#     cetak_garis()
#     print("       TERIMA KASIH TELAH MENGGUNAKAN")
#     print("             LAYANAN LAUNDRY")
#     cetak_garis()


# # ==========================================
# # FITUR 4: LIHAT DETAIL PESANAN
# # ==========================================

# def detail_pesanan(data):
#     print("\n--- DETAIL PESANAN ---")

#     if len(data) == 0:
#         print("Belum ada pesanan.")
#         return

#     id_cari = input_teks(
#         "Masukkan ID pesanan: "
#     ).upper()

#     pesanan = cari_pesanan(data, id_cari)

#     if pesanan is None:
#         print("ID pesanan tidak ditemukan!")
#         return

#     tampilkan_struk(pesanan)


# # ==========================================
# # FITUR 5: UBAH STATUS PESANAN
# # ==========================================

# def ubah_status(data):
#     print("\n--- UBAH STATUS PESANAN ---")

#     if len(data) == 0:
#         print("Belum ada pesanan.")
#         return

#     tampilkan_daftar_pesanan(data)

#     id_cari = input_teks(
#         "\nMasukkan ID pesanan: "
#     ).upper()

#     pesanan = cari_pesanan(data, id_cari)

#     if pesanan is None:
#         print("ID pesanan tidak ditemukan!")
#         return

#     print("\nID Pesanan :", pesanan["id_pesanan"])
#     print("Pelanggan  :", pesanan["nama_pelanggan"])
#     print("Status saat ini:", pesanan["status"])

#     print("\nPILIH STATUS BARU")

#     for nomor, status in enumerate(
#         DAFTAR_STATUS, start=1
#     ):
#         print(f"{nomor}. {status}")

#     pilihan = input_angka(
#         "Pilih status: ",
#         1
#     )

#     if pilihan > len(DAFTAR_STATUS):
#         print("Pilihan status tidak tersedia!")
#         return

#     status_baru = DAFTAR_STATUS[pilihan - 1]

#     if status_baru == pesanan["status"]:
#         print("Status pesanan tidak berubah.")
#         return

#     status_lama = pesanan["status"]

#     if konfirmasi(
#         f"Ubah status dari {status_lama} menjadi {status_baru}?"
#     ):
#         pesanan["status"] = status_baru

#         if simpan_pesanan(data):
#             print("Status pesanan berhasil diubah.")
#         else:
#             pesanan["status"] = status_lama

#     else:
#         print("Perubahan status dibatalkan.")


# # ==========================================
# # FITUR 6: HAPUS PESANAN
# # ==========================================

# def hapus_pesanan(data):
#     print("\n--- HAPUS PESANAN ---")

#     if len(data) == 0:
#         print("Belum ada pesanan.")
#         return

#     tampilkan_daftar_pesanan(data)

#     id_cari = input_teks(
#         "\nMasukkan ID pesanan yang dihapus: "
#     ).upper()

#     pesanan = cari_pesanan(data, id_cari)

#     if pesanan is None:
#         print("ID pesanan tidak ditemukan!")
#         return

#     if konfirmasi(
#         f"Yakin menghapus pesanan {id_cari}?"
#     ):
#         data.remove(pesanan)

#         if simpan_pesanan(data):
#             print("Pesanan berhasil dihapus.")
#         else:
#             data.append(pesanan)
#             print("Gagal menghapus pesanan.")

#     else:
#         print("Penghapusan dibatalkan.")


# # ==========================================
# # MENU UTAMA
# # ==========================================

# def tampilkan_menu():
#     print("\n")
#     cetak_garis()
#     print("MANAJEMEN PESANAN LAUNDRY")
#     cetak_garis()

#     print("1. Tambah Pesanan")
#     print("2. Lihat Daftar Pesanan")
#     print("3. Lihat Detail Pesanan")
#     print("4. Ubah Status Pesanan")
#     print("5. Hapus Pesanan")
#     print("0. Kembali")

#     cetak_garis()


# # ==========================================
# # PROGRAM UTAMA
# # ==========================================

# def main():
#     data = muat_pesanan()

#     while True:
#         tampilkan_menu()

#         pilihan = input_angka(
#             "Pilih menu: ",
#             0
#         )

#         if pilihan == 1:
#             tambah_pesanan(data)

#         elif pilihan == 2:
#             tampilkan_daftar_pesanan(data)

#         elif pilihan == 3:
#             detail_pesanan(data)

#         elif pilihan == 4:
#             ubah_status(data)

#         elif pilihan == 5:
#             hapus_pesanan(data)

#         elif pilihan == 0:
#             break

#         else:
#             print("Pilihan menu tidak tersedia!")

#     print("\nKembali ke menu sebelumnya.")


# if __name__ == "__main__":
#     try:
#         main()

#     except (KeyboardInterrupt, EOFError):
#         print("\nProgram dihentikan.")
#         print("Data yang sudah tersimpan tetap aman.")



# # import json
# # import math
# # import os
# # from datetime import datetime

# # import layanan as katalog  # daftar layanan, harga, dan fungsi bantu (input, tampilan)


# # # DATA AWAL
# # FILE_PESANAN = os.path.join(katalog.FOLDER_PROGRAM, "pesanan.json")
# # JUMLAH_MAKSIMAL = 1000
# # UANG_MAKSIMAL = 1000000000

# # # tuple: isi menu (urutan = nomor menu)
# # MENU_PESANAN = (
# #     "Buat Pesanan Baru",
# #     "Lihat Riwayat Pesanan",
# #     "Lihat Struk Pesanan",
# #     "Hapus Pesanan",
# # )
# # MENU_KERANJANG = (
# #     "Tambah Layanan",
# #     "Ubah Jumlah",
# #     "Hapus Layanan",
# #     "Lihat Keranjang",
# #     "Bayar",
# # )

# # # set: kunci yang wajib ada di setiap pesanan dan di setiap layanan yang dipesan
# # KUNCI_PESANAN = {"waktu", "barang", "total", "bayar", "kembalian"}
# # KUNCI_BARANG = {"nama", "harga", "jumlah", "subtotal"}


# # # VALIDASI INPUT
# # def input_jumlah(pesan):
# #     """Minta jumlah dalam kg. Boleh desimal (contoh: 2.5 atau 2,5)."""
# #     while True:
# #         teks = input(pesan).strip().replace(",", ".")
# #         try:  # exception handling: ValueError kalau input bukan angka
# #             jumlah = float(teks)
# #         except ValueError:
# #             print("Jumlah harus berupa angka (contoh: 2.5), coba lagi.")
# #             continue

# #         if not math.isfinite(jumlah):
# #             print("Jumlah tidak valid, coba lagi.")
# #             continue

# #         jumlah = round(jumlah, 2)
# #         if jumlah <= 0:
# #             print("Jumlah harus lebih dari 0.")
# #         elif jumlah > JUMLAH_MAKSIMAL:
# #             print(f"Jumlah tidak boleh lebih dari {JUMLAH_MAKSIMAL} kg.")
# #         else:
# #             return jumlah


# # def pilih_nomor(daftar, pesan):
# #     """Minta nomor dari sebuah list. Mengembalikan indeks list, atau None kalau batal."""
# #     nomor = katalog.input_angka(pesan + " (0 = batal): ", 0, len(daftar))
# #     if nomor == 0:
# #         return None
# #     return nomor - 1


# # # PENYIMPANAN DATA (FILE JSON)
# # def simpan_pesanan(data):
# #     try:  # IO: tulis riwayat pesanan ke file JSON
# #         with open(FILE_PESANAN, "w") as file:
# #             json.dump(data, file, indent=4)
# #         return True
# #     except OSError as error:
# #         print(f"Gagal menyimpan data pesanan: {error}")
# #         return False


# # def pesanan_valid(data):
# #     if not isinstance(data, list):
# #         return False
# #     for pesanan in data:
# #         if not isinstance(pesanan, dict) or not KUNCI_PESANAN <= set(pesanan):
# #             return False
# #         if not isinstance(pesanan["barang"], list):
# #             return False
# #         for barang in pesanan["barang"]:
# #             if not isinstance(barang, dict) or not KUNCI_BARANG <= set(barang):
# #                 return False
# #     return True


# # def muat_pesanan():
# #     try:  # IO: baca riwayat pesanan dari file JSON
# #         with open(FILE_PESANAN, "r") as file:
# #             data = json.load(file)
# #         if not pesanan_valid(data):
# #             raise ValueError("Isi file tidak sesuai format")
# #         return data

# #     except FileNotFoundError:
# #         return []

# #     except ValueError:  # termasuk json.JSONDecodeError
# #         print("File pesanan tidak sesuai. File lama disimpan sebagai pesanan.json.rusak.")
# #         try:
# #             os.replace(FILE_PESANAN, FILE_PESANAN + ".rusak")
# #         except OSError:
# #             pass
# #         return []

# #     except OSError as error:
# #         print(f"Gagal membaca file pesanan: {error}")
# #         return []


# # # PERHITUNGAN
# # def hitung_subtotal(harga, jumlah):
# #     return int(round(harga * jumlah))


# # def hitung_total(keranjang):
# #     total = 0
# #     for barang in keranjang:
# #         total = total + barang["subtotal"]
# #     return total


# # def cari_di_keranjang(keranjang, nama):
# #     """Mengembalikan indeks layanan di keranjang, atau None kalau belum ada."""
# #     indeks = 0
# #     for barang in keranjang:
# #         if barang["nama"] == nama:
# #             return indeks
# #         indeks = indeks + 1
# #     return None


# # # TAMPILAN
# # def tampilkan_menu(judul, daftar_menu, teks_nol):
# #     print()
# #     katalog.cetak_garis()
# #     print(judul)
# #     katalog.cetak_garis()
# #     nomor = 1
# #     for isi in daftar_menu:
# #         print(f"{nomor}. {isi}")
# #         nomor = nomor + 1
# #     print(f"0. {teks_nol}")
# #     katalog.cetak_garis()


# # def cetak_tabel_barang(daftar_barang):
# #     """Tabel layanan yang dipesan (dipakai oleh keranjang dan struk)."""
# #     print(f"{'No':<4}{'Layanan':<15}{'Harga':<13}{'Jumlah':<10}Subtotal")
# #     print("-" * katalog.LEBAR_GARIS)

# #     nomor = 1
# #     for barang in daftar_barang:
# #         harga = katalog.format_rupiah(barang["harga"])
# #         jumlah = f"{barang['jumlah']:g} kg"
# #         subtotal = katalog.format_rupiah(barang["subtotal"])
# #         print(f"{nomor:<4}{barang['nama'][:14]:<15}{harga:<13}{jumlah:<10}{subtotal}")
# #         nomor = nomor + 1

# #     print("-" * katalog.LEBAR_GARIS)


# # def tampilkan_keranjang(keranjang):
# #     print()
# #     katalog.cetak_garis()
# #     print("KERANJANG PESANAN")
# #     katalog.cetak_garis()

# #     if len(keranjang) == 0:
# #         print("Keranjang masih kosong.")
# #         katalog.cetak_garis()
# #         return

# #     cetak_tabel_barang(keranjang)
# #     print(f"{'Total':<12}: {katalog.format_rupiah(hitung_total(keranjang))}")
# #     katalog.cetak_garis()


# # def cetak_struk(pesanan):
# #     print()
# #     katalog.cetak_garis()
# #     print("STRUK PEMBAYARAN LAUNDRY".center(katalog.LEBAR_GARIS))
# #     katalog.cetak_garis()
# #     print(f"Tanggal : {pesanan['waktu']}")
# #     cetak_tabel_barang(pesanan["barang"])
# #     print(f"{'Total':<12}: {katalog.format_rupiah(pesanan['total'])}")
# #     print(f"{'Bayar':<12}: {katalog.format_rupiah(pesanan['bayar'])}")
# #     print(f"{'Kembalian':<12}: {katalog.format_rupiah(pesanan['kembalian'])}")
# #     katalog.cetak_garis()
# #     print("Terima kasih!".center(katalog.LEBAR_GARIS))
# #     katalog.cetak_garis()


# # def tampilkan_riwayat(data):
# #     print()
# #     katalog.cetak_garis()
# #     print("RIWAYAT PESANAN LAUNDRY")
# #     katalog.cetak_garis()

# #     if len(data) == 0:
# #         print("Belum ada pesanan.")
# #         katalog.cetak_garis()
# #         return

# #     print(f"{'No':<4}{'Tanggal':<19}{'Layanan':<9}Total")
# #     print("-" * katalog.LEBAR_GARIS)

# #     nomor = 1
# #     for pesanan in data:
# #         jenis = f"{len(pesanan['barang'])} jenis"
# #         total = katalog.format_rupiah(pesanan["total"])
# #         print(f"{nomor:<4}{pesanan['waktu']:<19}{jenis:<9}{total}")
# #         nomor = nomor + 1

# #     print("-" * katalog.LEBAR_GARIS)


# # # FITUR KERANJANG (satu transaksi)
# # def tambah_barang(keranjang, data_layanan):
# #     print("\n--- TAMBAH LAYANAN ---")
# #     katalog.tampilkan_daftar(data_layanan)  # daftar layanan terbaru
# #     indeks = katalog.pilih_nomor_layanan(data_layanan, "Pilih nomor layanan")
# #     if indeks is None:
# #         print("Dibatalkan.")
# #         return
# #     jenis = data_layanan[indeks]

# #     jumlah = input_jumlah("Jumlah (kg)            : ")

# #     posisi = cari_di_keranjang(keranjang, jenis["nama"])
# #     if posisi is None:
# #         keranjang.append({  # dictionary: satu layanan yang dipesan
# #             "nama": jenis["nama"],
# #             "harga": jenis["harga"],  # harga disalin agar pesanan lama tidak berubah
# #             "jumlah": jumlah,
# #             "subtotal": hitung_subtotal(jenis["harga"], jumlah),
# #         })
# #     else:  # layanan yang sama dipilih lagi: jumlahnya digabung
# #         barang = keranjang[posisi]
# #         jumlah_baru = round(barang["jumlah"] + jumlah, 2)
# #         if jumlah_baru > JUMLAH_MAKSIMAL:
# #             print(f"Jumlah layanan ini tidak boleh lebih dari {JUMLAH_MAKSIMAL} kg.")
# #             return
# #         barang["jumlah"] = jumlah_baru
# #         barang["subtotal"] = hitung_subtotal(barang["harga"], jumlah_baru)

# #     print(f"Layanan '{jenis['nama']}' dimasukkan ke keranjang.")


# # def ubah_jumlah(keranjang):
# #     print("\n--- UBAH JUMLAH ---")
# #     if len(keranjang) == 0:
# #         print("Keranjang masih kosong.")
# #         return

# #     tampilkan_keranjang(keranjang)
# #     indeks = pilih_nomor(keranjang, "Nomor layanan yang diubah")
# #     if indeks is None:
# #         print("Dibatalkan.")
# #         return

# #     barang = keranjang[indeks]
# #     jumlah_baru = input_jumlah(f"Jumlah baru (kg) [{barang['jumlah']:g}]: ")
# #     barang["jumlah"] = jumlah_baru
# #     barang["subtotal"] = hitung_subtotal(barang["harga"], jumlah_baru)
# #     print("Jumlah berhasil diubah.")


# # def hapus_barang(keranjang):
# #     print("\n--- HAPUS LAYANAN ---")
# #     if len(keranjang) == 0:
# #         print("Keranjang masih kosong.")
# #         return

# #     tampilkan_keranjang(keranjang)
# #     indeks = pilih_nomor(keranjang, "Nomor layanan yang dihapus")
# #     if indeks is None:
# #         print("Dibatalkan.")
# #         return

# #     nama = keranjang[indeks]["nama"]
# #     if katalog.konfirmasi(f"Yakin hapus '{nama}' dari keranjang?"):
# #         keranjang.pop(indeks)
# #         print(f"Layanan '{nama}' dihapus dari keranjang.")
# #     else:
# #         print("Penghapusan dibatalkan.")


# # def proses_bayar(keranjang):
# #     """Minta uang bayar. Mengembalikan pesanan (dictionary), atau None kalau batal."""
# #     total = hitung_total(keranjang)
# #     print(f"\nTotal pembayaran : {katalog.format_rupiah(total)}")

# #     while True:
# #         bayar = katalog.input_angka("Uang dibayar (Rp) (0 = batal): ", 0, UANG_MAKSIMAL)
# #         if bayar == 0:
# #             return None
# #         if bayar < total:
# #             print(f"Uang kurang {katalog.format_rupiah(total - bayar)}, coba lagi.")
# #         else:
# #             break

# #     return {  # dictionary: satu pesanan yang sudah dibayar
# #         "waktu": datetime.now().strftime("%Y-%m-%d %H:%M"),
# #         "barang": list(keranjang),
# #         "total": total,
# #         "bayar": bayar,
# #         "kembalian": bayar - total,
# #     }


# # def buat_pesanan(data, data_layanan):
# #     print("\n--- BUAT PESANAN BARU ---")
# #     if len(data_layanan) == 0:
# #         print("Belum ada layanan. Tambahkan layanan dulu di menu Kelola Layanan.")
# #         return

# #     keranjang = []  # list berisi layanan yang dipesan dalam transaksi ini

# #     while True:
# #         tampilkan_menu("KERANJANG PESANAN", MENU_KERANJANG, "Batalkan Pesanan")
# #         pilihan = katalog.input_angka("Pilih menu: ", 0, len(MENU_KERANJANG))

# #         if pilihan == 1:
# #             tambah_barang(keranjang, data_layanan)
# #         elif pilihan == 2:
# #             ubah_jumlah(keranjang)
# #         elif pilihan == 3:
# #             hapus_barang(keranjang)
# #         elif pilihan == 4:
# #             tampilkan_keranjang(keranjang)
# #         elif pilihan == 5:
# #             if len(keranjang) == 0:
# #                 print("Keranjang masih kosong, tambahkan layanan dulu.")
# #                 continue

# #             tampilkan_keranjang(keranjang)
# #             pesanan = proses_bayar(keranjang)
# #             if pesanan is None:
# #                 print("Pembayaran dibatalkan.")
# #                 continue

# #             data.append(pesanan)  # list: tambahkan ke riwayat pesanan
# #             simpan_pesanan(data)
# #             print("\nPembayaran berhasil.")
# #             cetak_struk(pesanan)
# #             return
# #         else:  # pilihan 0
# #             if len(keranjang) == 0 or katalog.konfirmasi("Keranjang akan dikosongkan. Batalkan pesanan?"):
# #                 print("Pesanan dibatalkan.")
# #                 return


# # # FITUR RIWAYAT PESANAN
# # def lihat_struk(data):
# #     print("\n--- LIHAT STRUK PESANAN ---")
# #     if len(data) == 0:
# #         print("Belum ada pesanan.")
# #         return

# #     tampilkan_riwayat(data)
# #     indeks = pilih_nomor(data, "Nomor pesanan")
# #     if indeks is None:
# #         print("Dibatalkan.")
# #         return

# #     cetak_struk(data[indeks])


# # def hapus_pesanan(data):
# #     print("\n--- HAPUS PESANAN ---")
# #     if len(data) == 0:
# #         print("Belum ada pesanan.")
# #         return

# #     tampilkan_riwayat(data)
# #     indeks = pilih_nomor(data, "Nomor pesanan yang dihapus")
# #     if indeks is None:
# #         print("Dibatalkan.")
# #         return

# #     waktu = data[indeks]["waktu"]
# #     if katalog.konfirmasi(f"Yakin hapus pesanan tanggal {waktu}?"):
# #         data.pop(indeks)
# #         if simpan_pesanan(data):
# #             print("Pesanan berhasil dihapus.")
# #     else:
# #         print("Penghapusan dibatalkan.")


# # # SUBMENU PESANAN (dipanggil dari main.py)
# # def menu_pesanan(data_layanan):
# #     data = muat_pesanan()  # list berisi semua pesanan yang sudah dibayar

# #     while True:
# #         tampilkan_menu("MANAJEMEN PESANAN LAUNDRY", MENU_PESANAN, "Kembali")
# #         pilihan = katalog.input_angka("Pilih menu: ", 0, len(MENU_PESANAN))

# #         if pilihan == 1:
# #             buat_pesanan(data, data_layanan)
# #         elif pilihan == 2:
# #             tampilkan_riwayat(data)
# #         elif pilihan == 3:
# #             lihat_struk(data)
# #         elif pilihan == 4:
# #             hapus_pesanan(data)
# #         else:  # pilihan 0: kembali ke menu utama
# #             break


# # # Jika file ini dijalankan langsung
# # if __name__ == "__main__":
# #     try:
# #         menu_pesanan(katalog.muat_data())
# #     except (KeyboardInterrupt, EOFError):
# #         print("\n\nProgram dihentikan. Data yang sudah disimpan tetap aman.")


# # # """pesanan.py - Manajemen pesanan laundry (aplikasi terminal / CLI).

# # # Penerapan materi pada kode ini:
# # # - Variabel, tipe data, operator : konstanta, int/float/str, hitung_total, perbandingan, logika
# # # - Percabangan dan perulangan    : if/elif/else, while, for
# # # - Fungsi                        : setiap tugas dipisah ke fungsi sendiri
# # # - List, tuple, set, dictionary  : daftar pesanan, STATUS_PESANAN, KUNCI_PESANAN, satu pesanan
# # # - Modul dan package             : json (package bawaan Python), os, layanan, pelanggan
# # # - Exception handling dan IO     : try/except dan with open() pada file pesanan.json

# # # Kode pesanan = kode (ID) pelanggan dari pelanggan.py. Kode hanya dibuat di pelanggan.py.
# # # """
# # # import json
# # # import os

# # # import layanan    # validasi, tampilan, dan data layanan
# # # import pelanggan  # data pelanggan (kode/ID, nama, telepon)


# # # # DATA AWAL
# # # FILE_PESANAN = os.path.join(layanan.FOLDER_PROGRAM, "pesanan.json")

# # # # tuple: urutan status pesanan
# # # STATUS_PESANAN = ("Diterima", "Diproses", "Selesai", "Diambil")

# # # # set: kunci yang wajib ada di setiap pesanan
# # # # ("telepon" sengaja tidak wajib agar pesanan lama tetap terbaca)
# # # KUNCI_PESANAN = {"kode", "pelanggan", "layanan", "harga_per_kg", "berat_kg", "total", "status"}


# # # # VALIDASI INPUT
# # # def input_berat(pesan):
# # #     while True:
# # #         teks = input(pesan).strip().replace(",", ".")
# # #         try:  # exception handling: ValueError kalau input bukan angka
# # #             berat = float(teks)
# # #         except ValueError:
# # #             print("Berat harus berupa angka (contoh: 2.5), coba lagi.")
# # #             continue

# # #         if berat <= 0:
# # #             print("Berat harus lebih dari 0.")
# # #         elif berat > 1000:
# # #             print("Berat tidak boleh lebih dari 1000 kg.")
# # #         else:
# # #             return round(berat, 2)


# # # # PENYIMPANAN DATA (FILE JSON)
# # # def simpan_pesanan(data):
# # #     try:  # IO: tulis daftar pesanan ke file JSON
# # #         with open(FILE_PESANAN, "w") as file:
# # #             json.dump(data, file, indent=4)
# # #         return True
# # #     except OSError as error:
# # #         print(f"Gagal menyimpan data pesanan: {error}")
# # #         return False


# # # def muat_pesanan():
# # #     try:  # IO: baca daftar pesanan dari file JSON
# # #         with open(FILE_PESANAN, "r") as file:
# # #             data = json.load(file)
# # #     except FileNotFoundError:
# # #         return []
# # #     except (ValueError, OSError):
# # #         print("File pesanan.json tidak bisa dibaca, data dimulai dari kosong.")
# # #         return []

# # #     # pastikan isi file berupa list dan setiap pesanan punya kunci yang wajib
# # #     if not isinstance(data, list):
# # #         return []
# # #     for pesanan in data:
# # #         if not isinstance(pesanan, dict) or not KUNCI_PESANAN <= set(pesanan):
# # #             print("Format pesanan.json tidak sesuai, data dimulai dari kosong.")
# # #             return []
# # #     return data


# # # # FUNGSI BANTU
# # # def hitung_total(harga_per_kg, berat_kg):
# # #     return int(round(harga_per_kg * berat_kg))


# # # def pilih_nomor_pesanan(data, pesan):
# # #     """Mengembalikan indeks list, atau None kalau batal."""
# # #     nomor = layanan.input_angka(pesan + " (0 = batal): ", 0, len(data))
# # #     if nomor == 0:
# # #         return None
# # #     return nomor - 1


# # # def pilih_pelanggan(data_pelanggan):
# # #     """Minta kode pelanggan. Mengembalikan data pelanggan, atau None kalau batal."""
# # #     while True:
# # #         id_cari = input("Masukkan ID pelanggan (0 = batal): ").strip().upper()
# # #         if id_cari == "0":
# # #             return None

# # #         terpilih = pelanggan.cari_pelanggan(data_pelanggan, id_cari)
# # #         if terpilih is not None:
# # #             return terpilih
# # #         print("ID pelanggan tidak ditemukan, coba lagi.")


# # # # TAMPILAN
# # # def tampilkan_daftar_pesanan(data):
# # #     print()
# # #     layanan.cetak_garis()
# # #     print("DAFTAR PESANAN LAUNDRY")
# # #     layanan.cetak_garis()

# # #     if len(data) == 0:
# # #         print("Belum ada pesanan.")
# # #         layanan.cetak_garis()
# # #         return

# # #     print(f"{'No':<4}{'Kode':<6}{'Pelanggan':<16}{'Layanan':<14}{'Berat':<8}{'Total':<13}Status")
# # #     print("-" * 70)

# # #     nomor = 1
# # #     for pesanan in data:
# # #         berat = f"{pesanan['berat_kg']} kg"
# # #         total = layanan.format_rupiah(pesanan["total"])
# # #         print(
# # #             f"{nomor:<4}{pesanan['kode']:<6}{pesanan['pelanggan'][:15]:<16}"
# # #             f"{pesanan['layanan'][:13]:<14}{berat:<8}{total:<13}{pesanan['status']}"
# # #         )
# # #         nomor = nomor + 1

# # #     print("-" * 70)


# # # def tampilkan_detail(pesanan):
# # #     print()
# # #     layanan.cetak_garis()
# # #     print(f"DETAIL PESANAN {pesanan['kode']}")
# # #     layanan.cetak_garis()
# # #     print(f"Nama Pelanggan : {pesanan['pelanggan']}")
# # #     print(f"No. Telepon    : {pesanan.get('telepon', '-')}")
# # #     print(f"Jenis Layanan  : {pesanan['layanan']}")
# # #     print(f"Harga per kg   : {layanan.format_rupiah(pesanan['harga_per_kg'])}")
# # #     print(f"Berat Pakaian  : {pesanan['berat_kg']} kg")
# # #     print(f"Total Biaya    : {layanan.format_rupiah(pesanan['total'])}")
# # #     print(f"Status         : {pesanan['status']}")
# # #     layanan.cetak_garis()


# # # # FITUR PESANAN
# # # def tambah_pesanan(data, data_layanan):
# # #     print("\n--- TAMBAH PESANAN ---")
# # #     if len(data_layanan) == 0:
# # #         print("Belum ada layanan. Tambahkan layanan dulu di menu Kelola Layanan.")
# # #         return

# # #     # dibaca ulang setiap kali agar pelanggan yang baru ditambah langsung muncul
# # #     data_pelanggan = pelanggan.baca_data()
# # #     if len(data_pelanggan) == 0:
# # #         print("Belum ada pelanggan. Tambahkan pelanggan dulu di menu Pelanggan.")
# # #         return

# # #     pelanggan.tampilkan(data_pelanggan)
# # #     terpilih = pilih_pelanggan(data_pelanggan)
# # #     if terpilih is None:
# # #         print("Dibatalkan.")
# # #         return
# # #     print(f"\nPelanggan : {terpilih['nama']} ({terpilih['telepon']})")

# # #     layanan.tampilkan_daftar(data_layanan)  # daftar layanan terbaru
# # #     indeks = layanan.pilih_nomor_layanan(data_layanan, "Pilih nomor layanan")
# # #     if indeks is None:
# # #         print("Dibatalkan.")
# # #         return
# # #     jenis = data_layanan[indeks]

# # #     berat = input_berat("Berat pakaian (kg)    : ")
# # #     total = hitung_total(jenis["harga"], berat)

# # #     print(f"\nPelanggan : {terpilih['nama']} ({terpilih['id']})")
# # #     print(f"Layanan   : {jenis['nama']} ({layanan.format_rupiah(jenis['harga'])}/kg)")
# # #     print(f"Total biaya: {layanan.format_rupiah(total)}")
# # #     if not layanan.konfirmasi("Simpan pesanan ini?"):
# # #         print("Pesanan dibatalkan.")
# # #         return

# # #     pesanan = {  # dictionary: satu pesanan
# # #         "kode": terpilih["id"],  # kode dari pelanggan.py, pesanan tidak membuat kode sendiri
# # #         "pelanggan": terpilih["nama"],
# # #         "telepon": terpilih["telepon"],
# # #         "layanan": jenis["nama"],
# # #         "harga_per_kg": jenis["harga"],
# # #         "berat_kg": berat,
# # #         "total": total,
# # #         "status": STATUS_PESANAN[0],
# # #     }
# # #     data.append(pesanan)  # list: tambahkan ke daftar pesanan

# # #     if simpan_pesanan(data):
# # #         print(f"Pesanan {pesanan['kode']} berhasil disimpan.")


# # # def ubah_status(data):
# # #     print("\n--- UBAH STATUS PESANAN ---")
# # #     if len(data) == 0:
# # #         print("Belum ada pesanan.")
# # #         return

# # #     tampilkan_daftar_pesanan(data)
# # #     indeks = pilih_nomor_pesanan(data, "Nomor pesanan")
# # #     if indeks is None:
# # #         print("Dibatalkan.")
# # #         return

# # #     pesanan = data[indeks]
# # #     print(f"\nStatus saat ini: {pesanan['status']}")
# # #     nomor = 1
# # #     for status in STATUS_PESANAN:
# # #         print(f"{nomor}. {status}")
# # #         nomor = nomor + 1

# # #     pilihan = layanan.input_angka("Pilih status baru (0 = batal): ", 0, len(STATUS_PESANAN))
# # #     if pilihan == 0:
# # #         print("Dibatalkan.")
# # #         return

# # #     pesanan["status"] = STATUS_PESANAN[pilihan - 1]
# # #     if simpan_pesanan(data):
# # #         print(f"Status pesanan {pesanan['kode']} diubah menjadi '{pesanan['status']}'.")


# # # def lihat_detail(data):
# # #     print("\n--- DETAIL PESANAN ---")
# # #     if len(data) == 0:
# # #         print("Belum ada pesanan.")
# # #         return

# # #     tampilkan_daftar_pesanan(data)
# # #     indeks = pilih_nomor_pesanan(data, "Nomor pesanan")
# # #     if indeks is None:
# # #         print("Dibatalkan.")
# # #         return

# # #     tampilkan_detail(data[indeks])


# # # # SUBMENU PESANAN (dipanggil dari main.py)
# # # def tampilkan_menu_pesanan():
# # #     print()
# # #     print("================================")
# # #     print("MANAJEMEN PESANAN LAUNDRY")
# # #     print("================================")
# # #     print("1. Tambah Pesanan")
# # #     print("2. Lihat Daftar Pesanan")
# # #     print("3. Lihat Detail Pesanan")
# # #     print("4. Ubah Status Pesanan")
# # #     print("0. Kembali")
# # #     print("================================")


# # # def menu_pesanan(data_layanan):
# # #     data = muat_pesanan()  # list berisi semua pesanan

# # #     while True:
# # #         tampilkan_menu_pesanan()
# # #         pilihan = layanan.input_angka("Pilih menu: ", 0, 4)

# # #         if pilihan == 1:
# # #             tambah_pesanan(data, data_layanan)
# # #         elif pilihan == 2:
# # #             tampilkan_daftar_pesanan(data)
# # #         elif pilihan == 3:
# # #             lihat_detail(data)
# # #         elif pilihan == 4:
# # #             ubah_status(data)
# # #         else:  # pilihan 0: kembali ke menu utama
# # #             break


# # # # Jika file ini dijalankan langsung
# # # if __name__ == "__main__":
# # #     try:
# # #         menu_pesanan(layanan.muat_data())
# # #     except (KeyboardInterrupt, EOFError):
# # #         print("\n\nProgram dihentikan. Data yang sudah disimpan tetap aman.")


# # # # import json
# # # # import os

# # # # import layanan    # validasi, tampilan, dan data layanan
# # # # import pelanggan  # data pelanggan (ID, nama, telepon)


# # # # # DATA AWAL
# # # # FILE_PESANAN = os.path.join(layanan.FOLDER_PROGRAM, "pesanan.json")

# # # # # tuple: urutan status pesanan
# # # # STATUS_PESANAN = ("Diterima", "Diproses", "Selesai", "Diambil")

# # # # # set: kunci yang wajib ada di setiap pesanan
# # # # # ("telepon" dan "id_pelanggan" sengaja tidak wajib agar pesanan lama tetap terbaca)
# # # # KUNCI_PESANAN = {"kode", "pelanggan", "layanan", "harga_per_kg", "berat_kg", "total", "status"}


# # # # # VALIDASI INPUT
# # # # def input_berat(pesan):
# # # #     while True:
# # # #         teks = input(pesan).strip().replace(",", ".")
# # # #         try:  # exception handling: ValueError kalau input bukan angka
# # # #             berat = float(teks)
# # # #         except ValueError:
# # # #             print("Berat harus berupa angka (contoh: 2.5), coba lagi.")
# # # #             continue

# # # #         if berat <= 0:
# # # #             print("Berat harus lebih dari 0.")
# # # #         elif berat > 1000:
# # # #             print("Berat tidak boleh lebih dari 1000 kg.")
# # # #         else:
# # # #             return round(berat, 2)


# # # # # PENYIMPANAN DATA (FILE JSON)
# # # # def simpan_pesanan(data):
# # # #     try:  # IO: tulis daftar pesanan ke file JSON
# # # #         with open(FILE_PESANAN, "w") as file:
# # # #             json.dump(data, file, indent=4)
# # # #         return True
# # # #     except OSError as error:
# # # #         print(f"Gagal menyimpan data pesanan: {error}")
# # # #         return False


# # # # def muat_pesanan():
# # # #     try:  # IO: baca daftar pesanan dari file JSON
# # # #         with open(FILE_PESANAN, "r") as file:
# # # #             data = json.load(file)
# # # #     except FileNotFoundError:
# # # #         return []
# # # #     except (ValueError, OSError):
# # # #         print("File pesanan.json tidak bisa dibaca, data dimulai dari kosong.")
# # # #         return []

# # # #     # pastikan isi file berupa list dan setiap pesanan punya kunci yang wajib
# # # #     if not isinstance(data, list):
# # # #         return []
# # # #     for pesanan in data:
# # # #         if not isinstance(pesanan, dict) or not KUNCI_PESANAN <= set(pesanan):
# # # #             print("Format pesanan.json tidak sesuai, data dimulai dari kosong.")
# # # #             return []
# # # #     return data


# # # # # FUNGSI BANTU
# # # # def buat_kode(data):
# # # #     """Kode pesanan berikutnya: L001, L002, ... (beda dari ID pelanggan P001)."""
# # # #     nomor_terpakai = [int(item["kode"][1:]) for item in data if item["kode"][1:].isdigit()]
# # # #     nomor_baru = max(nomor_terpakai, default=0) + 1
# # # #     return f"L{nomor_baru:03d}"


# # # # def hitung_total(harga_per_kg, berat_kg):
# # # #     return int(round(harga_per_kg * berat_kg))


# # # # def pilih_nomor_pesanan(data, pesan):
# # # #     """Mengembalikan indeks list, atau None kalau batal."""
# # # #     nomor = layanan.input_angka(pesan + " (0 = batal): ", 0, len(data))
# # # #     if nomor == 0:
# # # #         return None
# # # #     return nomor - 1


# # # # def pilih_pelanggan(data_pelanggan):
# # # #     """Minta ID pelanggan. Mengembalikan data pelanggan, atau None kalau batal."""
# # # #     while True:
# # # #         id_cari = input("Masukkan ID pelanggan (0 = batal): ").strip().upper()
# # # #         if id_cari == "0":
# # # #             return None

# # # #         terpilih = pelanggan.cari_pelanggan(data_pelanggan, id_cari)
# # # #         if terpilih is not None:
# # # #             return terpilih
# # # #         print("ID pelanggan tidak ditemukan, coba lagi.")


# # # # # TAMPILAN
# # # # def tampilkan_daftar_pesanan(data):
# # # #     print()
# # # #     layanan.cetak_garis()
# # # #     print("DAFTAR PESANAN LAUNDRY")
# # # #     layanan.cetak_garis()

# # # #     if len(data) == 0:
# # # #         print("Belum ada pesanan.")
# # # #         layanan.cetak_garis()
# # # #         return

# # # #     print(f"{'No':<4}{'Kode':<6}{'Pelanggan':<16}{'Layanan':<14}{'Berat':<8}{'Total':<13}Status")
# # # #     print("-" * 70)

# # # #     nomor = 1
# # # #     for pesanan in data:
# # # #         berat = f"{pesanan['berat_kg']} kg"
# # # #         total = layanan.format_rupiah(pesanan["total"])
# # # #         print(
# # # #             f"{nomor:<4}{pesanan['kode']:<6}{pesanan['pelanggan'][:15]:<16}"
# # # #             f"{pesanan['layanan'][:13]:<14}{berat:<8}{total:<13}{pesanan['status']}"
# # # #         )
# # # #         nomor = nomor + 1

# # # #     print("-" * 70)


# # # # def tampilkan_detail(pesanan):
# # # #     print()
# # # #     layanan.cetak_garis()
# # # #     print(f"DETAIL PESANAN {pesanan['kode']}")
# # # #     layanan.cetak_garis()
# # # #     print(f"ID Pelanggan   : {pesanan.get('id_pelanggan', '-')}")
# # # #     print(f"Nama Pelanggan : {pesanan['pelanggan']}")
# # # #     print(f"No. Telepon    : {pesanan.get('telepon', '-')}")
# # # #     print(f"Jenis Layanan  : {pesanan['layanan']}")
# # # #     print(f"Harga per kg   : {layanan.format_rupiah(pesanan['harga_per_kg'])}")
# # # #     print(f"Berat Pakaian  : {pesanan['berat_kg']} kg")
# # # #     print(f"Total Biaya    : {layanan.format_rupiah(pesanan['total'])}")
# # # #     print(f"Status         : {pesanan['status']}")
# # # #     layanan.cetak_garis()


# # # # # FITUR PESANAN
# # # # def tambah_pesanan(data, data_layanan):
# # # #     print("\n--- TAMBAH PESANAN ---")
# # # #     if len(data_layanan) == 0:
# # # #         print("Belum ada layanan. Tambahkan layanan dulu di menu Kelola Layanan.")
# # # #         return

# # # #     # dibaca ulang setiap kali agar pelanggan yang baru ditambah langsung muncul
# # # #     data_pelanggan = pelanggan.baca_data()
# # # #     if len(data_pelanggan) == 0:
# # # #         print("Belum ada pelanggan. Tambahkan pelanggan dulu di menu Pelanggan.")
# # # #         return

# # # #     pelanggan.tampilkan(data_pelanggan)
# # # #     terpilih = pilih_pelanggan(data_pelanggan)
# # # #     if terpilih is None:
# # # #         print("Dibatalkan.")
# # # #         return
# # # #     print(f"\nPelanggan : {terpilih['nama']} ({terpilih['telepon']})")

# # # #     layanan.tampilkan_daftar(data_layanan)  # daftar layanan terbaru
# # # #     indeks = layanan.pilih_nomor_layanan(data_layanan, "Pilih nomor layanan")
# # # #     if indeks is None:
# # # #         print("Dibatalkan.")
# # # #         return
# # # #     jenis = data_layanan[indeks]

# # # #     berat = input_berat("Berat pakaian (kg)    : ")
# # # #     total = hitung_total(jenis["harga"], berat)

# # # #     print(f"\nPelanggan : {terpilih['nama']} ({terpilih['id']})")
# # # #     print(f"Layanan   : {jenis['nama']} ({layanan.format_rupiah(jenis['harga'])}/kg)")
# # # #     print(f"Total biaya: {layanan.format_rupiah(total)}")
# # # #     if not layanan.konfirmasi("Simpan pesanan ini?"):
# # # #         print("Pesanan dibatalkan.")
# # # #         return

# # # #     pesanan = {  # dictionary: satu pesanan
# # # #         "kode": buat_kode(data),
# # # #         "id_pelanggan": terpilih["id"],
# # # #         "pelanggan": terpilih["nama"],
# # # #         "telepon": terpilih["telepon"],
# # # #         "layanan": jenis["nama"],
# # # #         "harga_per_kg": jenis["harga"],
# # # #         "berat_kg": berat,
# # # #         "total": total,
# # # #         "status": STATUS_PESANAN[0],
# # # #     }
# # # #     data.append(pesanan)  # list: tambahkan ke daftar pesanan

# # # #     if simpan_pesanan(data):
# # # #         print(f"Pesanan {pesanan['kode']} berhasil disimpan.")


# # # # def ubah_status(data):
# # # #     print("\n--- UBAH STATUS PESANAN ---")
# # # #     if len(data) == 0:
# # # #         print("Belum ada pesanan.")
# # # #         return

# # # #     tampilkan_daftar_pesanan(data)
# # # #     indeks = pilih_nomor_pesanan(data, "Nomor pesanan")
# # # #     if indeks is None:
# # # #         print("Dibatalkan.")
# # # #         return

# # # #     pesanan = data[indeks]
# # # #     print(f"\nStatus saat ini: {pesanan['status']}")
# # # #     nomor = 1
# # # #     for status in STATUS_PESANAN:
# # # #         print(f"{nomor}. {status}")
# # # #         nomor = nomor + 1

# # # #     pilihan = layanan.input_angka("Pilih status baru (0 = batal): ", 0, len(STATUS_PESANAN))
# # # #     if pilihan == 0:
# # # #         print("Dibatalkan.")
# # # #         return

# # # #     pesanan["status"] = STATUS_PESANAN[pilihan - 1]
# # # #     if simpan_pesanan(data):
# # # #         print(f"Status pesanan {pesanan['kode']} diubah menjadi '{pesanan['status']}'.")


# # # # def lihat_detail(data):
# # # #     print("\n--- DETAIL PESANAN ---")
# # # #     if len(data) == 0:
# # # #         print("Belum ada pesanan.")
# # # #         return

# # # #     tampilkan_daftar_pesanan(data)
# # # #     indeks = pilih_nomor_pesanan(data, "Nomor pesanan")
# # # #     if indeks is None:
# # # #         print("Dibatalkan.")
# # # #         return

# # # #     tampilkan_detail(data[indeks])


# # # # # SUBMENU PESANAN (dipanggil dari main.py)
# # # # def tampilkan_menu_pesanan():
# # # #     print()
# # # #     print("================================")
# # # #     print("MANAJEMEN PESANAN LAUNDRY")
# # # #     print("================================")
# # # #     print("1. Tambah Pesanan")
# # # #     print("2. Lihat Daftar Pesanan")
# # # #     print("3. Lihat Detail Pesanan")
# # # #     print("4. Ubah Status Pesanan")
# # # #     print("0. Kembali")
# # # #     print("================================")


# # # # def menu_pesanan(data_layanan):
# # # #     data = muat_pesanan()  # list berisi semua pesanan

# # # #     while True:
# # # #         tampilkan_menu_pesanan()
# # # #         pilihan = layanan.input_angka("Pilih menu: ", 0, 4)

# # # #         if pilihan == 1:
# # # #             tambah_pesanan(data, data_layanan)
# # # #         elif pilihan == 2:
# # # #             tampilkan_daftar_pesanan(data)
# # # #         elif pilihan == 3:
# # # #             lihat_detail(data)
# # # #         elif pilihan == 4:
# # # #             ubah_status(data)
# # # #         else:  # pilihan 0: kembali ke menu utama
# # # #             break


# # # # # Jika file ini dijalankan langsung
# # # # if __name__ == "__main__":
# # # #     try:
# # # #         menu_pesanan(layanan.muat_data())
# # # #     except (KeyboardInterrupt, EOFError):
# # # #         print("\n\nProgram dihentikan. Data yang sudah disimpan tetap aman.")

# # # # import json
# # # # import os

# # # # import layanan    # validasi, tampilan, dan data layanan
# # # # import pelanggan  # data pelanggan (ID, nama, telepon)


# # # # # DATA AWAL
# # # # FILE_PESANAN = os.path.join(layanan.FOLDER_PROGRAM, "pesanan.json")

# # # # # tuple: urutan status pesanan
# # # # STATUS_PESANAN = ("Diterima", "Diproses", "Selesai", "Diambil")

# # # # # set: kunci yang wajib ada di setiap pesanan
# # # # # ("telepon" dan "id_pelanggan" sengaja tidak wajib agar pesanan lama tetap terbaca)
# # # # KUNCI_PESANAN = {"kode", "pelanggan", "layanan", "harga_per_kg", "berat_kg", "total", "status"}


# # # # # VALIDASI INPUT
# # # # def input_berat(pesan):
# # # #     while True:
# # # #         teks = input(pesan).strip().replace(",", ".")
# # # #         try:
# # # #             berat = float(teks)
# # # #         except ValueError:
# # # #             print("Berat harus berupa angka (contoh: 2.5), coba lagi.")
# # # #             continue

# # # #         if berat <= 0:
# # # #             print("Berat harus lebih dari 0.")
# # # #         elif berat > 1000:
# # # #             print("Berat tidak boleh lebih dari 1000 kg.")
# # # #         else:
# # # #             return round(berat, 2)


# # # # # PENYIMPANAN DATA (FILE JSON)
# # # # def simpan_pesanan(data):
# # # #     try:
# # # #         with open(FILE_PESANAN, "w") as file:
# # # #             json.dump(data, file, indent=4)
# # # #         return True
# # # #     except OSError as error:
# # # #         print(f"Gagal menyimpan data pesanan: {error}")
# # # #         return False


# # # # def muat_pesanan():
# # # #     try:
# # # #         with open(FILE_PESANAN, "r") as file:
# # # #             data = json.load(file)
# # # #     except FileNotFoundError:
# # # #         return []
# # # #     except (ValueError, OSError):
# # # #         print("File pesanan.json tidak bisa dibaca, data dimulai dari kosong.")
# # # #         return []

# # # #     # pastikan isi file berupa list dan setiap pesanan punya kunci yang wajib
# # # #     if not isinstance(data, list):
# # # #         return []
# # # #     for pesanan in data:
# # # #         if not isinstance(pesanan, dict) or not KUNCI_PESANAN <= set(pesanan):
# # # #             print("Format pesanan.json tidak sesuai, data dimulai dari kosong.")
# # # #             return []
# # # #     return data


# # # # # FUNGSI BANTU
# # # # def buat_kode(data):
# # # #     """Kode pesanan berikutnya: L001, L002, ... (beda dari ID pelanggan P001)."""
# # # #     nomor_terpakai = [int(item["kode"][1:]) for item in data if item["kode"][1:].isdigit()]
# # # #     nomor_baru = max(nomor_terpakai, default=0) + 1
# # # #     return f"L{nomor_baru:03d}"


# # # # def hitung_total(harga_per_kg, berat_kg):
# # # #     return int(round(harga_per_kg * berat_kg))


# # # # def pilih_nomor_pesanan(data, pesan):
# # # #     """Mengembalikan indeks list, atau None kalau batal."""
# # # #     nomor = layanan.input_angka(pesan + " (0 = batal): ", 0, len(data))
# # # #     if nomor == 0:
# # # #         return None
# # # #     return nomor - 1


# # # # def pilih_pelanggan(data_pelanggan):
# # # #     """Minta ID pelanggan. Mengembalikan data pelanggan, atau None kalau batal."""
# # # #     while True:
# # # #         id_cari = input("Masukkan ID pelanggan (0 = batal): ").strip().upper()
# # # #         if id_cari == "0":
# # # #             return None

# # # #         terpilih = pelanggan.cari_pelanggan(data_pelanggan, id_cari)
# # # #         if terpilih is not None:
# # # #             return terpilih
# # # #         print("ID pelanggan tidak ditemukan, coba lagi.")


# # # # # TAMPILAN
# # # # def tampilkan_daftar_pesanan(data):
# # # #     print()
# # # #     layanan.cetak_garis()
# # # #     print("DAFTAR PESANAN LAUNDRY")
# # # #     layanan.cetak_garis()

# # # #     if len(data) == 0:
# # # #         print("Belum ada pesanan.")
# # # #         layanan.cetak_garis()
# # # #         return

# # # #     print(f"{'No':<4}{'Kode':<6}{'Pelanggan':<16}{'Layanan':<14}{'Berat':<8}{'Total':<13}Status")
# # # #     print("-" * 70)

# # # #     nomor = 1
# # # #     for pesanan in data:
# # # #         berat = f"{pesanan['berat_kg']} kg"
# # # #         total = layanan.format_rupiah(pesanan["total"])
# # # #         print(
# # # #             f"{nomor:<4}{pesanan['kode']:<6}{pesanan['pelanggan'][:15]:<16}"
# # # #             f"{pesanan['layanan'][:13]:<14}{berat:<8}{total:<13}{pesanan['status']}"
# # # #         )
# # # #         nomor = nomor + 1

# # # #     print("-" * 70)


# # # # def tampilkan_detail(pesanan):
# # # #     print()
# # # #     layanan.cetak_garis()
# # # #     print(f"DETAIL PESANAN {pesanan['kode']}")
# # # #     layanan.cetak_garis()
# # # #     print(f"ID Pelanggan   : {pesanan.get('id_pelanggan', '-')}")
# # # #     print(f"Nama Pelanggan : {pesanan['pelanggan']}")
# # # #     print(f"No. Telepon    : {pesanan.get('telepon', '-')}")
# # # #     print(f"Jenis Layanan  : {pesanan['layanan']}")
# # # #     print(f"Harga per kg   : {layanan.format_rupiah(pesanan['harga_per_kg'])}")
# # # #     print(f"Berat Pakaian  : {pesanan['berat_kg']} kg")
# # # #     print(f"Total Biaya    : {layanan.format_rupiah(pesanan['total'])}")
# # # #     print(f"Status         : {pesanan['status']}")
# # # #     layanan.cetak_garis()


# # # # # FITUR PESANAN
# # # # def tambah_pesanan(data, data_layanan):
# # # #     print("\n--- TAMBAH PESANAN ---")
# # # #     if len(data_layanan) == 0:
# # # #         print("Belum ada layanan. Tambahkan layanan dulu di menu Kelola Layanan.")
# # # #         return

# # # #     # dibaca ulang setiap kali agar pelanggan yang baru ditambah langsung muncul
# # # #     data_pelanggan = pelanggan.baca_data()
# # # #     if len(data_pelanggan) == 0:
# # # #         print("Belum ada pelanggan. Tambahkan pelanggan dulu di menu Pelanggan.")
# # # #         return

# # # #     pelanggan.tampilkan(data_pelanggan)
# # # #     terpilih = pilih_pelanggan(data_pelanggan)
# # # #     if terpilih is None:
# # # #         print("Dibatalkan.")
# # # #         return
# # # #     print(f"\nPelanggan : {terpilih['nama']} ({terpilih['telepon']})")

# # # #     layanan.tampilkan_daftar(data_layanan)  # daftar layanan terbaru
# # # #     indeks = layanan.pilih_nomor_layanan(data_layanan, "Pilih nomor layanan")
# # # #     if indeks is None:
# # # #         print("Dibatalkan.")
# # # #         return
# # # #     jenis = data_layanan[indeks]

# # # #     berat = input_berat("Berat pakaian (kg)    : ")
# # # #     total = hitung_total(jenis["harga"], berat)

# # # #     print(f"\nPelanggan : {terpilih['nama']} ({terpilih['id']})")
# # # #     print(f"Layanan   : {jenis['nama']} ({layanan.format_rupiah(jenis['harga'])}/kg)")
# # # #     print(f"Total biaya: {layanan.format_rupiah(total)}")
# # # #     if not layanan.konfirmasi("Simpan pesanan ini?"):
# # # #         print("Pesanan dibatalkan.")
# # # #         return

# # # #     pesanan = {
# # # #         "kode": buat_kode(data),
# # # #         "id_pelanggan": terpilih["id"],
# # # #         "pelanggan": terpilih["nama"],
# # # #         "telepon": terpilih["telepon"],
# # # #         "layanan": jenis["nama"],
# # # #         "harga_per_kg": jenis["harga"],
# # # #         "berat_kg": berat,
# # # #         "total": total,
# # # #         "status": STATUS_PESANAN[0],
# # # #     }
# # # #     data.append(pesanan)

# # # #     if simpan_pesanan(data):
# # # #         print(f"Pesanan {pesanan['kode']} berhasil disimpan.")


# # # # def ubah_status(data):
# # # #     print("\n--- UBAH STATUS PESANAN ---")
# # # #     if len(data) == 0:
# # # #         print("Belum ada pesanan.")
# # # #         return

# # # #     tampilkan_daftar_pesanan(data)
# # # #     indeks = pilih_nomor_pesanan(data, "Nomor pesanan")
# # # #     if indeks is None:
# # # #         print("Dibatalkan.")
# # # #         return

# # # #     pesanan = data[indeks]
# # # #     print(f"\nStatus saat ini: {pesanan['status']}")
# # # #     nomor = 1
# # # #     for status in STATUS_PESANAN:
# # # #         print(f"{nomor}. {status}")
# # # #         nomor = nomor + 1

# # # #     pilihan = layanan.input_angka("Pilih status baru (0 = batal): ", 0, len(STATUS_PESANAN))
# # # #     if pilihan == 0:
# # # #         print("Dibatalkan.")
# # # #         return

# # # #     pesanan["status"] = STATUS_PESANAN[pilihan - 1]
# # # #     if simpan_pesanan(data):
# # # #         print(f"Status pesanan {pesanan['kode']} diubah menjadi '{pesanan['status']}'.")


# # # # def lihat_detail(data):
# # # #     print("\n--- DETAIL PESANAN ---")
# # # #     if len(data) == 0:
# # # #         print("Belum ada pesanan.")
# # # #         return

# # # #     tampilkan_daftar_pesanan(data)
# # # #     indeks = pilih_nomor_pesanan(data, "Nomor pesanan")
# # # #     if indeks is None:
# # # #         print("Dibatalkan.")
# # # #         return

# # # #     tampilkan_detail(data[indeks])


# # # # # SUBMENU PESANAN (dipanggil dari main.py)
# # # # def tampilkan_menu_pesanan():
# # # #     print()
# # # #     print("================================")
# # # #     print("MANAJEMEN PESANAN LAUNDRY")
# # # #     print("================================")
# # # #     print("1. Tambah Pesanan")
# # # #     print("2. Lihat Daftar Pesanan")
# # # #     print("3. Lihat Detail Pesanan")
# # # #     print("4. Ubah Status Pesanan")
# # # #     print("0. Kembali")
# # # #     print("================================")


# # # # def menu_pesanan(data_layanan):
# # # #     data = muat_pesanan()

# # # #     while True:
# # # #         tampilkan_menu_pesanan()
# # # #         pilihan = layanan.input_angka("Pilih menu: ", 0, 4)

# # # #         if pilihan == 1:
# # # #             tambah_pesanan(data, data_layanan)
# # # #         elif pilihan == 2:
# # # #             tampilkan_daftar_pesanan(data)
# # # #         elif pilihan == 3:
# # # #             lihat_detail(data)
# # # #         elif pilihan == 4:
# # # #             ubah_status(data)
# # # #         else:  # pilihan 0: kembali ke menu utama
# # # #             break


# # # # # Jika file ini dijalankan langsung
# # # # if __name__ == "__main__":
# # # #     try:
# # # #         menu_pesanan(layanan.muat_data())
# # # #     except (KeyboardInterrupt, EOFError):
# # # #         print("\n\nProgram dihentikan. Data yang sudah disimpan tetap aman.")

# # # # # import json
# # # # # import os

# # # # # import layanan  # file 1: dipakai untuk validasi, tampilan, dan data layanan


# # # # # # DATA AWAL
# # # # # FILE_PESANAN = os.path.join(layanan.FOLDER_PROGRAM, "pesanan.json")

# # # # # # tuple: urutan status pesanan
# # # # # STATUS_PESANAN = ("Diterima", "Diproses", "Selesai", "Diambil")

# # # # # # set: kunci yang wajib ada di setiap pesanan
# # # # # KUNCI_PESANAN = {"kode", "pelanggan", "layanan", "harga_per_kg", "berat_kg", "total", "status"}


# # # # # # VALIDASI INPUT
# # # # # def input_berat(pesan):
# # # # #     while True:
# # # # #         teks = input(pesan).strip().replace(",", ".")
# # # # #         try:
# # # # #             berat = float(teks)
# # # # #         except ValueError:
# # # # #             print("Berat harus berupa angka (contoh: 2.5), coba lagi.")
# # # # #             continue

# # # # #         if berat <= 0:
# # # # #             print("Berat harus lebih dari 0.")
# # # # #         elif berat > 1000:
# # # # #             print("Berat tidak boleh lebih dari 1000 kg.")
# # # # #         else:
# # # # #             return round(berat, 2)




# # # # # # PENYIMPANAN DATA (FILE JSON)
# # # # # def simpan_pesanan(data):
# # # # #     try:
# # # # #         with open(FILE_PESANAN, "w") as file:
# # # # #             json.dump(data, file, indent=4)
# # # # #         return True
# # # # #     except OSError as error:
# # # # #         print(f"Gagal menyimpan data pesanan: {error}")
# # # # #         return False


# # # # # def muat_pesanan():
# # # # #     try:
# # # # #         with open(FILE_PESANAN, "r") as file:
# # # # #             data = json.load(file)
# # # # #     except FileNotFoundError:
# # # # #         return []
# # # # #     except (ValueError, OSError):
# # # # #         print("File pesanan.json tidak bisa dibaca, data dimulai dari kosong.")
# # # # #         return []

# # # # #     # pastikan isi file berupa list dan setiap pesanan punya kunci yang wajib
# # # # #     if not isinstance(data, list):
# # # # #         return []
# # # # #     for pesanan in data:
# # # # #         if not isinstance(pesanan, dict) or not KUNCI_PESANAN <= set(pesanan):
# # # # #             print("Format pesanan.json tidak sesuai, data dimulai dari kosong.")
# # # # #             return []
# # # # #     return data


# # # # # # FUNGSI BANTU



# # # # # def hitung_total(harga_per_kg, berat_kg):
# # # # #     return int(round(harga_per_kg * berat_kg))


# # # # # def pilih_nomor_pesanan(data, pesan):
# # # # #     """Mengembalikan indeks list, atau None kalau batal."""
# # # # #     nomor = layanan.input_angka(pesan + " (0 = batal): ", 0, len(data))
# # # # #     if nomor == 0:
# # # # #         return None
# # # # #     return nomor - 1


# # # # # # TAMPILAN
# # # # # def tampilkan_daftar_pesanan(data):
# # # # #     print()
# # # # #     layanan.cetak_garis()
# # # # #     print("DAFTAR PESANAN LAUNDRY")
# # # # #     layanan.cetak_garis()

# # # # #     if len(data) == 0:
# # # # #         print("Belum ada pesanan.")
# # # # #         layanan.cetak_garis()
# # # # #         return

# # # # #     print(f"{'No':<4}{'Kode':<6}{'Pelanggan':<16}{'Layanan':<14}{'Berat':<8}{'Total':<13}Status")
# # # # #     print("-" * 70)

# # # # #     nomor = 1
# # # # #     for pesanan in data:
# # # # #         berat = f"{pesanan['berat_kg']} kg"
# # # # #         total = layanan.format_rupiah(pesanan["total"])
# # # # #         print(
# # # # #             f"{nomor:<4}{pesanan['kode']:<6}{pesanan['pelanggan'][:15]:<16}"
# # # # #             f"{pesanan['layanan'][:13]:<14}{berat:<8}{total:<13}{pesanan['status']}"
# # # # #         )
# # # # #         nomor = nomor + 1

# # # # #     print("-" * 70)


# # # # # def tampilkan_detail(pesanan):
# # # # #     print()
# # # # #     layanan.cetak_garis()
# # # # #     print(f"DETAIL PESANAN {pesanan['kode']}")
# # # # #     layanan.cetak_garis()
# # # # #     print(f"Nama Pelanggan : {pesanan['pelanggan']}")
# # # # #     print(f"No. Telepon    : {pesanan.get('telepon', '-')}")
# # # # #     print(f"Jenis Layanan  : {pesanan['layanan']}")
# # # # #     print(f"Harga per kg   : {layanan.format_rupiah(pesanan['harga_per_kg'])}")
# # # # #     print(f"Berat Pakaian  : {pesanan['berat_kg']} kg")
# # # # #     print(f"Total Biaya    : {layanan.format_rupiah(pesanan['total'])}")
# # # # #     print(f"Status         : {pesanan['status']}")
# # # # #     layanan.cetak_garis()


# # # # # # FITUR PESANAN
# # # # # def tambah_pesanan(data, data_layanan):
# # # # #     print("\n--- TAMBAH PESANAN ---")
# # # # #     if len(data_layanan) == 0:
# # # # #         print("Belum ada layanan. Tambahkan layanan dulu di menu Kelola Layanan.")
# # # # #         return

# # # # #     pelanggan = layanan.input_teks("Nama pelanggan        : ")

# # # # #     layanan.tampilkan_daftar(data_layanan)  # daftar layanan terbaru
# # # # #     indeks = layanan.pilih_nomor_layanan(data_layanan, "Pilih nomor layanan")
# # # # #     if indeks is None:
# # # # #         print("Dibatalkan.")
# # # # #         return
# # # # #     jenis = data_layanan[indeks]

# # # # #     berat = input_berat("Berat pakaian (kg)    : ")
# # # # #     total = hitung_total(jenis["harga"], berat)

# # # # #     print(f"\nLayanan : {jenis['nama']} ({layanan.format_rupiah(jenis['harga'])}/kg)")
# # # # #     print(f"Total biaya: {layanan.format_rupiah(total)}")
# # # # #     if not layanan.konfirmasi("Simpan pesanan ini?"):
# # # # #         print("Pesanan dibatalkan.")
# # # # #         return

# # # # #     pesanan = {
# # # # #         "kode": buat_kode(data),
# # # # #         "pelanggan": pelanggan,
# # # # #         "telepon": telepon,
# # # # #         "layanan": jenis["nama"],
# # # # #         "harga_per_kg": jenis["harga"],
# # # # #         "berat_kg": berat,
# # # # #         "total": total,
# # # # #         "status": STATUS_PESANAN[0],
# # # # #     }
# # # # #     data.append(pesanan)

# # # # #     if simpan_pesanan(data):
# # # # #         print(f"Pesanan {pesanan['kode']} berhasil disimpan.")


# # # # # def ubah_status(data):
# # # # #     print("\n--- UBAH STATUS PESANAN ---")
# # # # #     if len(data) == 0:
# # # # #         print("Belum ada pesanan.")
# # # # #         return

# # # # #     tampilkan_daftar_pesanan(data)
# # # # #     indeks = pilih_nomor_pesanan(data, "Nomor pesanan")
# # # # #     if indeks is None:
# # # # #         print("Dibatalkan.")
# # # # #         return

# # # # #     pesanan = data[indeks]
# # # # #     print(f"\nStatus saat ini: {pesanan['status']}")
# # # # #     nomor = 1
# # # # #     for status in STATUS_PESANAN:
# # # # #         print(f"{nomor}. {status}")
# # # # #         nomor = nomor + 1

# # # # #     pilihan = layanan.input_angka("Pilih status baru (0 = batal): ", 0, len(STATUS_PESANAN))
# # # # #     if pilihan == 0:
# # # # #         print("Dibatalkan.")
# # # # #         return

# # # # #     pesanan["status"] = STATUS_PESANAN[pilihan - 1]
# # # # #     if simpan_pesanan(data):
# # # # #         print(f"Status pesanan {pesanan['kode']} diubah menjadi '{pesanan['status']}'.")


# # # # # def lihat_detail(data):
# # # # #     print("\n--- DETAIL PESANAN ---")
# # # # #     if len(data) == 0:
# # # # #         print("Belum ada pesanan.")
# # # # #         return

# # # # #     tampilkan_daftar_pesanan(data)
# # # # #     indeks = pilih_nomor_pesanan(data, "Nomor pesanan")
# # # # #     if indeks is None:
# # # # #         print("Dibatalkan.")
# # # # #         return

# # # # #     tampilkan_detail(data[indeks])


# # # # # # SUBMENU PESANAN (dipanggil dari main.py)
# # # # # def tampilkan_menu_pesanan():
# # # # #     print()
# # # # #     print("================================")
# # # # #     print("MANAJEMEN PESANAN LAUNDRY")
# # # # #     print("================================")
# # # # #     print("1. Tambah Pesanan")
# # # # #     print("2. Lihat Daftar Pesanan")
# # # # #     print("3. Lihat Detail Pesanan")
# # # # #     print("4. Ubah Status Pesanan")
# # # # #     print("0. Kembali")
# # # # #     print("================================")


# # # # # def menu_pesanan(data_layanan):
# # # # #     data = muat_pesanan()

# # # # #     while True:
# # # # #         tampilkan_menu_pesanan()
# # # # #         pilihan = layanan.input_angka("Pilih menu: ", 0, 4)

# # # # #         if pilihan == 1:
# # # # #             tambah_pesanan(data, data_layanan)
# # # # #         elif pilihan == 2:
# # # # #             tampilkan_daftar_pesanan(data)
# # # # #         elif pilihan == 3:
# # # # #             lihat_detail(data)
# # # # #         elif pilihan == 4:
# # # # #             ubah_status(data)
# # # # #         else:
# # # # #             break
# # # # # # bagian else diubah ke menu utama 

# # # # # # Jika file ini dijalankan langsung
# # # # # if __name__ == "__main__":
# # # # #     try:
# # # # #         menu_pesanan(layanan.muat_data())
# # # # #     except (KeyboardInterrupt, EOFError):
# # # # #         print("\n\nProgram dihentikan. Data yang sudah disimpan tetap aman.")














# # # # # # import json
# # # # # # import os

# # # # # # import layanan  # file 1: dipakai ulang untuk validasi, tampilan, dan data layanan


# # # # # # # PENGATURAN DAN DATA AWAL

# # # # # # FILE_PESANAN = os.path.join(layanan.FOLDER_PROGRAM, "pelanggan.json")

# # # # # # # tuple berisi urutan status pesanan
# # # # # # STATUS_PESANAN = ("Diterima", "Diproses", "Selesai", "Diambil")

# # # # # # # set berisi kunci yang wajib ada di setiap pesanan
# # # # # # # ("telepon" sengaja tidak wajib agar data lama tanpa telepon tetap terbaca)
# # # # # # KUNCI_PESANAN = {"kode", "pelanggan", "layanan", "harga_per_kg", "berat_kg", "total", "status"}


# # # # # # # VALIDASI INPUT

# # # # # # def input_berat(pesan, maksimal=100):
# # # # # #     """Minta berat dalam kg. Boleh desimal (contoh: 2.5 atau 2,5)."""
# # # # # #     while True:
# # # # # #         teks = input(pesan).strip().replace(",", ".")
# # # # # #         try:
# # # # # #             berat = float(teks)
# # # # # #         except ValueError:
# # # # # #             print("Berat harus berupa angka (contoh: 2.5), coba lagi.")
# # # # # #             continue

# # # # # #         if berat != berat or berat in (float("inf"), float("-inf")):
# # # # # #             print("Berat tidak valid, coba lagi.")
# # # # # #         elif berat <= 0:
# # # # # #             print("Berat harus lebih dari 0.")
# # # # # #         elif berat > maksimal:
# # # # # #             print(f"Berat tidak boleh lebih dari {maksimal} kg.")
# # # # # #         else:
# # # # # #             return round(berat, 2)


# # # # # # def input_telepon(pesan):
# # # # # #     """Minta nomor telepon. Boleh diawali + dan boleh memakai spasi/strip."""
# # # # # #     while True:
# # # # # #         teks = input(pesan).strip()
# # # # # #         nomor = teks.replace(" ", "").replace("-", "")
# # # # # #         isi = nomor[1:] if nomor.startswith("+") else nomor

# # # # # #         if not isi.isdigit():
# # # # # #             print("Nomor telepon hanya boleh berisi angka (contoh: 081234567890).")
# # # # # #         elif not 9 <= len(isi) <= 15:
# # # # # #             print("Nomor telepon harus 9 sampai 15 digit.")
# # # # # #         else:
# # # # # #             return nomor


# # # # # # # PENYIMPANAN DATA (FILE JSON)

# # # # # # def simpan_pesanan(data):
# # # # # #     try:
# # # # # #         with open(FILE_PESANAN, "w") as file:
# # # # # #             json.dump(data, file, indent=4)
# # # # # #         return True
# # # # # #     except OSError as error:
# # # # # #         print(f"Gagal menyimpan data pesanan: {error}")
# # # # # #         return False


# # # # # # def pesanan_valid(data):
# # # # # #     if not isinstance(data, list):
# # # # # #         return False
# # # # # #     for pesanan in data:
# # # # # #         if not isinstance(pesanan, dict) or not KUNCI_PESANAN <= set(pesanan):
# # # # # #             return False
# # # # # #     return True


# # # # # # def muat_pesanan():
# # # # # #     try:
# # # # # #         with open(FILE_PESANAN, "r") as file:
# # # # # #             data = json.load(file)
# # # # # #         if not pesanan_valid(data):
# # # # # #             raise ValueError("Isi file tidak sesuai format")
# # # # # #         return data

# # # # # #     except FileNotFoundError:
# # # # # #         return []

# # # # # #     except ValueError:  # termasuk json.JSONDecodeError
# # # # # #         print("File pelanggan rusak. File lama disimpan sebagai pelanggan.json.rusak.")
# # # # # #         try:
# # # # # #             os.replace(FILE_PESANAN, FILE_PESANAN + ".rusak")
# # # # # #         except OSError:
# # # # # #             pass
# # # # # #         return []

# # # # # #     except OSError as error:
# # # # # #         print(f"Gagal membaca file pelanggan: {error}")
# # # # # #         return []


# # # # # # # FUNGSI BANTU

# # # # # # def buat_kode(data):
# # # # # #     """Buat kode pesanan berikutnya, contoh: P001, P002, ..."""
# # # # # #     nomor_terpakai = [int(item["kode"][1:]) for item in data if item["kode"][1:].isdigit()]
# # # # # #     nomor_baru = max(nomor_terpakai, default=0) + 1
# # # # # #     return f"P{nomor_baru:03d}"


# # # # # # def hitung_total(harga_per_kg, berat_kg):
# # # # # #     """Total biaya = harga per kg x berat (dibulatkan ke rupiah)."""
# # # # # #     return int(round(harga_per_kg * berat_kg))


# # # # # # def pilih_nomor_pesanan(data, pesan):
# # # # # #     """Minta nomor pesanan. Mengembalikan indeks list, atau None kalau batal."""
# # # # # #     nomor = layanan.input_angka(pesan + " (0 = batal): ", 0, len(data))
# # # # # #     if nomor == 0:
# # # # # #         return None
# # # # # #     return nomor - 1


# # # # # # # TAMPILAN

# # # # # # def tampilkan_daftar_pesanan(data):
# # # # # #     """Tampilkan seluruh pesanan dalam bentuk tabel."""
# # # # # #     print()
# # # # # #     layanan.cetak_garis()
# # # # # #     print("DAFTAR PESANAN LAUNDRY")
# # # # # #     layanan.cetak_garis()

# # # # # #     if len(data) == 0:
# # # # # #         print("Belum ada pesanan.")
# # # # # #         layanan.cetak_garis()
# # # # # #         return

# # # # # #     print(f"{'No':<4}{'Kode':<6}{'Pelanggan':<16}{'Layanan':<14}{'Berat':<8}{'Total':<13}Status")
# # # # # #     print("-" * 70)

# # # # # #     nomor = 1
# # # # # #     for pesanan in data:
# # # # # #         berat = f"{pesanan['berat_kg']} kg"
# # # # # #         total = layanan.format_rupiah(pesanan["total"])
# # # # # #         print(
# # # # # #             f"{nomor:<4}{pesanan['kode']:<6}{pesanan['pelanggan'][:15]:<16}"
# # # # # #             f"{pesanan['layanan'][:13]:<14}{berat:<8}{total:<13}{pesanan['status']}"
# # # # # #         )
# # # # # #         nomor = nomor + 1

# # # # # #     print("-" * 70)


# # # # # # def tampilkan_detail(pesanan):
# # # # # #     print()
# # # # # #     layanan.cetak_garis()
# # # # # #     print(f"DETAIL PESANAN {pesanan['kode']}")
# # # # # #     layanan.cetak_garis()
# # # # # #     print(f"Nama Pelanggan : {pesanan['pelanggan']}")
# # # # # #     print(f"No. Telepon    : {pesanan.get('telepon', '-')}")
# # # # # #     print(f"Jenis Layanan  : {pesanan['layanan']}")
# # # # # #     print(f"Harga per kg   : {layanan.format_rupiah(pesanan['harga_per_kg'])}")
# # # # # #     print(f"Berat Pakaian  : {pesanan['berat_kg']} kg")
# # # # # #     print(f"Total Biaya    : {layanan.format_rupiah(pesanan['total'])}")
# # # # # #     print(f"Status         : {pesanan['status']}")
# # # # # #     layanan.cetak_garis()


# # # # # # # FITUR PESANAN

# # # # # # def tambah_pesanan(data, data_layanan):
# # # # # #     print("\n--- TAMBAH PESANAN ---")
# # # # # #     if len(data_layanan) == 0:
# # # # # #         print("Belum ada layanan. Tambahkan layanan dulu di menu Kelola Layanan.")
# # # # # #         return

# # # # # #     pelanggan = layanan.input_teks("Nama pelanggan        : ")
# # # # # #     telepon = input_telepon("No. telepon          : ")

# # # # # #     # daftar layanan terbaru (hasil tambah/ubah/hapus di menu Kelola Layanan)
# # # # # #     layanan.tampilkan_daftar(data_layanan)
# # # # # #     indeks = layanan.pilih_nomor_layanan(data_layanan, "Pilih nomor layanan")
# # # # # #     if indeks is None:
# # # # # #         print("Dibatalkan.")
# # # # # #         return
# # # # # #     jenis = data_layanan[indeks]

# # # # # #     berat = input_berat("Berat pakaian (kg)    : ")
# # # # # #     total = hitung_total(jenis["harga"], berat)

# # # # # #     print(f"\nLayanan : {jenis['nama']} ({layanan.format_rupiah(jenis['harga'])}/kg)")
# # # # # #     print(f"Total biaya: {layanan.format_rupiah(total)}")
# # # # # #     if not layanan.konfirmasi("Simpan pesanan ini?"):
# # # # # #         print("Pesanan dibatalkan.")
# # # # # #         return

# # # # # #     pesanan = {
# # # # # #         "kode": buat_kode(data),
# # # # # #         "pelanggan": pelanggan,
# # # # # #         "telepon": telepon,
# # # # # #         "layanan": jenis["nama"],
# # # # # #         "harga_per_kg": jenis["harga"],  # harga disalin agar pesanan lama tidak berubah
# # # # # #         "berat_kg": berat,
# # # # # #         "total": total,
# # # # # #         "status": STATUS_PESANAN[0],
# # # # # #     }
# # # # # #     data.append(pesanan)

# # # # # #     if simpan_pesanan(data):
# # # # # #         print(f"Pesanan {pesanan['kode']} berhasil disimpan.")


# # # # # # def ubah_status(data):
# # # # # #     print("\n--- UBAH STATUS PESANAN ---")
# # # # # #     if len(data) == 0:
# # # # # #         print("Belum ada pesanan.")
# # # # # #         return

# # # # # #     tampilkan_daftar_pesanan(data)
# # # # # #     indeks = pilih_nomor_pesanan(data, "Nomor pesanan")
# # # # # #     if indeks is None:
# # # # # #         print("Dibatalkan.")
# # # # # #         return

# # # # # #     pesanan = data[indeks]
# # # # # #     print(f"\nStatus saat ini: {pesanan['status']}")
# # # # # #     for nomor, status in enumerate(STATUS_PESANAN, start=1):
# # # # # #         print(f"{nomor}. {status}")

# # # # # #     pilihan = layanan.input_angka("Pilih status baru (0 = batal): ", 0, len(STATUS_PESANAN))
# # # # # #     if pilihan == 0:
# # # # # #         print("Dibatalkan.")
# # # # # #         return

# # # # # #     pesanan["status"] = STATUS_PESANAN[pilihan - 1]
# # # # # #     if simpan_pesanan(data):
# # # # # #         print(f"Status pesanan {pesanan['kode']} diubah menjadi '{pesanan['status']}'.")


# # # # # # def lihat_detail(data):
# # # # # #     print("\n--- DETAIL PESANAN ---")
# # # # # #     if len(data) == 0:
# # # # # #         print("Belum ada pesanan.")
# # # # # #         return

# # # # # #     tampilkan_daftar_pesanan(data)
# # # # # #     indeks = pilih_nomor_pesanan(data, "Nomor pesanan")
# # # # # #     if indeks is None:
# # # # # #         print("Dibatalkan.")
# # # # # #         return

# # # # # #     tampilkan_detail(data[indeks])


# # # # # # # SUBMENU PESANAN (dipanggil dari main.py)

# # # # # # def tampilkan_menu_pesanan():
# # # # # #     print()
# # # # # #     layanan.cetak_garis()
# # # # # #     print("MANAJEMEN PESANAN LAUNDRY")
# # # # # #     layanan.cetak_garis()
# # # # # #     print("1. Tambah Pesanan")
# # # # # #     print("2. Lihat Daftar Pesanan")
# # # # # #     print("3. Lihat Detail Pesanan")
# # # # # #     print("4. Ubah Status Pesanan")
# # # # # #     print("0. Kembali")
# # # # # #     layanan.cetak_garis()


# # # # # # def menu_pesanan(data_layanan):
# # # # # #     """Submenu pesanan. Dipanggil dari main.py lewat: pesanan.menu_pesanan(data_layanan)"""
# # # # # #     data = muat_pesanan()  # data dibaca dari pelanggan.json

# # # # # #     while True:
# # # # # #         tampilkan_menu_pesanan()
# # # # # #         pilihan = layanan.input_angka("Pilih menu: ", 0, 4)

# # # # # #         if pilihan == 1:
# # # # # #             tambah_pesanan(data, data_layanan)
# # # # # #         elif pilihan == 2:
# # # # # #             tampilkan_daftar_pesanan(data)
# # # # # #         elif pilihan == 3:
# # # # # #             lihat_detail(data)
# # # # # #         elif pilihan == 4:
# # # # # #             ubah_status(data)
# # # # # #         else:  # pilihan == 0
# # # # # #             break


# # # # # # # Jika file ini dijalankan langsung, layanan dibaca dari layanan.json.
# # # # # # if __name__ == "__main__":
# # # # # #     try:
# # # # # #         menu_pesanan(layanan.muat_data())
# # # # # #     except (KeyboardInterrupt, EOFError):
# # # # # #         print("\n\nProgram dihentikan. Data yang sudah disimpan tetap aman.")