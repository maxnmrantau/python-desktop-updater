import json
import threading
import webbrowser
from typing import Callable, Optional, Dict, Any
from packaging import version
import requests

class AppUpdater:
    """
    Modul untuk menangani pengecekan pembaruan versi aplikasi dan membuka browser ke link unduhan.
    """
    def __init__(self, current_version: str, update_check_url: str):
        self.current_version = current_version
        self.update_check_url = update_check_url

    def is_newer_version(self, latest_version: str) -> bool:
        """Membandingkan apakah versi di server lebih baru dari versi lokal saat ini."""
        try:
            return version.parse(latest_version) > version.parse(self.current_version)
        except Exception:
            return False

    def fetch_version_info(self) -> Dict[str, Any]:
        """
        Mengambil informasi versi dari server online atau file lokal (untuk pengujian).
        """
        # Jika update_check_url adalah URL online (http/https)
        if self.update_check_url.startswith("http://") or self.update_check_url.startswith("https://"):
            response = requests.get(self.update_check_url, timeout=7)
            response.raise_for_status()
            return response.json()
        else:
            # Jika menggunakan file lokal untuk simulasi testing offline
            with open(self.update_check_url, "r", encoding="utf-8") as f:
                return json.load(f)

    def check_for_updates_async(
        self, 
        on_update_available: Callable[[Dict[str, Any]], None],
        on_up_to_date: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[str], None]] = None
    ):
        """
        Menjalankan pengecekan update di background thread agar aplikasi UI tidak freeze/hang.
        """
        def _worker():
            try:
                data = self.fetch_version_info()
                
                if "error" in data:
                    raise ValueError(f"Server mengembalikan error: {data['error']}")

                latest_ver = data.get("latest_version")
                if not latest_ver:
                    raise ValueError("Format data tidak valid: 'latest_version' tidak ditemukan.")

                if self.is_newer_version(latest_ver):
                    # Callback saat ada versi baru
                    on_update_available(data)
                else:
                    # Callback saat versi sudah terbaru
                    if on_up_to_date:
                        on_up_to_date()
            except Exception as e:
                if on_error:
                    on_error(str(e))

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    @staticmethod
    def open_download_page(download_url: str):
        """
        Membuka browser default sistem operasi menuju link download (Google Drive).
        """
        if download_url:
            webbrowser.open(download_url, new=2)
