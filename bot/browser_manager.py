# bot/browser_manager.py

import platform
import shutil
import os
from playwright.sync_api import sync_playwright


# ==========================================================
# DETECCIÓN DE NAVEGADOR DEL SISTEMA (Windows + Linux)
# ==========================================================

def detectar_navegador():
    system = platform.system()

    # -------- WINDOWS --------
    if system == "Windows":
        posibles = [
            ("chrome", r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            ("chrome", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
            ("msedge", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
            ("brave", r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"),
        ]

        for nombre, ruta in posibles:
            if os.path.exists(ruta):
                return nombre, ruta

    # -------- LINUX --------
    elif system == "Linux":
        posibles = [
            ("chrome", "google-chrome"),
            ("msedge", "microsoft-edge"),
            ("brave", "brave-browser"),
            ("brave", "brave"),
            ("chromium", "chromium"),
            ("chromium-browser", "chromium-browser"),
        ]

        for nombre, comando in posibles:
            ruta = shutil.which(comando)
            if ruta:
                return nombre, ruta

    return None, None


# ==========================================================
# BROWSER MANAGER (Singleton)
# ==========================================================

class BrowserManager:
    _instance = None

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    @classmethod
    def get_instance(cls, headless=True, start_url=None):
        if cls._instance is None:
            cls._instance = BrowserManager()
            cls._instance._start_browser(headless, start_url)
        return cls._instance

    def _start_browser(self, headless, start_url):

        navegador, ruta = detectar_navegador()

        if not navegador:
            raise Exception(
                "No se encontró un navegador compatible instalado.\n"
                "Instale Chrome, Edge, Brave o Chromium."
            )

        self.playwright = sync_playwright().start()

        # Chrome o Edge → usar channel (más estable)
        if navegador in ["chrome", "msedge"]:
            self.browser = self.playwright.chromium.launch(
                channel=navegador,
                headless=headless
            )

        # Brave o Chromium → usar ruta directa
        else:
            self.browser = self.playwright.chromium.launch(
                executable_path=ruta,
                headless=headless
            )

        self.context = self.browser.new_context()
        self.page = self.context.new_page()

        if start_url:
            self.page.goto(start_url, wait_until="domcontentloaded")

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

        BrowserManager._instance = None

