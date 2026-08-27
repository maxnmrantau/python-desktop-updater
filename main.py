import os
import customtkinter as ctk
from tkinter import messagebox
from updater import AppUpdater

# Konfigurasi Tampilan
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Versi aplikasi saat ini
CURRENT_APP_VERSION = "1.0.0"

# Lokasi sumber data versi dari Google Sheets Web App Anda
# Catatan: Tambahkan parameter ?app_id=sesuai_nama_di_tabel_sheets
DEFAULT_VERSION_SOURCE = "https://script.google.com/macros/s/AKfycbyqwsdcw7PkbjPOvC-VQOWdaEbJjcGigJ7BNIfFeoHxo6isU9AcrWo1Ns9mAaajK-1C/exec?app_id=kasir_app"




class UpdateDialog(ctk.CTkToplevel):
    """
    Jendela Pop-up Modal untuk Menampilkan Notifikasi Pembaruan Aplikasi.
    """
    def __init__(self, parent, update_data: dict):
        super().__init__(parent)
        self.parent = parent
        self.update_data = update_data
        
        self.title("Pembaruan Aplikasi Tersedia")
        self.geometry("520x440")
        self.resizable(False, False)

        # Pusatkan posisi dialog relatif terhadap jendela utama
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 260
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 220
        self.geometry(f"+{x}+{y}")
        
        self.transient(parent)
        self.grab_set()  # Kunci fokus pada pop-up

        self.setup_ui()

    def setup_ui(self):
        # Header Badge
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=24, pady=(20, 10))

        title_label = ctk.CTkLabel(
            header_frame, 
            text="🚀 Pembaruan Tersedia!", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#38bdf8"
        )
        title_label.pack(anchor="w")

        latest_ver = self.update_data.get("latest_version", "Baru")
        sub_label = ctk.CTkLabel(
            header_frame, 
            text=f"Versi baru v{latest_ver} siap diunduh (Versi Anda: v{CURRENT_APP_VERSION})",
            font=ctk.CTkFont(size=13),
            text_color="#94a3b8"
        )
        sub_label.pack(anchor="w", pady=(4, 0))

        # Changelog Container
        changelog_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("#1e293b", "#1e293b"))
        changelog_frame.pack(fill="both", expand=True, padx=24, pady=10)

        cl_title = ctk.CTkLabel(
            changelog_frame, 
            text="📋 Apa yang Baru di Versi Ini:", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f8fafc"
        )
        cl_title.pack(anchor="w", padx=16, pady=(12, 6))

        # List Changelog (Memformat setiap baris agar rapi ke bawah)
        changelog_raw = self.update_data.get("changelog", ["Peningkatan stabilitas dan perbaikan bug."])
        lines = []
        if isinstance(changelog_raw, list):
            for item in changelog_raw:
                for sub in str(item).split("\n"):
                    cleaned = sub.strip().lstrip("-").lstrip("•").strip()
                    if cleaned:
                        lines.append(f"• {cleaned}")
        else:
            for sub in str(changelog_raw).split("\n"):
                cleaned = sub.strip().lstrip("-").lstrip("•").strip()
                if cleaned:
                    lines.append(f"• {cleaned}")

        changelog_text = "\n".join(lines) if lines else "• Pembaruan dan perbaikan bug."

        cl_content = ctk.CTkTextbox(
            changelog_frame, 
            fg_color="transparent", 
            text_color="#cbd5e1",
            font=ctk.CTkFont(size=13),
            activate_scrollbars=True
        )
        cl_content.insert("1.0", changelog_text)
        cl_content.configure(state="disabled")
        cl_content.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Tombol Aksi
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(10, 20))

        # Tombol Update (Buka Google Drive)
        self.btn_update = ctk.CTkButton(
            btn_frame,
            text="Download",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=42,
            fg_color="#0284c7",
            hover_color="#0369a1",
            command=self.on_click_update
        )
        self.btn_update.pack(side="right", padx=(8, 0), fill="x", expand=True)

        # Tombol Nanti (jika bukan update wajib / force update)
        is_force = self.update_data.get("is_force_update", False)
        if not is_force:
            self.btn_later = ctk.CTkButton(
                btn_frame,
                text="Nanti Saja",
                font=ctk.CTkFont(size=13),
                height=42,
                fg_color="#334155",
                hover_color="#475569",
                command=self.destroy
            )
            self.btn_later.pack(side="right", fill="x", expand=True)

    def on_click_update(self):
        """Membuka link Google Drive di browser default pengguna"""
        download_url = self.update_data.get("download_url", "")
        if download_url:
            AppUpdater.open_download_page(download_url)
            self.destroy()
        else:
            messagebox.showerror("Error", "URL Unduhan tidak ditemukan!")


