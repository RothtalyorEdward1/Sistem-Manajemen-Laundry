from datetime import datetime
from Modul.penyimpanan_riwayat import (
    simpan_data_pesanan,
    simpan_riwayat_pembayaran,
)

DISKON_MEMBER = 0.10      # 10%
DISKON_NON_MEMBER = 0.0   # 0%


def _hitung_ringkasan_layanan(pesanan_dict):
    daftar = pesanan_dict.get("daftar_layanan", [])
    if daftar and isinstance(daftar, list):
        nama_list = [item.get("nama_layanan", "-") for item in daftar]
        ringkasan_nama = ", ".join(nama_list)
        total_berat = sum(float(item.get("berat", 0)) for item in daftar)
        biaya_awal = sum(float(item.get("subtotal", 0)) for item in daftar)
        return ringkasan_nama, total_berat, biaya_awal
    
    return (
        pesanan_dict.get("layanan", "-"),
        float(pesanan_dict.get("berat_kg", 0)),
        float(pesanan_dict.get("total_biaya") or pesanan_dict.get("total", 0)),
    )


def _cek_member(data_plg):
    if not data_plg:
        return None
    for key in ("is_member", "member", "status_member"):
        if key in data_plg:
            val = data_plg[key]
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                return val.strip().lower() in ("ya", "yes", "true", "member", "1")
    return None


def cetak_bukti_transaksi(data_bayar):
    print("\n" + "=" * 54)
    print("              BUKTI TRANSAKSI LAUNDRY")
    print("=" * 54)
    print(f"ID Pembayaran   : {data_bayar['id_pembayaran']}")
    print(f"No. Transaksi   : {data_bayar['no_transaksi']}")
    print(f"Pelanggan       : {data_bayar['nama_pelanggan']} ({data_bayar['id_pelanggan']})")
    print(f"Status Member   : {'Member (Diskon 10%)' if data_bayar['is_member'] else 'Non-Member (0%)'}")
    print(f"Layanan         : {data_bayar['nama_layanan']} ({data_bayar['berat_kg']} kg)")
    print(f"Tanggal Bayar   : {data_bayar['waktu_bayar']}")
    print("-" * 54)
    print(f"Biaya Awal      : Rp{data_bayar['biaya_awal']:,.0f}")
    print(f"Diskon          : -Rp{data_bayar['nominal_diskon']:,.0f}")
    print(f"Total Tagihan   : Rp{data_bayar['total_tagihan']:,.0f}")
    print(f"Nominal Bayar   : Rp{data_bayar['nominal_bayar']:,.0f}")
    print(f"Kembalian       : Rp{data_bayar['kembalian']:,.0f}")
    print("=" * 54)
    print("      Terima kasih telah menggunakan jasa kami!")
    print("=" * 54 + "\n")


