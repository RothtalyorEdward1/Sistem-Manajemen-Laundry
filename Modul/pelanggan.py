
# ini def berat 
def tambah_pesanan():
    try:
        berat = float(input("Berat pakaian (kg): "))
        harga = float(input("harga:"))
        if berat <= 0:
            print("Berat harus lebih dari 0 kg!")
            return

    except ValueError:
        print("Berat harus berupa angka!")
        return

    # Menghitung total biaya
    total = berat * harga

    print("\n========== RINCIAN PESANAN ==========")
    print("Total biaya    : Rp", total)
print(tambah_pesanan())