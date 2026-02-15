# bot/paginas/login_manager.py
from bot.config.urls import URL_LOGIN, URL_HOME
from bot.config.settings import TIMEOUT_1, TIMEOUT_2


class ManagerSession:
    def __init__(self, page):
        self.page = page

    def login(self, usuario: str, password: str) -> bool:
        # Comprobamos si estamos en la página de login
        self.page.goto(URL_LOGIN)

        # Esperar inputs
        self.page.wait_for_selector("input", timeout=TIMEOUT_1)

        # Detectar input de usuario
        if self.page.locator('input[name="user"]').count() > 0:
            user_input = 'input[name="user"]'
        else:
            user_input = 'input[type="text"]'

        self.page.fill(user_input, usuario)
       
        self.page.fill('#pass', password)
 
        # Click botón de login
        self.page.click('button:has-text("Iniciar sesión")')

        try:
            # Esperamos explícitamente la URL HOME
            self.page.wait_for_url(f"{URL_HOME}*", timeout=TIMEOUT_2)
        except:
            pass
        return self.page.url.startswith(URL_HOME)
        
        # Esperar a que cargue la página de HOME
        self.page.wait_for_load_state("networkidle")


    def _close_modal_safe(self):
        try:
            self.page.wait_for_load_state("networkidle")
            if self.page.url.startswith(URL_HOME):

                close_modal_btn = self.page.locator('button:has-text("Close")')

                if close_modal_btn.count() > 0:
                    close_modal_btn.wait_for(state="visible", timeout=3000)
                    close_modal_btn.click()
                    print("✅ Modal cerrado")
        except Exception as e:
            print("⚠️ No se pudo cerrar modal:", e)


    def logout(self):
        self.page.goto(URL_HOME)
        print("🌐 URL actual:", self.page.url)
        

        self.page.wait_for_selector('text="Cerrar sesión"', timeout=TIMEOUT_2)
        self.page.click('text="Cerrar sesión"')
        print("✅ Click en botón Logout")

        self.page.wait_for_load_state("networkidle")

        if self.page.url.startswith(URL_LOGIN):
            return True

        print("❌ No se pudo cerrar sesión")
        return False

