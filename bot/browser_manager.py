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
# BROWSER MANAGER (Singleton Optimizado)
# ==========================================================

class BrowserManager:
    _instance = None

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    # ------------------------------------------------------
    # SINGLETON
    # ------------------------------------------------------
    @classmethod
    def get_instance(cls, headless=True, start_url=None):
        if cls._instance is None:
            cls._instance = BrowserManager()
            cls._instance._start_browser(headless, start_url)
        return cls._instance

    # ------------------------------------------------------
    # INICIO OPTIMIZADO DEL NAVEGADOR
    # ------------------------------------------------------
    def _start_browser(self, headless=True, start_url=None):

        navegador, ruta = detectar_navegador()

        if not navegador:
            raise Exception(
                "No se encontró un navegador compatible.\n"
                "Instale Chrome, Edge, Brave o Chromium."
            )

        self.playwright = sync_playwright().start()

        # 🔥 ARGUMENTOS DE RENDIMIENTO
        launch_args = [
            "--disable-dev-shm-usage",
            "--disable-extensions",
            "--disable-infobars",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-default-apps",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-popup-blocking",
            "--disable-renderer-backgrounding",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
        ]

        # --------------------------------------------------
        # LANZAMIENTO
        # --------------------------------------------------
        if navegador in ["chrome", "msedge"]:
            self.browser = self.playwright.chromium.launch(
                channel=navegador,
                headless=headless,
                args=launch_args
            )
        else:
            self.browser = self.playwright.chromium.launch(
                executable_path=ruta,
                headless=headless,
                args=launch_args
            )

        # --------------------------------------------------
        # CONTEXTO OPTIMIZADO
        # --------------------------------------------------
        self.context = self.browser.new_context(
            java_script_enabled=True,
            ignore_https_errors=True,
            locale="es-ES",
        )

        # 🔥 BLOQUEAR RECURSOS PESADOS (acelera muchísimo)
        self.context.route(
            "**/*",
            lambda route: route.abort()
            # if route.request.resource_type in ["image", "media", "font"]
            if route.request.resource_type in ["media", "font"]

            else route.continue_()
        )

        self.page = self.context.new_page()

        # --------------------------------------------------
        # IR A URL INICIAL
        # --------------------------------------------------
        if start_url:
            self.page.goto(start_url, wait_until="domcontentloaded")

    # ------------------------------------------------------
    # OBTENER PAGE
    # ------------------------------------------------------
    def get_page(self):
        return self.page

    # ------------------------------------------------------
    # CERRAR NAVEGADOR
    # ------------------------------------------------------
    def close(self):
        try:
            if self.context:
                self.context.close()

            if self.browser:
                self.browser.close()

            if self.playwright:
                self.playwright.stop()

        finally:
            BrowserManager._instance = None

