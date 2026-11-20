from datetime import datetime
from penyimpana_riwayat import (
    simpan_data_pesanan,
    simpan_riwayat_pembayaran,
)

# Referensi tarif layanan standar (digunakan sebagai fallback jika layanan tidak ditemukan)
TARIF_LAYANAN_DEFAULT = {
    "Cuci Kering": 5000,
    "Cuci Setrika": 7000,
    "Setrika Saja": 4000,
    "Express": 25000,
}

DISKON_MEMBER = 0.10      # 10%
DISKON_NON_MEMBER = 0.0   # 0%


def _cek_status_member(pelanggan_dict):
    """Mengecek apakah pelanggan terdaftar sebagai member (mendukung boolean atau string)."""
    if not pelanggan_dict:
        return False
    status = pelanggan_dict.get("is_member", pelanggan_dict.get("status_member", False))
    if isinstance(status, bool):
        return status
    if isinstance(status, str):
        return status.strip().lower() in ("ya", "yes", "true", "member", "1")
    return False


def _cari_layanan(id_layanan, daftar_layanan):
    """Mencari nama dan harga per kg layanan dari daftar_layanan atau tarif default."""
    for lyn in daftar_layanan:
        if lyn.get("id_layanan", "").upper() == id_layanan.upper():
            return lyn.get("nama_layanan", id_layanan), lyn.get("harga_per_kg", 0)
    # Fallback jika id_layanan berisi nama layanan langsung
    if id_layanan in TARIF_LAYANAN_DEFAULT:
        return id_layanan, TARIF_LAYANAN_DEFAULT[id_layanan]
    return id_layanan, 0


def cetak_bukti_transaksi(data_bayar):
    """Menampilkan struk / bukti transaksi pembayaran secara rapi di terminal."""
    print("\n" + "=" * 52)
    print("             BUKTI TRANSAKSI LAUNDRY")
    print("=" * 52)
    print(f"ID Pembayaran   : {data_bayar['id_pembayaran']}")
    print(f"No. Transaksi   : {data_bayar['no_transaksi']}")
    print(f"Pelanggan       : {data_bayar['nama_pelanggan']} ({data_bayar['id_pelanggan']})")
    print(f"Status Member   : {'Member (Diskon 10%)' if data_bayar['is_member'] else 'Non-Member (0%)'}")
    print(f"Layanan         : {data_bayar['nama_layanan']} ({data_bayar['berat_kg']} kg)")
    print(f"Waktu Bayar     : {data_bayar['waktu_bayar']}")
    print("-" * 52)
    print(f"Biaya Awal      : Rp{data_bayar['biaya_awal']:,.0f}")
    print(f"Diskon          : -Rp{data_bayar['nominal_diskon']:,.0f}")
    print(f"Total Tagihan   : Rp{data_bayar['total_tagihan']:,.0f}")
    print(f"Nominal Bayar   : Rp{data_bayar['nominal_bayar']:,.0f}")
    print(f"Kembalian       : Rp{data_bayar['kembalian']:,.0f}")
    print("=" * 52)
    print("     Terima kasih telah menggunakan jasa kami!")
    print("=" * 52 + "\n")


