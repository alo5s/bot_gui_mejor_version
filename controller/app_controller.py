# controller/app_controller.py

from ui.layout.layout_login import LoginView
from ui.layout.layout_home import HomeView
from controller.workers import SessionWorker


class AppController:
    def __init__(self, window):
        self.window = window
        self.show_browser = True

        # ---------- worker único ----------
        self.worker = SessionWorker(self.show_browser)

        # ---------- señales del worker ----------
        self.worker.login_ok.connect(self.on_login_ok)
        self.worker.login_error.connect(self.on_login_error)
        self.worker.logout_ok.connect(self.on_logout_ok)

        self.worker.automation_ok.connect(self.on_automation_ok)
        self.worker.automation_error.connect(self.on_automation_ok)
        self.worker.automation_paused.connect(self.on_automation_paused)
        

        self.worker.error.connect(self.on_worker_error)
        self.worker.persona_no_encontrada.connect(self.show_persona_no_encontrada)


        # ---------- vista login ----------
        self.login_view = LoginView()
        self.login_view.login_requested.connect(self.start_login)
        self.window.setCentralWidget(self.login_view)

    # ==================================================
    # CONFIG
    # ==================================================
    def set_show_browser(self, value: bool):
        # self.show_browser = value
        # if self.worker and not self.worker.isRunning():
        #     self.worker.show_browser = value
        if self.worker:
            self.worker.show_browser = value
    # ==================================================
    # LOGIN
    # ==================================================
    def start_login(self, user, password):
        # login() ya se encarga de iniciar el thread
        self.worker.login(user, password)

    def on_login_ok(self, user):
        self.home = HomeView(user)
        # conectar señal del menú

        
        # 🔴 CONECTAR ERROR AQUÍ (cuando home ya existe)
        self.worker.automation_error.connect(self.home.show_bot_error)

        # conectar señal del menú
        self.window.menu.data_updated.connect(self.home.reload_custom_data)
        
        # 🔌 conectar señales UI → worker
        self.home.logout_requested.connect(self.logout)
        self.home.start_requested.connect(self.worker.start_automation)
        self.home.pause_requested.connect(self.worker.pause_automation)
        self.home.resume_requested.connect(self.worker.resume_automation)
        self.home.stop_requested.connect(self.worker.stop_automation)

        # 🔹 conectar señal poliza_terminada → mostrar alert
        self.worker.poliza_terminada.connect(self.home.show_poliza_alert)


        self.window.setCentralWidget(self.home)

    def on_login_error(self, msg):
        self.login_view.show_error(msg)
        self.login_view.reset()

    # ==================================================
    # LOGOUT
    # ==================================================
    def logout(self):
        self.worker.logout()

    def on_logout_ok(self):
        self.login_view = LoginView()
        self.login_view.login_requested.connect(self.start_login)
        self.window.setCentralWidget(self.login_view)

    # ==================================================
    # AUTOMATION STATUS
    # ==================================================
    def on_automation_ok(self, msg):
        if not hasattr(self, "home"):
            return

        # mostrar estado
        self.home.status_label.setText(msg)
        self.home.logs.append(msg)

        # si terminó / falló / se detuvo → reset UI
        if (
            "finalizada" in msg
            or "detenida" in msg
            or msg.startswith("❌")
        ):
            self.home.reset_bot_ui()

    def on_automation_paused(self, msg):
        if hasattr(self, "home"):
            self.home.status_label.setText(msg)
            self.home.logs.append(msg)

    # ==================================================
    # ERRORES CRÍTICOS
    # ==================================================
    def on_worker_error(self, msg):
        print("🔥 Worker error:", msg)

        self.login_view = LoginView()
        self.login_view.login_requested.connect(self.start_login)
        self.window.setCentralWidget(self.login_view)
        self.login_view.show_error(msg)



    def show_persona_no_encontrada(self, data: dict):
        if hasattr(self, "home"):
            self.home.show_persona_no_encontrada(
                data["dni"],
                data["poliza"],
                data["asegurado"]
            )

