

import json 
import os 
import layanan 


FOLDER_PROGRAM = os.path.dirname(os.path.abspath(__file__)) 
FILE_PESANAN = os.path.join(FOLDER_PROGRAM, "pesanan.json") 
FILE_PELANGGAN = os.path.join(FOLDER_PROGRAM, "data_pelanggan.json") 

STATUS_PESANAN = ("Diterima", "Diproses", "Selesai", "Diambil") 



def baca_pesanan():
    if not os.path.exists(FILE_PESANAN): 
        return []

    try:
        with open(FILE_PESANAN, "r") as file:
            data = json.load(file) 

        if isinstance(data, list): 
            return data
        else:
            print("Format data pesanan tidak sesuai.")
            return []

    except (json.JSONDecodeError, OSError) as error:
        print("Gagal membaca data pesanan:", error)
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

        if isinstance(data, list):
            return data
        else:
            return []

    except (json.JSONDecodeError, OSError) as error:
        print("Gagal membaca data pelanggan:", error)
        return []



def input_teks(pesan):
    while True:
        teks = input(pesan).strip()

        if teks != "":
            return teks
        else:
            print("Input tidak boleh kosong!")


def input_angka(pesan, minimal=0):
    while True:
        try:
            angka = int(input(pesan))

            if angka >= minimal:
                return angka
            else:
                print("Angka minimal adalah", minimal)

        except ValueError:
            print("Masukkan angka bulat yang benar!")


def input_berat(pesan):
    while True:
        try:
            berat = float(input(pesan).replace(",", ".")) 

            if berat > 0:
                return berat
            else:
                print("Berat harus lebih dari 0 kg!")

        except ValueError:
            print("Masukkan berat dalam angka!")


def format_rupiah(angka):
    return "Rp " + f"{angka:,.0f}".replace(",", ".") 



def buat_id_pesanan(data):
    id_terpakai = set() 

    for pesanan in data:
        id_terpakai.add(pesanan["id"]) 

    nomor = 1

    while True:
        kode = f"ORD{nomor:03d}"

        if kode not in id_terpakai:
            return kode
        else:
            nomor += 1



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



def tampilkan_daftar_pesanan(data):
    print("\n" + "=" * 60)
    print("DAFTAR PESANAN LAUNDRY")
    print("=" * 60)

    if len(data) == 0:
        print("Belum ada pesanan.")
        return
    else:
        print(f"{'No':<5}{'Kode':<12}{'Pelanggan':<25}{'Status':<15}")
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



def tambah_pesanan(data):
    print("\n" + "=" * 40)
    print("TAMBAH PESANAN LAUNDRY")
    print("=" * 40)

    pelanggan_data = baca_pelanggan()

    if len(pelanggan_data) == 0:
        print("Belum ada pelanggan. Tambahkan pelanggan terlebihdahulu.")
        return
    else:
        kode = input_teks("Masukkan kode pelanggan: ").upper()
        pelanggan = cari_pelanggan(pelanggan_data, kode)

    if pelanggan is None:
        print("Kode pelanggan tidak ditemukan!")
        return
    else:
        print("\nData Pelanggan")
        print("Kode    :", pelanggan["id"])
        print("Nama    :", pelanggan["nama"])
        print("Telepon :", pelanggan["telepon"])
        print("Alamat  :", pelanggan["alamat"])

    daftar_layanan = layanan.muat_data() 

    if len(daftar_layanan) == 0:
        print("Belum tersedia layanan laundry.")
        return
    else:
        daftar_barang = []

    
    while True:
        layanan.tampilkan_daftar(daftar_layanan)

        print("\nPilih layanan yang ingin ditambahkan.")

        nomor = input_angka("Nomor layanan: ", 0)

        if nomor == 0:
            if len(daftar_barang) > 0:
                break
            else:
                print("Minimal pilih satu layanan!")
                continue

        elif nomor <= len(daftar_layanan):
            jenis = daftar_layanan[nomor - 1] 
            berat = input_berat("Masukkan berat pakaian (kg): ")

            subtotal = berat * jenis["harga"]

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
            break

        else:
            print("Nomor layanan tidak tersedia!")

    pesanan_baru = {
        "id": buat_id_pesanan(data),
        "pelanggan_id": pelanggan["id"],
        "nama_pelanggan": pelanggan["nama"],
        "telepon": pelanggan["telepon"],
        "alamat": pelanggan["alamat"],
        "daftar_layanan": daftar_barang,
        "status": STATUS_PESANAN[0]
    }

    data.append(pesanan_baru)

    if simpan_pesanan(data):
        print("\nPesanan berhasil disimpan!")
        tampilkan_struk(pesanan_baru)
    else:
        data.remove(pesanan_baru)



