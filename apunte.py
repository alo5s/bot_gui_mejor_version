from PySide6.QtCore import QThread, Signal
from queue import Queue, Empty

from bot.browser_manager import BrowserManager
from bot.paginas.login_manager import ManagerSession


class SessionWorker(QThread):
    # ----- señales hacia la GUI -----
    login_ok = Signal(str)
    login_error = Signal(str)
    logout_ok = Signal()
    automation_started = Signal()
    automation_finished = Signal()
    error = Signal(str)

    def __init__(self, show_browser=True):
        super().__init__()
        self.show_browser = show_browser

        self.browser = None
        self.session = None

        self.tasks = Queue()
        self._running = True
        self.logged = False
        self.automation_running = False  # 🔥 Nuevo estado

    # =========================
    # API PÚBLICA (GUI → Worker)
    # =========================

    def login(self, user: str, password: str):
        """Solicita login"""
        self.tasks.put(("login", user, password))
        if not self.isRunning():
            self.start()

    def logout(self):
        """Solicita logout"""
        self.tasks.put(("logout",))

    def start_automation(self):
        """Solicita iniciar automatización"""
        self.tasks.put(("automation",))

    def stop(self):
        """Cerrar worker y navegador"""
        self._running = False
        self.quit()
        self.wait()
        if self.browser:
            try:
                self.browser.close()
            except Exception:
                pass

    # =========================
    # LOOP PRINCIPAL DEL THREAD
    # =========================
    def run(self):
        try:
            # ---- Crear navegador UNA sola vez ----
            self.browser = BrowserManager.get_instance(
                headless=not self.show_browser
            )
            self.session = ManagerSession(self.browser.page)

            while self._running:
                try:
                    task = self.tasks.get(timeout=0.1)
                except Empty:
                    continue

                action = task[0]

                # ---------- LOGIN ----------
                if action == "login":
                    if self.logged:
                        # ⛔ ya logueado → ignorar
                        continue

                    _, user, password = task
                    ok = self.session.login(user, password)
                    if ok:
                        self.logged = True
                        self.login_ok.emit(user)
                    else:
                        self.login_error.emit("❌ Usuario o contraseña incorrectos")

                # ---------- LOGOUT ----------
                elif action == "logout":
                    if self.automation_running:
                        self.error.emit("⛔ No se puede cerrar sesión mientras el bot está activo")
                        continue

                    if not self.logged:
                        continue

                    ok = self.session.logout()
                    if ok:
                        self.logged = False
                        self.logout_ok.emit()
                    else:
                        self.error.emit("❌ Falló el logout")

                # ---------- AUTOMATIZACIÓN ----------
                elif action == "automation":
                    if not self.logged:
                        self.error.emit("⚠️ Debes iniciar sesión primero")
                        continue

                    if self.automation_running:
                        continue

                    self.automation_running = True
                    self.automation_started.emit()

                    try:
                        self.run_bot()  # 👈 lógica de automatización real
                    except Exception as e:
                        self.error.emit(str(e))
                    finally:
                        self.automation_running = False
                        self.automation_finished.emit()

        except Exception as e:
            self.error.emit(str(e))

    # =========================
    # MÉTODO DE AUTOMATIZACIÓN
    # =========================
    def run_bot(self):
        """
        Aquí va toda tu lógica de automatización.
        Usa self.session / self.browser
        """
        # EJEMPLO
        self.session.go_to_dashboard()
        self.session.process_policies()
        # 🟢 Se puede agregar loops, waits, clicks, scraping, etc.





# Forzar reinicio completo del worker al logout
# def on_logout_ok(self):
#     self.worker.quit()
#     self.worker.wait()
#
#     self.worker = SessionWorker(self.show_browser)
#     self.worker.login_ok.connect(self.on_login_ok)
#     self.worker.login_error.connect(self.on_login_error)
#     self.worker.logout_ok.connect(self.on_logout_ok)
#     self.worker.error.connect(self.on_worker_error)
#
#     self.login_view = LoginView()
#     self.login_view.login_requested.connect(self.start_login)
#     self.window.setCentralWidget(self.login_view)