def proses_pembayaran(
    daftar_pelanggan, daftar_pesanan, riwayat_pembayaran
):
    print("\n" + "=" * 72)
    print("                      PROSES PEMBAYARAN LAUNDRY")
    print("=" * 72)

    transaksi_lunas = {
        str(b.get("no_transaksi", "")).upper() for b in riwayat_pembayaran
    }

    pesanan_belum_lunas = []
    for p in daftar_pesanan:
        kode_trx = str(p.get("id") or p.get("no_transaksi", "")).upper()
        if kode_trx and kode_trx not in transaksi_lunas and p.get("status_bayar", "belum").lower() != "lunas":
            pesanan_belum_lunas.append(p)

    if not pesanan_belum_lunas:
        print("[INFO] Tidak ada pesanan yang menunggu pembayaran saat ini.")
        return

    map_pelanggan = {
        str(p.get("id") or p.get("id_pelanggan", "")).upper(): p
        for p in daftar_pelanggan
    }

    print("Daftar Pesanan Belum Lunas:")
    print("-" * 82)
    print(
        f"{'No. TRX':<10} | {'Pelanggan':<18} | {'Layanan':<22} | "
        f"{'Berat':<8} | {'Biaya Awal':<13}"
    )
    print("-" * 82)

    for item in pesanan_belum_lunas:
        no_trx = item.get("id") or item.get("no_transaksi", "-")
        id_plg = str(item.get("pelanggan_id") or item.get("id_pelanggan", "-")).upper()
        nama_plg = item.get("nama_pelanggan") or map_pelanggan.get(id_plg, {}).get("nama", id_plg)
        nama_lyn, berat, biaya_awal = _hitung_ringkasan_layanan(item)

        print(
            f"{no_trx:<10} | {nama_plg[:18]:<18} | {nama_lyn[:22]:<22} | "
            f"{berat:<5} kg | Rp{biaya_awal:<10,.0f}"
        )
    print("-" * 82)

    target_trx = input("Masukkan No. Transaksi yang akan dibayar (0 untuk batal): ").strip().upper()
    if target_trx == "0" or not target_trx:
        print("[INFO] Proses pembayaran dibatalkan.")
        return

    pesanan_terpilih = None
    for p in daftar_pesanan:
        kode_trx = str(p.get("id") or p.get("no_transaksi", "")).upper()
        if kode_trx == target_trx:
            pesanan_terpilih = p
            break

    if not pesanan_terpilih:
        print(f"[ERROR] Nomor transaksi '{target_trx}' tidak ditemukan.")
        return

    if target_trx in transaksi_lunas or pesanan_terpilih.get("status_bayar", "").lower() == "lunas":
        print(f"[INFO] Transaksi '{target_trx}' sudah lunas sebelumnya.")
        return

    no_trx_sah = pesanan_terpilih.get("id") or pesanan_terpilih.get("no_transaksi")
    id_plg = str(pesanan_terpilih.get("pelanggan_id") or pesanan_terpilih.get("id_pelanggan", "-")).upper()
    data_plg = map_pelanggan.get(id_plg, {})
    nama_plg = pesanan_terpilih.get("nama_pelanggan") or data_plg.get("nama", "Pelanggan Umum")
    nama_lyn, berat_kg, biaya_awal = _hitung_ringkasan_layanan(pesanan_terpilih)

    status_member = _cek_member(data_plg)
    if status_member is None:
        while True:
            tanya = input("Apakah pelanggan merupakan Member? (y/n): ").strip().lower()
            if tanya in ("y", "n"):
                status_member = (tanya == "y")
                break
            print("[ERROR] Masukkan 'y' untuk Member atau 'n' untuk Non-Member.")

    persen_diskon = DISKON_MEMBER if status_member else DISKON_NON_MEMBER
    nominal_diskon = biaya_awal * persen_diskon
    total_tagihan = biaya_awal - nominal_diskon

    print("\n--- RINCIAN TAGIHAN ---")
    print(f"No. Transaksi : {no_trx_sah}")
    print(f"Pelanggan     : {nama_plg} ({id_plg})")
    print(f"Layanan       : {nama_lyn} ({berat_kg} kg)")
    print(f"Biaya Awal    : Rp{biaya_awal:,.0f}")
    print(f"Diskon ({int(persen_diskon * 100)}%)  : -Rp{nominal_diskon:,.0f}")
    print(f"Total Tagihan : Rp{total_tagihan:,.0f}")
    print("-" * 28)

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
    catatan_pembayaran = {
        "id_pembayaran": id_pembayaran,
        "no_transaksi": no_trx_sah,
        "id_pelanggan": id_plg,
        "nama_pelanggan": nama_plg,
        "nama_layanan": nama_lyn,
        "berat_kg": berat_kg,
        "is_member": status_member,
        "biaya_awal": biaya_awal,
        "nominal_diskon": nominal_diskon,
        "total_tagihan": total_tagihan,
        "nominal_bayar": nominal_bayar,
        "kembalian": kembalian,
        "waktu_bayar": waktu_bayar,
    }

    riwayat_pembayaran.append(catatan_pembayaran)
    pesanan_terpilih["status_bayar"] = "lunas"

    simpan_riwayat_pembayaran(riwayat_pembayaran)
    simpan_data_pesanan(daftar_pesanan)

    print("\n[SUKSES] Pembayaran berhasil dicatat dan disimpan!")
    cetak_bukti_transaksi(catatan_pembayaran)


def lihat_bukti_transaksi(riwayat_pembayaran):
    print("\n--- CETAK ULANG BUKTI TRANSAKSI ---")
    if not riwayat_pembayaran:
        print("[INFO] Belum ada riwayat pembayaran yang tersimpan.")
        return

    target_trx = input("Masukkan No. Transaksi (contoh: ORD001): ").strip().upper()
    for bayar in riwayat_pembayaran:
        if str(bayar.get("no_transaksi", "")).upper() == target_trx:
            cetak_bukti_transaksi(bayar)
            return

    print(f"[ERROR] Bukti pembayaran untuk transaksi '{target_trx}' tidak ditemukan.")


def menu_pembayaran(
    daftar_pelanggan, daftar_pesanan, riwayat_pembayaran
):
    while True:
        print("\n=== MENU PEMBAYARAN LAUNDRY ===")
        print("1. Catat Pembayaran Pelanggan")
        print("2. Cetak Ulang Bukti Transaksi")
        print("0. Kembali ke Menu Utama")

        pilihan = input("Pilih menu (0-2): ").strip()

        if pilihan == "1":
            proses_pembayaran(
                daftar_pelanggan, daftar_pesanan, riwayat_pembayaran
            )
        elif pilihan == "2":
            lihat_bukti_transaksi(riwayat_pembayaran)
        elif pilihan == "0":
            break
        else:
            print("[ERROR] Pilihan tidak valid! Silakan masukkan angka 0 sampai 2.")
