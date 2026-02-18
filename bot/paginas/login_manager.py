# bot/paginas/login_manager.py

from bot.config.urls import URL_LOGIN, URL_HOME
from bot.config.settings import TIMEOUT_1, TIMEOUT_2
from playwright.sync_api import TimeoutError as PlaywrightTimeout


class ManagerSession:
    def __init__(self, page):
        self.page = page

    # ==================================================
    # LOGIN (LO DEJAMOS COMO LO TENÍAS)
    # ==================================================
    def login(self, usuario: str, password: str) -> bool:
        self.page.goto(URL_LOGIN)

        self.page.wait_for_selector("input", timeout=TIMEOUT_1)

        if self.page.locator('input[name="user"]').count() > 0:
            user_input = 'input[name="user"]'
        else:
            user_input = 'input[type="text"]'

        self.page.fill(user_input, usuario)
        self.page.fill('#pass', password)

        self.page.click('button:has-text("Iniciar sesión")')

        try:
            self.page.wait_for_url(f"{URL_HOME}*", timeout=TIMEOUT_2)
        except:
            pass

        return self.page.url.startswith(URL_HOME)

    # ==================================================
    # CIERRE DE MODAL OPTIMIZADO
    # ==================================================
    def _close_modal_safe(self):
        if not self.page.url.startswith(URL_HOME):
            return

        try:
            self.page.wait_for_load_state("networkidle")
            # 🔥 Selector exacto del botón X
            close_btn = self.page.locator('button:has(svg.lucide-x)').first
            if close_btn.count() > 0:
                close_btn.wait_for(state="visible", timeout=2000)
                close_btn.click()
                print("✅ Modal cerrado correctamente")

        except PlaywrightTimeout:
            pass
        except Exception as e:
            print("⚠️ No se pudo cerrar modal:", e)

    # ==================================================
    # LOGOUT OPTIMIZADO
    # ==================================================
    def logout(self) -> bool:
        try:
            self.page.goto(URL_HOME, wait_until="domcontentloaded")

            logout_btn = self.page.get_by_role("button", name="Cerrar sesión")

            logout_btn.wait_for(state="visible", timeout=TIMEOUT_2)
            logout_btn.click()

            self.page.wait_for_url(f"{URL_LOGIN}*", timeout=TIMEOUT_2)

            print("✅ Logout exitoso")
            return True

        except PlaywrightTimeout:
            print("❌ Timeout en logout")
            return False
        except Exception as e:
            print("❌ Error en logout:", e)
            return False

