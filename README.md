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

- 🎨 **Modern Dark UI**: Tampilan notifikasi pop-up elegan berbasis CustomTkinter dengan dukungan *Semantic Versioning* (SemVer).
- 🧵 **Asynchronous & Non-Blocking**: Pengecekan versi berjalan di *background thread*, aplikasi tidak akan mengalami *lag* atau *freeze*.
- 📊 **Google Sheets Version Management**: Manajemen versi terpusat tanpa perlu menyewa server atau membuat backend khusus.
- 🔽 **Multi-Line Changelog Support**: Mendukung daftar pembaruan berpoin yang rapi.
- ⚡ **Direct Google Drive Integration**: Tombol unduh langsung membuka browser bawaan menuju tautan Google Drive.
- 🔒 **Force Update & Soft Update**: Mendukung opsi pembaruan wajib (*Force Update*) maupun pembaruan opsional (*Soft Update*).

---

## 📁 Struktur Proyek

```text
├── main.py        # Antarmuka (UI) utama & jendela pop-up dialog pembaruan
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

### 2. Jalankan Aplikasi
```bash
python main.py
```

---

## 🛠️ Panduan Integrasi Google Sheets (Langkah demi Langkah)

### Langkah 1: Buat Tabel di Google Sheets
Buat spreadsheet baru di [Google Sheets](https://sheets.new) dengan susunan kolom berikut di baris pertama:

| app_id | latest_version | download_url | changelog | is_force |
| :--- | :--- | :--- | :--- | :--- |
| **kasir_app** | 1.0.2 | https://drive.google.com/... | Perbaikan cetak struk *(Alt+Enter)*<br>Peningkatan performa | FALSE |
| **toko_app** | 2.0.0 | https://drive.google.com/... | Fitur baru barcode scanner | FALSE |

> 💡 **Tips Mengetik Changelog:**
> Gunakan tombol **`Alt + Enter`** di dalam sel untuk membuat baris baru ke bawah.
> 
> 💡 **Tips Kolom `is_force`:**
> Anda bisa mengubah kolom `is_force` menjadi **Checkbox** (*Insert ➡️ Checkbox*) atau **Dropdown** (*Insert ➡️ Dropdown*).

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

### Langkah 3: Hubungkan ke Aplikasi Python
Buka file `main.py` dan ubah variabel `DEFAULT_VERSION_SOURCE`:

```python
# Masukkan URL Apps Script Anda disertai parameter ?app_id=nama_app_anda
DEFAULT_VERSION_SOURCE = "https://script.google.com/macros/s/AKfycb.../exec?app_id=kasir_app"
```

---

## 📦 Cara Memasang ke Proyek Aplikasi Anda yang Sudah Ada

Cukup salin file [`updater.py`](updater.py) ke dalam folder proyek Anda, lalu panggil di UI Anda:

```python
from updater import AppUpdater

CURRENT_VERSION = "1.0.0"
CHECK_URL = "https://script.google.com/macros/s/.../exec?app_id=nama_app"

updater = AppUpdater(current_version=CURRENT_VERSION, update_check_url=CHECK_URL)

# Pengecekan di latar belakang (Non-blocking)
updater.check_for_updates_async(
    on_update_available=lambda data: print("Ada update baru:", data["latest_version"]),
    on_up_to_date=lambda: print("Aplikasi sudah versi terbaru."),
    on_error=lambda err: print("Error:", err)
)
```

---

## 🔄 Alur Rilis Pembaruan di Masa Depan

Ketika Anda membuat versi baru untuk aplikasi Anda:
1. **Upload File Baru:** Upload file installer (`.exe`/`.zip`) ke **Google Drive** dan atur izin sharing ke *Anyone with the link (Viewer)*.
2. **Ubah Data di Google Sheets:**
   - Ubah `latest_version` ke nomor versi baru (misal `1.0.3`).
   - Perbarui link di kolom `download_url`.
   - Perbarui catatan perbaikan di kolom `changelog`.
3. **Selesai!** Semua pengguna yang membuka aplikasi versi lama akan langsung mendapatkan pop-up notifikasi pembaruan secara otomatis.