def tampilkan_struk(pesanan):
    print("\n" + "=" * 50)
    print("              STRUK LAUNDRY")
    print("=" * 50)

    print("Kode Pesanan  :", pesanan["id"])
    print("Kode Pelanggan:", pesanan["pelanggan_id"])
    print("Nama Pelanggan:", pesanan["nama_pelanggan"])

    print("-" * 50)
    print("RINCIAN LAYANAN")

    for nomor, barang in enumerate(pesanan["daftar_layanan"], start=1):
        print(f"\n{nomor}. {barang['nama_layanan']}")
        print("   Berat     :", barang["berat"], "kg")
        print("   Harga/kg :", format_rupiah(barang["harga_per_kg"]))
        print("   Subtotal :", format_rupiah(barang["subtotal"]))

    print("-" * 50)
    print("Status Pesanan:", pesanan["status"])
    print("=" * 50)
    print("       TERIMA KASIH TELAH MENGGUNAKAN")
    print("             JASA LAUNDRY KAMI")
    print("=" * 50)



def detail_pesanan(data):
    print("\n--- DETAIL PESANAN ---")

    if len(data) == 0:
        print("Belum ada pesanan.")
        return
    else:
        kode = input_teks("Masukkan kode pesanan: ").upper()  
        pesanan = cari_pesanan(data, kode)

    if pesanan is None:
        print("Pesanan tidak ditemukan!")
    else:
        tampilkan_struk(pesanan)




def ubah_status(data):
    print("\n--- UBAH STATUS PESANAN ---")

    if len(data) == 0:
        print("Belum ada pesanan.")
        return

    tampilkan_daftar_pesanan(data)

    kode = input_teks("Masukkan kode pesanan: ").upper()
    pesanan = cari_pesanan(data, kode)

    if pesanan is None:
        print("Pesanan tidak ditemukan!")
        return

    print("\nKode Pesanan:", pesanan["id"])
    print("Pelanggan   :", pesanan["nama_pelanggan"])
    print("Status Lama :", pesanan["status"])

    nomor_status = STATUS_PESANAN.index(pesanan["status"])

    print("\nPilihan Status")

    for nomor, status in enumerate(STATUS_PESANAN, start=1):
        print(f"{nomor}. {status}")

    pilihan = input_angka("Pilih status baru: ", 1)

    if pilihan > len(STATUS_PESANAN):
        print("Pilihan status tidak tersedia!")
        return

    if pilihan <= nomor_status:
        print("Status tidak bisa dimundurkan ke status sebelumnya!")
        return

    status_lama = pesanan["status"]
    status_baru = STATUS_PESANAN[pilihan - 1]

    pesanan["status"] = status_baru

    if simpan_pesanan(data):
        print("\nStatus pesanan berhasil diubah!")
        print("Status lama:", status_lama)
        print("Status baru:", status_baru)
    else:
        pesanan["status"] = status_lama
        print("Gagal mengubah status pesanan.")



def hapus_pesanan(data):
    print("\n--- HAPUS PESANAN ---")

    if len(data) == 0:
        print("Belum ada pesanan.")
        return

    tampilkan_daftar_pesanan(data)

    kode = input_teks("Masukkan kode pesanan yang dihapus: ").upper() 
    pesanan = cari_pesanan(data, kode)

    if pesanan is None:
        print("Pesanan tidak ditemukan!")
        return

    print("\nKode Pesanan:", pesanan["id"])
    print("Pelanggan   :", pesanan["nama_pelanggan"])
    print("Status      :", pesanan["status"])

    yakin = input("\nYakin ingin menghapus pesanan? (y/t): ").strip().lower() 

    if yakin == "y" or yakin == "ya":
        indeks = data.index(pesanan)
        data.pop(indeks)

        if simpan_pesanan(data):
            print("Pesanan berhasil dihapus.")
        else:
            data.insert(indeks, pesanan)
            print("Gagal menghapus pesanan.")

    elif yakin == "t" or yakin == "tidak" or yakin == "n":
        print("Penghapusan dibatalkan.")

    else:
        print("Pilihan tidak valid!")




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



def main():
    data = baca_pesanan()

    while True:
        tampilkan_menu()
        pilihan = input("Pilih menu: ").strip()

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