class MainApp(ctk.CTk):
    """
    Aplikasi Utama Desktop
    """
    def __init__(self):
        super().__init__()

        self.title("Aplikasi Desktop - Sistem Cek Update")
        self.geometry("640x480")
        self.minsize(580, 420)

        self.updater = AppUpdater(
            current_version=CURRENT_APP_VERSION, 
            update_check_url=DEFAULT_VERSION_SOURCE
        )

        self.setup_ui()
        
        # Pengecekan otomatis saat aplikasi pertama kali dibuka (diberi jeda 800ms)
        self.after(800, self.check_updates_auto)

    def setup_ui(self):
        # Header / Banner
        header = ctk.CTkFrame(self, corner_radius=12, fg_color=("#1e293b", "#0f172a"))
        header.pack(fill="x", padx=24, pady=20)

        app_title = ctk.CTkLabel(
            header, 
            text="💻 Sistem Manajemen Toko", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#f8fafc"
        )
        app_title.pack(anchor="w", padx=20, pady=(16, 4))

        version_badge = ctk.CTkLabel(
            header, 
            text=f"Versi Terpasang: v{CURRENT_APP_VERSION}", 
            font=ctk.CTkFont(size=13),
            text_color="#38bdf8"
        )
        version_badge.pack(anchor="w", padx=20, pady=(0, 16))

        # Konten Utama
        content_frame = ctk.CTkFrame(self, corner_radius=12)
        content_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # Status Update
        self.status_label = ctk.CTkLabel(
            content_frame,
            text="🔍 Menunggu pengecekan pembaruan...",
            font=ctk.CTkFont(size=14),
            text_color="#94a3b8"
        )
        self.status_label.pack(pady=(30, 15))

        # Tombol Cek Update Manual
        self.btn_check = ctk.CTkButton(
            content_frame,
            text="🔄 Periksa Pembaruan Sekarang",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self.check_updates_manual
        )
        self.btn_check.pack(pady=10)

        # Bagian Penjelasan Integrasi Google Sheets
        dev_box = ctk.CTkFrame(content_frame, fg_color=("#0f172a", "#1e293b"), corner_radius=8)
        dev_box.pack(fill="x", padx=20, pady=(25, 15))

        dev_title = ctk.CTkLabel(
            dev_box,
            text="📊 Cara Kerja Auto-Update (Google Sheets):",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#38bdf8"
        )
        dev_title.pack(anchor="w", padx=12, pady=(10, 4))

        dev_desc = ctk.CTkLabel(
            dev_box,
            text="1. Aplikasi mengambil data versi dari Google Sheets (via Apps Script Web App).\n"
                 "2. Cukup edit versi & changelog (Alt+Enter) di Spreadsheet untuk rilis baru.\n"
                 "3. Klik 'Download' di notifikasi akan langsung membuka link Google Drive di browser.",
            font=ctk.CTkFont(size=12),
            text_color="#cbd5e1",
            justify="left"
        )
        dev_desc.pack(anchor="w", padx=12, pady=(0, 10))

    def check_updates_auto(self):
        """Pengecekan update secara otomatis saat startup"""
        self.status_label.configure(text="🔍 Memeriksa pembaruan di server...", text_color="#38bdf8")
        self.updater.check_for_updates_async(
            on_update_available=self._on_update_found,
            on_up_to_date=self._on_up_to_date,
            on_error=self._on_update_error
        )

    def check_updates_manual(self):
        """Pengecekan update saat tombol manual ditekan"""
        self.btn_check.configure(state="disabled", text="Memeriksa...")
        self.status_label.configure(text="🔍 Memeriksa pembaruan di server...", text_color="#38bdf8")
        
        def on_complete_up_to_date():
            self.btn_check.configure(state="normal", text="🔄 Periksa Pembaruan Sekarang")
            self._on_up_to_date()
            messagebox.showinfo("Informasi", "Aplikasi Anda sudah menggunakan versi terbaru!")

        def on_complete_error(err):
            self.btn_check.configure(state="normal", text="🔄 Periksa Pembaruan Sekarang")
            self._on_update_error(err)
            messagebox.showerror("Gagal Cek Update", f"Terjadi kesalahan saat memeriksa update:\n{err}")

        def on_complete_found(data):
            self.btn_check.configure(state="normal", text="🔄 Periksa Pembaruan Sekarang")
            self._on_update_found(data)

        self.updater.check_for_updates_async(
            on_update_available=on_complete_found,
            on_up_to_date=on_complete_up_to_date,
            on_error=on_complete_error
        )

    def _on_update_found(self, data: dict):
        """Dipanggil ketika versi baru ditemukan"""
        self.after(0, lambda: self._show_update_modal(data))

    def _show_update_modal(self, data: dict):
        latest = data.get("latest_version", "Baru")
        self.status_label.configure(
            text=f"✨ Pembaruan versi v{latest} ditemukan!", 
            text_color="#4ade80"
        )
        # Buka Pop-up Dialog
        UpdateDialog(self, data)

    def _on_up_to_date(self):
        """Dipanggil ketika versi sudah paling baru"""
        self.after(0, lambda: self.status_label.configure(
            text="✅ Aplikasi Anda sudah menggunakan versi terbaru.", 
            text_color="#94a3b8"
        ))

    def _on_update_error(self, err_msg: str):
        """Dipanggil ketika terjadi error jaringan / gagal fetch"""
        self.after(0, lambda: self.status_label.configure(
            text=f"⚠️ Gagal memeriksa update: {err_msg}", 
            text_color="#f87171"
        ))


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
