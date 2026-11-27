import json
import os


# PENGATURAN DAN DATA AWAL

FOLDER_PROGRAM = os.path.dirname(__file__)
FILE_LAYANAN = os.path.join(FOLDER_PROGRAM, "layanan.json")
LEBAR_GARIS = 52

# tuple berisi layanan awal: (nama, harga per kg, estimasi jam)
LAYANAN_AWAL = (
    ("Cuci Strika", 8000, 48),
    ("Setrika Saja", 5000, 24),
    ("Cuci Saja", 6000, 24),
    ("Express", 25000, 6),
)

# set berisi kunci yang wajib ada di setiap layanan
KUNCI_WAJIB = {"nama", "harga", "estimasi_jam"}

# set berisi jawaban ya / tidak
JAWABAN_YA = {"y", "ya"}
JAWABAN_TIDAK = {"t", "tidak", "n"}


# VALIDASI INPUT

def input_teks(pesan, boleh_kosong=False):
    while True:
        teks = input(pesan).strip()
        if teks != "" or boleh_kosong:
            return teks
        print("Input tidak boleh kosong, coba lagi.")


def input_angka(pesan, minimal=0, maksimal=None, boleh_kosong=False):
    while True:
        teks = input(pesan).strip()

        if teks == "" and boleh_kosong:
            return None

        try:
            angka = int(teks)
        except ValueError:
            print("Input harus berupa angka bulat (tanpa titik/koma), coba lagi.")
            continue

        if angka < minimal:
            print(f"Angka tidak boleh kurang dari {minimal}.")
        elif maksimal is not None and angka > maksimal:
            print(f"Angka tidak boleh lebih dari {maksimal}.")
        else:
            return angka


def konfirmasi(pesan):
    while True:
        jawaban = input(pesan + " (y/t): ").replace(" ", "").lower()
        if jawaban in JAWABAN_YA:
            return True
        if jawaban in JAWABAN_TIDAK:
            return False
        print("Jawab dengan y (ya) atau t (tidak).")


# PENYIMPANAN DATA (FILE JSON)

def buat_data_awal():
    data = []
    for nama, harga, estimasi in LAYANAN_AWAL:
        layanan = {"nama": nama, "harga": harga, "estimasi_jam": estimasi}
        data.append(layanan)
    return data


def simpan_data(data):
    try:
        with open(FILE_LAYANAN, "w") as file:
            json.dump(data, file, indent=4)
        return True
    except OSError as error:
        print(f"Gagal menyimpan data: {error}")
        return False


def data_valid(data):
    try:
        for layanan in data:
            if not KUNCI_WAJIB <= set(layanan):
                return False
        return True
    except TypeError:
        return False

def muat_data():
    try:
        with open(FILE_LAYANAN, "r") as file:
            data = json.load(file)
        if not data_valid(data):
            raise ValueError("Isi file tidak sesuai format")
        return data

    except FileNotFoundError:
        data = buat_data_awal()
        simpan_data(data)
        return data

    except ValueError:  
        print("File data rusak. File lama disimpan sebagai layanan.json.rusak.")
        try:
            os.replace(FILE_LAYANAN, FILE_LAYANAN + ".rusak")
        except OSError:
            pass
        data = buat_data_awal()
        simpan_data(data)
        return data

    except OSError as error:
        print(f"Gagal membaca file data: {error}")
        return buat_data_awal()


# TAMPILAN

def cetak_garis():
    print("=" * LEBAR_GARIS)


def format_rupiah(angka):
    """Contoh: 8000 -> 'Rp 8.000'"""
    return "Rp " + f"{angka:,}".replace(",", ".")


# Minta nomor layanan. Mengembalikan indeks list, atau None kalau batal.
def pilih_nomor_layanan(data, pesan):
    nomor = input_angka(pesan + " (0 = batal): ", 0, len(data))
    if nomor == 0:
        return None
    return nomor - 1

# tampilan layar dalam bentuk tabel
def tampilkan_daftar(data):
    print()
    cetak_garis()
    print("DAFTAR LAYANAN LAUNDRY")
    cetak_garis()

    if len(data) == 0:
        print("Belum ada layanan.")
        cetak_garis()
        return

    print("No  Layanan             Harga/kg      Estimasi")
    print("-" * 48)

    nomor = 1
    for jenis in data:
        harga = format_rupiah(jenis["harga"])
        jam = str(jenis["estimasi_jam"]) + " jam"
        print(f"{nomor:<4}{jenis['nama']:<20}{harga:<14}{jam}")
        nomor = nomor + 1

    print("-" * 48)


