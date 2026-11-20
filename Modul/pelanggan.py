import json
import os

NAMA_FILE = "data_pelanggan.json"

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


# ---------- FITUR 1:TAMPILKAN ----------
def tampilkan(data):
    print("\n=== DAFTAR PELANGGAN ===")