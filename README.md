<img width="638" height="508" alt="20260827-142848" src="https://github.com/user-attachments/assets/a4434c9e-45d0-4e37-98e6-5d061ddb6772" />

# 🚀 Python Desktop Auto-Updater

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![UI Framework](https://img.shields.io/badge/UI-CustomTkinter-blueviolet.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Backend](https://img.shields.io/badge/Database-Google%20Sheets-success.svg)](https://sheets.google.com)
[![Storage](https://img.shields.io/badge/Storage-Google%20Drive-yellow.svg)](https://drive.google.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Python Desktop Auto-Updater** adalah modul sistem pengecekan dan notifikasi pembaruan (*auto-update notification*) untuk aplikasi desktop berbasis Python. Sistem ini dirancang ringan (*lightweight*), menggunakan antarmuka modern (**CustomTkinter**), dan memanfaatkan **Google Sheets** sebagai database versi terpusat serta **Google Drive** sebagai tempat penyimpanan file installer.

Dengan sistem ini, Anda dapat mengelola rilis pembaruan untuk **puluhan aplikasi desktop sekaligus** hanya dari satu tabel spreadsheet (bahkan bisa diedit langsung dari smartphone)!

---

## ✨ Fitur Utama

- 🎨 **Modern Dark UI**: Tampilan notifikasi pop-up dialog elegan berbasis CustomTkinter dengan dukungan *Semantic Versioning* (SemVer).
- 🧵 **Asynchronous & Non-Blocking**: Pengecekan versi berjalan di *background thread*, aplikasi tidak akan mengalami *lag* atau *freeze*.
- 📊 **Google Sheets Version Management**: Manajemen versi terpusat tanpa perlu menyewa server atau membuat backend khusus.
- 🔽 **Multi-Line Changelog Support**: Mendukung daftar pembaruan berpoin yang rapi ke bawah.
- ⚡ **Direct Google Drive Integration**: Tombol unduh langsung membuka browser bawaan menuju tautan Google Drive.
- 🔒 **Force Update & Soft Update**: Mendukung opsi pembaruan wajib (*Force Update*) maupun pembaruan opsional (*Soft Update*).
- 🚀 **Auto-Check on Startup**: Notifikasi otomatis muncul saat aplikasi dibuka hanya jika ada versi baru (tanpa mengganggu jika aplikasi sudah versi terbaru).

---

## 📁 Struktur Proyek

```text
├── main.py        # Contoh implementasi lengkap (UI Utama & Pop-up Notifikasi Update)
├── updater.py     # Modul inti logika update (Threading, Version Check, Browser Launcher)
├── version.json   # Template data konfigurasi versi (opsional untuk simulasi lokal/GitHub)
├── .gitignore     # Filter file sementara / cache python
└── README.md      # Dokumentasi lengkap proyek
```

---

## 🚀 Panduan Instalasi & Menjalankan

### 1. Prasyarat
Pastikan Anda telah menginstal Python 3.8 ke atas dan pustaka yang dibutuhkan:

```bash
pip install customtkinter requests packaging
```

### 2. Jalankan Contoh Aplikasi
```bash
python main.py
```

---

## 🛠️ Panduan Integrasi Google Sheets (Database Versi)

### Langkah 1: Buat Tabel di Google Sheets
Buat spreadsheet baru di [Google Sheets](https://sheets.new) dengan susunan kolom berikut di baris pertama:

| app_id | latest_version | download_url | changelog | is_force |
| :--- | :--- | :--- | :--- | :--- |
| **kasir_app** | 1.0.2 | https://drive.google.com/drive/folders/... | Perbaikan cetak struk *(Alt+Enter)*<br>Peningkatan performa | FALSE |
| **toko_app** | 2.0.0 | https://drive.google.com/drive/folders/... | Fitur baru barcode scanner | FALSE |

> 💡 **Tips Mengetik Changelog:**
> Gunakan tombol **`Alt + Enter`** di dalam sel spreadsheet untuk membuat baris baru ke bawah.
> 
> 💡 **Tips Kolom `is_force`:**
> Anda bisa mengubah kolom `is_force` menjadi **Checkbox** (*Insert ➡️ Checkbox*) atau **Dropdown** (*Insert ➡️ Dropdown*).
> - `FALSE` = Soft Update (Ada tombol "Download" & "Nanti Saja").
> - `TRUE` = Force Update (Hanya ada tombol "Download", wajib update).

---

### Langkah 2: Buat Google Apps Script (Web API)
1. Di Google Sheets, klik menu **Extensions** ➡️ **Apps Script**.
2. Hapus semua kode yang ada dan paste kode berikut:

```javascript
function doGet(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var data = sheet.getDataRange().getValues();
  var appId = e.parameter.app_id;
  
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == appId) {
      var result = {
        latest_version: String(data[i][1]),
        download_url: data[i][2],
        changelog: String(data[i][3]).split(/\r?\n/),
        is_force_update: data[i][4] === true || String(data[i][4]).toUpperCase() === "TRUE"
      };
      return ContentService.createTextOutput(JSON.stringify(result))
             .setMimeType(ContentService.MimeType.JSON);
    }
  }
  return ContentService.createTextOutput(JSON.stringify({error: "App not found"}))
         .setMimeType(ContentService.MimeType.JSON);
}
```

3. Klik tombol **Deploy** ➡️ **New deployment**.
4. Pilih tipe **Web app**:
   - **Execute as**: *Me*
   - **Who has access**: *Anyone*
5. Klik **Deploy** dan berikan izin (*Authorize access*).
6. Salin **Web App URL** yang diberikan (berakhiran `/exec`).

---

## 📦 Cara Memasang ke Aplikasi Desktop Anda Sendiri

Untuk menerapkan sistem ini ke aplikasi desktop Anda yang sudah ada, ikuti 2 langkah berikut:

### 1. Salin File `updater.py` ke Folder Proyek Anda
Salin file [`updater.py`](updater.py) ke dalam satu folder dengan kode aplikasi Anda.

### 2. Pasang Kode Auto-Update ke File Utama Anda (`main.py` / `app.py`)

Berikut adalah contoh lengkap cara mengintegrasikan **Pengecekan Otomatis saat Startup** dan **Jendela Pop-up Dialog Update**:

```python
import customtkinter as ctk
from tkinter import messagebox
from updater import AppUpdater

# 1. Tentukan versi aplikasi Anda saat ini
CURRENT_APP_VERSION = "1.0.0"

# 2. Masukkan URL Apps Script Google Sheets Anda (disertai ?app_id=nama_app_anda)
VERSION_SOURCE_URL = "https://script.google.com/macros/s/AKfycb.../exec?app_id=kasir_app"


class UpdateDialog(ctk.CTkToplevel):
    """Jendela Pop-up Notifikasi Pembaruan"""
    def __init__(self, parent, update_data: dict):
        super().__init__(parent)
        self.update_data = update_data
        
        self.title("Pembaruan Aplikasi Tersedia")
        self.geometry("520x440")
        self.resizable(False, False)
        
        # Pusatkan posisi dialog
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 260
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 220
        self.geometry(f"+{x}+{y}")
        
        self.transient(parent)
        self.grab_set()

        # Header
        latest_ver = self.update_data.get("latest_version", "Baru")
        ctk.CTkLabel(
            self, 
            text="🚀 Pembaruan Tersedia!", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#38bdf8"
        ).pack(anchor="w", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            self, 
            text=f"Versi baru v{latest_ver} siap diunduh (Versi Anda: v{CURRENT_APP_VERSION})",
            font=ctk.CTkFont(size=13),
            text_color="#94a3b8"
        ).pack(anchor="w", padx=24, pady=(0, 10))

        # Changelog Container
        cl_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("#1e293b", "#1e293b"))
        cl_frame.pack(fill="both", expand=True, padx=24, pady=10)

        ctk.CTkLabel(
            cl_frame, 
            text="📋 Apa yang Baru di Versi Ini:", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f8fafc"
        ).pack(anchor="w", padx=16, pady=(12, 6))

        # Memformat teks changelog menjadi poin-poin rapi ke bawah
        changelog_raw = self.update_data.get("changelog", ["Peningkatan stabilitas."])
        lines = []
        if isinstance(changelog_raw, list):
            for item in changelog_raw:
                for sub in str(item).split("\n"):
                    cleaned = sub.strip().lstrip("-").lstrip("•").strip()
                    if cleaned:
                        lines.append(f"• {cleaned}")
        else:
            lines = [f"• {changelog_raw}"]

        cl_box = ctk.CTkTextbox(
            cl_frame, 
            fg_color="transparent", 
            text_color="#cbd5e1",
            font=ctk.CTkFont(size=13)
        )
        cl_box.insert("1.0", "\n".join(lines))
        cl_box.configure(state="disabled")
        cl_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Tombol Aksi
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(10, 20))

        # Tombol Download (Membuka Google Drive di Browser)
        ctk.CTkButton(
            btn_frame,
            text="Download",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=42,
            fg_color="#0284c7",
            hover_color="#0369a1",
            command=self.on_download
        ).pack(side="right", padx=(8, 0), fill="x", expand=True)

        # Tombol Nanti (jika bukan force update)
        if not self.update_data.get("is_force_update", False):
            ctk.CTkButton(
                btn_frame,
                text="Nanti Saja",
                font=ctk.CTkFont(size=13),
                height=42,
                fg_color="#334155",
                hover_color="#475569",
                command=self.destroy
            ).pack(side="right", fill="x", expand=True)

    def on_download(self):
        download_url = self.update_data.get("download_url", "")
        if download_url:
            AppUpdater.open_download_page(download_url)
            self.destroy()


class MainApplication(ctk.CTk):
    """Aplikasi Utama Anda"""
    def __init__(self):
        super().__init__()
        self.title("Aplikasi Kasir / Manajemen Toko")
        self.geometry("800x500")

        # Inisialisasi Updater
        self.updater = AppUpdater(
            current_version=CURRENT_APP_VERSION, 
            update_check_url=VERSION_SOURCE_URL
        )

        # Cek update otomatis 1 detik setelah aplikasi terbuka (Non-blocking)
        self.after(1000, self.auto_check_update)

        # ... (Letakkan kode antarmuka aplikasi utama Anda di sini) ...
        ctk.CTkLabel(
            self, 
            text=f"Selamat Datang di Aplikasi (v{CURRENT_APP_VERSION})", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=40)

    def auto_check_update(self):
        # Jalankan di background thread
        self.updater.check_for_updates_async(
            on_update_available=lambda data: UpdateDialog(self, data)
            # on_up_to_date sengaja dikosongkan agar tidak mengganggu user jika sudah versi terbaru
        )


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
```

---

## ❓ Apakah Perlu Tombol "Cek Update"?

**Tidak wajib.** 
- Standar aplikasi desktop modern (seperti Telegram, Spotify, VS Code) melakukan **pengecekan otomatis saat aplikasi pertama kali dibuka**.
- Pop-up pembaruan **hanya akan muncul jika memang ada versi baru di Google Sheets**. Jika versi sudah paling baru, aplikasi akan berjalan tenang tanpa memunculkan pop-up yang mengganggu pengguna.
- Tombol manual hanya opsional jika Anda ingin meletakkannya di menu *Pengaturan (Settings)* atau *Tentang (About)*.

---

## 🔄 Alur Rilis Pembaruan di Masa Depan

Ketika Anda merilis versi baru untuk aplikasi Anda:
1. **Upload File Baru:** Upload file installer (`.exe`/`.zip`) ke **Google Drive** dan atur izin sharing ke *Anyone with the link (Viewer)*.
2. **Ubah Data di Google Sheets:**
   - Ubah `latest_version` ke nomor versi baru (misal `1.0.3`).
   - Perbarui link di kolom `download_url`.
   - Perbarui catatan perbaikan di kolom `changelog` (gunakan `Alt+Enter` untuk baris baru).
3. **Selesai!** Semua pengguna yang membuka aplikasi versi lama akan langsung mendapatkan pop-up notifikasi pembaruan secara otomatis.