def proses_pembayaran(
    daftar_pelanggan, daftar_layanan, daftar_pesanan, riwayat_pembayaran
):
    """Mencatat pembayaran pelanggan, menghitung diskon member, tagihan, & kembalian."""
    print("\n" + "=" * 65)
    print("                  PROSES PEMBAYARAN LAUNDRY")
    print("=" * 65)

    # Set nomor transaksi yang sudah lunas dari riwayat_pembayaran
    transaksi_lunas = {
        b.get("no_transaksi", "").upper() for b in riwayat_pembayaran
    }

    # Filter pesanan yang belum dibayar
    pesanan_belum_lunas = [
        p for p in daftar_pesanan
        if p.get("no_transaksi", "").upper() not in transaksi_lunas
        and p.get("status_bayar", "belum").lower() != "lunas"
    ]

    if not pesanan_belum_lunas:
        print("[INFO] Tidak ada pesanan yang menunggu pembayaran saat ini.")
        return

    map_pelanggan = {
        p.get("id_pelanggan", "").upper(): p for p in daftar_pelanggan
    }

    print("Daftar Pesanan Belum Lunas:")
    print("-" * 78)
    print(
        f"{'No. TRX':<10} | {'Pelanggan':<18} | {'Layanan':<15} | "
        f"{'Berat':<7} | {'Biaya Awal':<13}"
    )
    print("-" * 78)
    for item in pesanan_belum_lunas:
        no_trx = item.get("no_transaksi", "-")
        id_plg = item.get("id_pelanggan", "-").upper()
        nama_plg = map_pelanggan.get(id_plg, {}).get("nama", id_plg)
        nama_lyn, harga_kg = _cari_layanan(item.get("id_layanan", ""), daftar_layanan)
        berat = item.get("berat_kg", 0)
        biaya_awal = item.get("total_biaya", berat * harga_kg)

        print(
            f"{no_trx:<10} | {nama_plg[:18]:<18} | {nama_lyn[:15]:<15} | "
            f"{berat:<4} kg | Rp{biaya_awal:<10,.0f}"
        )
    print("-" * 78)

    target_trx = input("Masukkan No. Transaksi yang akan dibayar (0 untuk batal): ").strip().upper()
    if target_trx == "0" or not target_trx:
        print("[INFO] Proses pembayaran dibatalkan.")
        return

    # Cari objek pesanan
    pesanan_terpilih = None
    for p in daftar_pesanan:
        if p.get("no_transaksi", "").upper() == target_trx:
            pesanan_terpilih = p
            break

    if not pesanan_terpilih:
        print(f"[ERROR] Nomor transaksi '{target_trx}' tidak ditemukan.")
        return

    if target_trx in transaksi_lunas or pesanan_terpilih.get("status_bayar", "").lower() == "lunas":
        print(f"[INFO] Transaksi '{target_trx}' sudah lunas sebelumnya.")
        return

    # Ambil detail pelanggan, layanan, dan hitung biaya awal
    id_plg = pesanan_terpilih.get("id_pelanggan", "").upper()
    data_plg = map_pelanggan.get(id_plg, {})
    nama_plg = data_plg.get("nama", "Pelanggan Umum")
    nama_lyn, harga_kg = _cari_layanan(pesanan_terpilih.get("id_layanan", ""), daftar_layanan)
    berat_kg = pesanan_terpilih.get("berat_kg", 0)

    biaya_awal = pesanan_terpilih.get("total_biaya", 0)
    if biaya_awal <= 0 and harga_kg > 0:
        biaya_awal = berat_kg * harga_kg

    # Cek status member (otomatis dari data pelanggan, atau konfirmasi jika belum tercatat)
    if "is_member" in data_plg or "status_member" in data_plg:
        is_member = _cek_status_member(data_plg)
    else:
        while True:
            tanya_member = input("Apakah pelanggan merupakan Member? (y/n): ").strip().lower()
            if tanya_member in ("y", "n"):
                is_member = (tanya_member == "y")
                break
            print("[ERROR] Masukkan 'y' untuk Member atau 'n' untuk Non-Member.")

    persen_diskon = DISKON_MEMBER if is_member else DISKON_NON_MEMBER
    nominal_diskon = biaya_awal * persen_diskon
    total_tagihan = biaya_awal - nominal_diskon

    print("\n--- RINCIAN TAGIHAN ---")
    print(f"Pelanggan     : {nama_plg} ({id_plg})")
    print(f"Layanan       : {nama_lyn} ({berat_kg} kg)")
    print(f"Biaya Awal    : Rp{biaya_awal:,.0f}")
    print(f"Diskon ({int(persen_diskon * 100)}%)  : -Rp{nominal_diskon:,.0f}")
    print(f"Total Tagihan : Rp{total_tagihan:,.0f}")
    print("-" * 25)

    # Validasi nominal pembayaran (tidak boleh negatif & harus mencukupi total tagihan)
    while True:
        try:
            nominal_bayar = float(input("Masukkan nominal uang pembayaran (Rp): "))
            if nominal_bayar < 0:
                print("[ERROR] Pembayaran tidak boleh bernilai negatif.")
            elif nominal_bayar < total_tagihan:
                kurang = total_tagihan - nominal_bayar
                print(f"[ERROR] Uang pembayaran kurang Rp{kurang:,.0f}. Harus mencukupi total tagihan!")
            else:
                break
        except ValueError:
            print("[ERROR] Input tidak valid! Masukkan angka nominal uang yang benar.")

    kembalian = nominal_bayar - total_tagihan
    id_pembayaran = f"PAY{len(riwayat_pembayaran) + 1:03d}"
    waktu_bayar = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Struktur dictionary disinkronkan dengan penyimpanan_riwayat.py (memakai key 'total_tagihan')
    catatan_pembayaran = {
        "id_pembayaran": id_pembayaran,
        "no_transaksi": pesanan_terpilih["no_transaksi"],
        "id_pelanggan": pesanan_terpilih["id_pelanggan"],
        "nama_pelanggan": nama_plg,
        "nama_layanan": nama_lyn,
        "berat_kg": berat_kg,
        "is_member": is_member,
        "biaya_awal": biaya_awal,
        "nominal_diskon": nominal_diskon,
        "total_tagihan": total_tagihan,
        "nominal_bayar": nominal_bayar,
        "kembalian": kembalian,
        "waktu_bayar": waktu_bayar,
    }

    # Update list di memori dan simpan langsung ke file JSON via modul teman Anda
    riwayat_pembayaran.append(catatan_pembayaran)
    pesanan_terpilih["status_bayar"] = "lunas"
    pesanan_terpilih["total_biaya"] = total_tagihan

    simpan_riwayat_pembayaran(riwayat_pembayaran)
    simpan_data_pesanan(daftar_pesanan)

    print("\n[SUKSES] Pembayaran berhasil dicatat dan disimpan!")
    cetak_bukti_transaksi(catatan_pembayaran)