# FITUR: TAMBAH, UBAH, HAPUS LAYANAN

def tambah_layanan(data):
    print("\n--- TAMBAH LAYANAN ---")
    nama = input_teks("Nama layanan (contoh: Cuci Saja)  : ")

    # set berisi nama yang sudah dipakai (huruf kecil semua)
    nama_terpakai = {item["nama"].lower() for item in data}
    if nama.lower() in nama_terpakai:
        print("Layanan dengan nama itu sudah ada.")
        return

    harga = input_angka("Harga per kg (Rp)      : ", minimal=1)
    estimasi = input_angka("Estimasi selesai (jam) : ", minimal=1)

    data.append({"nama": nama, "harga": harga, "estimasi_jam": estimasi})

    if simpan_data(data):
        print(f"Layanan '{nama}' berhasil ditambahkan.")


def ubah_layanan(data):
    print("\n--- UBAH LAYANAN ---")
    if len(data) == 0:
        print("Belum ada layanan yang bisa diubah.")
        return

    tampilkan_daftar(data)
    indeks = pilih_nomor_layanan(data, "Nomor layanan yang diubah")
    if indeks is None:
        print("Dibatalkan.")
        return

    layanan = data[indeks]
    print("Tekan Enter jika tidak ingin mengubah bagian tersebut.")

    # nama 
    nama_baru = input_teks(f"Nama baru [{layanan['nama']}]: ", boleh_kosong=True)
    if nama_baru != "":
        nama_lain = {
            item["nama"].lower() for i, item in enumerate(data) if i != indeks
        }
        if nama_baru.lower() in nama_lain:
            print("Layanan dengan nama itu sudah ada. Perubahan dibatalkan.")
            return
        layanan["nama"] = nama_baru

    #  harga 
    harga_baru = input_angka(
        f"Harga baru [{layanan['harga']}]: ", minimal=1, boleh_kosong=True
    )
    if harga_baru is not None:
        layanan["harga"] = harga_baru

    #  estimasi 
    estimasi_baru = input_angka(
        f"Estimasi baru (jam) [{layanan['estimasi_jam']}]: ",
        minimal=1,
        boleh_kosong=True,
    )
    if estimasi_baru is not None:
        layanan["estimasi_jam"] = estimasi_baru

    if simpan_data(data):
        print("Layanan berhasil diubah.")


def hapus_layanan(data):
    print("\n--- HAPUS LAYANAN ---")
    if len(data) == 0:
        print("Belum ada layanan yang bisa dihapus.")
        return

    tampilkan_daftar(data)
    indeks = pilih_nomor_layanan(data, "Nomor layanan yang dihapus")
    if indeks is None:
        print("Dibatalkan.")
        return

    nama = data[indeks]["nama"]
    if konfirmasi(f"Yakin hapus layanan '{nama}'?"):
        data.pop(indeks)
        if simpan_data(data):
            print(f"Layanan '{nama}' berhasil dihapus.")
    else:
        print("Penghapusan dibatalkan.")


# MENU

def tampilkan_menu():
    print()
    cetak_garis()
    print("MANAJEMEN LAYANAN LAUNDRY")
    cetak_garis()
    print("1. Lihat Daftar Layanan")
    print("2. Tambah Layanan")
    print("3. Ubah Layanan")
    print("4. Hapus Layanan")
    print("0. Keluar")
    cetak_garis()


# PROGRAM UTAMA

def main():
    data = muat_data()  # data dibaca dari file ketika program mulai

    while True:
        tampilkan_menu()
        pilihan = input_angka("Pilih menu: ", 0, 4)

        if pilihan == 1:
            tampilkan_daftar(data)
        elif pilihan == 2:
            tambah_layanan(data)
        elif pilihan == 3:
            ubah_layanan(data)
        elif pilihan == 4:
            hapus_layanan(data)
        else:  # pilihan == 0
            break

    print("\nTerima kasih, sampai jumpa!")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgram dihentikan. Data yang sudah disimpan tetap aman.")