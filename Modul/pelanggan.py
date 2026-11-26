
import json
import os

# ---------- PENGATURAN FILE ----------
FOLDER_MODUL = os.path.dirname(os.path.abspath(__file__))
NAMA_FILE = os.path.join(FOLDER_MODUL, "data_pelanggan.json")


# ---------- SIMPAN DAN BACA FILE ----------
def baca_data():
    if not os.path.exists(NAMA_FILE):
        return []
    try:
        file = open(NAMA_FILE, "r")
        data = json.load(file)
        file.close()
        return data
    except:
        print("File data bermasalah, mulai dari data kosong.")
        return []


def simpan_data(data):
    try:
        file = open(NAMA_FILE, "w")
        json.dump(data, file, indent=4)
        file.close()
    except:
        print("Data gagal disimpan.")


# ---------- CEK INPUT ----------
def minta_nama(teks, boleh_kosong=False):
    huruf_boleh = "abcdefghijklmnopqrstuvwxyz "

    while True:
        nama = input(teks).strip()

        if nama == "" and boleh_kosong:
            return ""

        if nama == "":
            print("Nama tidak boleh kosong!")
        else:
            salah = False
            for huruf in nama.lower():
                if huruf not in huruf_boleh:
                    salah = True
                    break

            if salah:
                print("Nama hanya boleh huruf!")
            else:
                return nama.title()


def minta_telepon(teks, boleh_kosong=False):
    while True:
        telepon = input(teks).strip()
        if telepon == "" and boleh_kosong:
            return ""
        if telepon.isdigit() == False:
            print("Telepon harus angka!")
        elif len(telepon) < 10 or len(telepon) > 13:
            print("Telepon harus 10 sampai 13 angka!")
        else:
            return telepon


def minta_alamat(teks, boleh_kosong=False):
    while True:
        alamat = input(teks).strip()
        if alamat == "" and boleh_kosong == False:
            print("Alamat tidak boleh kosong!")
        else:
            return alamat


# ---------- FUNGSI BANTU ----------
def buat_id(data):
    # ID dibuat otomatis: P001, P002, dst. Tidak akan sama.
    id_terpakai = set()
    for p in data:
        id_terpakai.add(p["id"])

    nomor = 1
    while True:
        # Tambahkan angka 0 di depan supaya ID rapi
        if nomor < 10:
            id_baru = "P00" + str(nomor)
        elif nomor < 100:
            id_baru = "P0" + str(nomor)
        else:
            id_baru = "P" + str(nomor)

        # Kalau ID belum dipakai, langsung gunakan
        if id_baru not in id_terpakai:
            return id_baru

        nomor = nomor + 1


def cari_pelanggan(data, id_cari):
    for p in data:
        if p["id"] == id_cari:
            return p
    return None


# ---------- FITUR 1: TAMPILKAN ----------
def tampilkan(data):
    print("\n=== DAFTAR PELANGGAN ===")
    if len(data) == 0:
        print("Belum ada data pelanggan.")
        return
    for p in data:
        print(p["id"], "|", p["nama"], "|", p["telepon"], "|", p["alamat"])
    print("Total:", len(data), "pelanggan")


# ---------- FITUR 2: TAMBAH ----------
def tambah(data):
    print("\n=== TAMBAH PELANGGAN ===")
    nama = minta_nama("Nama     : ")
    telepon = minta_telepon("Telepon : ")
    alamat = minta_alamat("Alamat  : ")

    pelanggan = {
        "id": buat_id(data),
        "nama": nama,
        "telepon": telepon,
        "alamat": alamat
    }
    data.append(pelanggan)
    simpan_data(data)
    print("Berhasil! ID pelanggan:", pelanggan["id"])


# ---------- FITUR 3: UBAH ----------
def ubah(data):
    print("\n=== UBAH PELANGGAN ===")
    if len(data) == 0:
        print("Belum ada data pelanggan.")
        return

    tampilkan(data)
    id_cari = input("\nMasukkan ID yang mau diubah: ").strip().upper()
    pelanggan = cari_pelanggan(data, id_cari)

    if pelanggan == None:
        print("ID tidak ditemukan!")
        return

    print("Kosongkan jika tidak ingin diubah.")
    nama = minta_nama("Nama baru    : ", True)
    telepon = minta_telepon("Telepon baru : ", True)
    alamat = minta_alamat("Alamat baru  : ", True)

    if nama != "":
        pelanggan["nama"] = nama
    if telepon != "":
        pelanggan["telepon"] = telepon
    if alamat != "":
        pelanggan["alamat"] = alamat

    simpan_data(data)
    print("Data berhasil diubah.")


# ---------- FITUR 4: HAPUS ----------
def hapus(data):
    print("\n=== HAPUS PELANGGAN ===")
    if len(data) == 0:
        print("Belum ada data pelanggan.")
        return

    tampilkan(data)
    id_cari = input("\nMasukkan ID yang mau dihapus: ").strip().upper()
    pelanggan = cari_pelanggan(data, id_cari)

    if pelanggan == None:
        print("ID tidak ditemukan!")
        return

    yakin = input("Yakin hapus " + pelanggan["nama"] + "? (y/n): ").strip().lower()
    if yakin == "y":
        data.remove(pelanggan)
        simpan_data(data)
        print("Data berhasil dihapus.")
    else:
        print("Batal menghapus.")


# ---------- MENU ----------
def menu_pelanggan():
    data = baca_data()
    pilihan_menu = ("0", "1", "2", "3", "4")

    while True:
        print("\n=== MANAJEMEN PELANGGAN ===")
        print("1. Tambah pelanggan")
        print("2. Tampilkan pelanggan")
        print("3. Ubah pelanggan")
        print("4. Hapus pelanggan")
        print("0. Kembali")
        pilihan = input("Pilih: ").strip()

        if pilihan not in pilihan_menu:
            print("Pilihan salah!")
        elif pilihan == "1":
            tambah(data)
        elif pilihan == "2":
            tampilkan(data)
        elif pilihan == "3":
            ubah(data)
        elif pilihan == "4":
            hapus(data)
        else:
            break


if __name__ == "__main__":
    menu_pelanggan()
