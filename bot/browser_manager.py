# bot/browser_manager.py

import os
import sys
from playwright.sync_api import sync_playwright


def configurar_playwright():
    """
    Configura la ruta de los navegadores de Playwright
    para que funcione tanto en desarrollo como en .exe (PyInstaller)
    """
    if getattr(sys, "frozen", False):
        # Cuando está empaquetado
        base_path = sys._MEIPASS
    else:
        # Cuando está en desarrollo
        base_path = os.path.dirname(os.path.abspath(__file__))

    browsers_path = os.path.join(base_path, "playwright-browsers")
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path


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

        # 🔥 IMPORTANTE: configurar antes de iniciar Playwright
        configurar_playwright()

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

        if start_url:
            self.page.goto(start_url)

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

        BrowserManager._instance = None