def lihat_bukti_transaksi(riwayat_pembayaran):
    """Menampilkan ulang bukti transaksi yang sudah dibayar."""
    print("\n--- CETAK ULANG BUKTI TRANSAKSI ---")
    if not riwayat_pembayaran:
        print("[INFO] Belum ada riwayat pembayaran yang tersimpan.")
        return

    target_trx = input("Masukkan No. Transaksi (contoh: TRX001): ").strip().upper()
    for bayar in riwayat_pembayaran:
        if bayar.get("no_transaksi", "").upper() == target_trx:
            cetak_bukti_transaksi(bayar)
            return

    print(f"[ERROR] Bukti pembayaran untuk transaksi '{target_trx}' tidak ditemukan.")


def menu_pembayaran(
    daftar_pelanggan, daftar_layanan, daftar_pesanan, riwayat_pembayaran
):
    """Submenu interaktif Fitur 4: Pembayaran (untuk dipanggil dari main.py)."""
    while True:
        print("\n=== MENU PEMBAYARAN LAUNDRY ===")
        print("1. Catat Pembayaran Pelanggan")
        print("2. Cetak Ulang Bukti Transaksi")
        print("0. Kembali ke Menu Utama")

        pilihan = input("Pilih menu (0-2): ").strip()

        if pilihan == "1":
            proses_pembayaran(
                daftar_pelanggan, daftar_layanan, daftar_pesanan, riwayat_pembayaran
            )
        elif pilihan == "2":
            lihat_bukti_transaksi(riwayat_pembayaran)
        elif pilihan == "0":
            break
        else:
            print("[ERROR] Pilihan tidak valid! Silakan masukkan angka 0 sampai 2.")