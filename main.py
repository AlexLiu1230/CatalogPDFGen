import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from catalog.csv_reader import read_csv
from catalog.pdf_generator import generate_pdf

# 確定程式運行的目錄
if getattr(sys, 'frozen', False):  # 是否為打包後的環境（PyInstaller）
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def select_csv():
    """
    讓使用者選擇 CSV 檔案，並將路徑存入變數。
    """
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        csv_path.set(file_path)

def generate():
    """
    讀取選擇的 CSV 檔案，並生成 PDF。
    """
    if not csv_path.get():
        messagebox.showerror("Error", "Please select a CSV file!")
        return

    if not os.path.exists(csv_path.get()):
        messagebox.showerror("Error", "CSV file not found! Please check the file path.")
        return

    pdf_file = os.path.join(os.path.expanduser("~"), "Desktop", "catalog.pdf")  # 存到桌面
    data = read_csv(csv_path.get())

    # 確保圖片路徑正確
    image_base_path = os.path.dirname(csv_path.get())
    if "Image Path" in data.columns:
        data["Image Path"] = data["Image Path"].apply(
            lambda x: os.path.join(image_base_path, x) if not os.path.isabs(x) else x)

    if data is not None:
        generate_pdf(data, pdf_file)
        messagebox.showinfo("Success", f"PDF successfully generated!\nFile location: {pdf_file}")
    else:
        messagebox.showerror("Error", "Failed to read CSV file. Please check the file format.")

def test_generate_pdf():
    """
    測試模式：自動讀取 products.csv，並產生 PDF 檔案到專案目錄內。
    """
    test_csv_path = "/Users/yuhsin/PycharmProjects/CatalogPDFGen/products.csv"
    image_base_path = "/Users/yuhsin/PycharmProjects/CatalogPDFGen"  # 設定圖片根目錄
    pdf_output_path = os.path.join(BASE_DIR, "catalog.pdf")  # 產生的 PDF 檔案路徑 (專案內)

    if not os.path.exists(test_csv_path):
        print(f"❌ 測試失敗：找不到測試 CSV 檔案 {test_csv_path}")
        return

    data = read_csv(test_csv_path)

    # 確保圖片路徑正確
    if "Image Path" in data.columns:
        data["Image Path"] = data["Image Path"].apply(
            lambda x: os.path.join(image_base_path, x) if not os.path.isabs(x) else x)

    if data is not None:
        generate_pdf(data, pdf_output_path)
        print(f"✅ 測試成功！PDF 產生於 {pdf_output_path}")
    else:
        print("❌ 測試失敗：無法讀取 CSV 檔案，請檢查格式")

def main():
    """
    主函式，負責啟動 GUI。
    """
    global root, csv_path
    root = tk.Tk()
    root.title("產品型錄 PDF 產生器")
    root.geometry("400x200")

    csv_path = tk.StringVar()

    # 介面設計
    tk.Label(root, text="選擇 CSV 檔案:").pack(pady=5)
    tk.Entry(root, textvariable=csv_path, width=40).pack()
    tk.Button(root, text="選擇檔案", command=select_csv).pack(pady=5)
    tk.Button(root, text="產生 PDF", command=generate).pack(pady=10)

    # 啟動 GUI
    root.mainloop()

if __name__ == "__main__":
    test_generate_pdf()
    #main()
