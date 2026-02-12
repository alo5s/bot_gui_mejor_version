from PySide6.QtCore import QThread, Signal
from queue import Queue, Empty
from bot.browser_manager import BrowserManager
from bot.paginas.login_manager import ManagerSession
from bot.paginas.bot_manager import ManagerBot
import time


class BotState:
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"


class SessionWorker(QThread):
    # ---------- señales ----------
    login_ok = Signal(str)
    login_error = Signal(str)
    logout_ok = Signal()

    automation_ok = Signal(str)
    automation_error = Signal(str)
    automation_paused = Signal(str)

    error = Signal(str)

    # ---------- init ----------
    def __init__(self, show_browser=True):
        super().__init__()
        self.show_browser = show_browser

        self.browser = None
        self.session = None
        self.bot = None

        self.tasks = Queue()
        self._running = True
        self.logged = False

        self.state = BotState.IDLE
        self.current_stage = 1

        self.ubicaciones = []
        self.aseguradora = []

        self.polizas_ubicacion = None
        self.pago_ubicacion = None
        self.excel_ubicacion = None
        self.guardado_ubicacion = None
    # ==================================================
    # API PUBLICA
    # ==================================================
    def login(self, user: str, password: str):
        self.tasks.put(("login", user, password))
        if not self.isRunning():
            self.start()

    def logout(self):
        self.tasks.put(("logout",))

    def start_automation(self, data: dict):
        self.tasks.put(("start", data))

    def pause_automation(self):
        self.tasks.put(("pause",))

    def resume_automation(self):
        self.tasks.put(("resume",))

    def stop_automation(self):
        self.tasks.put(("stop",))

    # ==================================================
    # THREAD LOOP
    # ==================================================
    def run(self):
        try:
            if not self.browser:
                self.browser = BrowserManager.get_instance(
                    headless=not self.show_browser
                )
                self.session = ManagerSession(self.browser.page)

            while self._running:
                try:
                    task = self.tasks.get_nowait()
                    self._handle_task(task)
                except Empty:
                    pass

                self._run_bot_cycle()
                time.sleep(0.1)

        except Exception as e:
            self.error.emit(str(e))

    # ==================================================
    # TASK HANDLER
    # ==================================================
    def _handle_task(self, task):
        action = task[0]

        # ---------- LOGIN ----------
        if action == "login":
            if self.logged:
                return
            _, user, password = task
            if self.session.login(user, password):
                self.logged = True
                self.login_ok.emit(user)
            else:
                self.login_error.emit("❌ Usuario o contraseña incorrectos")

        # ---------- LOGOUT ----------
        elif action == "logout":
            if self.logged and self.session.logout():
                self.logged = False
                self.logout_ok.emit()

        # ---------- START ----------
        elif action == "start":
            if self.logged and self.state == BotState.IDLE:
                _, data = task

                self.ubicaciones = data["ubicaciones"]
                self.aseguradora = data["aseguradoras"]
                
                
                self.polizas_ubicacion = data["polizas_ubicacion"]
                self.pago_ubicacion = data["pago_ubicacion"]
                self.excel_ubicacion = data["excel_ubicacion"]
                self.guardado_ubicacion = data["guardado_ubicacion"]

                self.current_stage = 1
                self.state = BotState.RUNNING
                self.automation_ok.emit("▶  Automatización iniciada")

        # ---------- PAUSE ----------
        elif action == "pause":
            if self.state == BotState.RUNNING:
                self.state = BotState.PAUSED
                self.automation_paused.emit(
                    f"⏸  Pausado en etapa {self.current_stage}"
                )

        # ---------- RESUME ----------
        elif action == "resume":
            if self.state == BotState.PAUSED:
                self.state = BotState.RUNNING
                self.automation_ok.emit(
                    f"▶  Reanudando desde etapa {self.current_stage}"
                )

        # ---------- STOP ----------
        elif action == "stop":
            self._reset_bot("⏹  Automatización detenida")

    # ==================================================
    # BOT FLOW
    # ==================================================
    def _run_bot_cycle(self):
        if self.state != BotState.RUNNING:
            return

        if not self.bot:
            self.bot = ManagerBot(self.session.page)

        # ---------- ETAPA 1 ----------
        if self.current_stage == 1:
            if self.bot.etap_1():
                self.current_stage = 2
                self.automation_ok.emit("✅ Etapa 1 completada")
            else:
                self._fail("Error en Etapa 1")

        # ---------- ETAPA 2 ----------
        elif self.current_stage == 2:
            if self.bot.etap_2(self.ubicaciones):
                self.current_stage = 3
                self.automation_ok.emit("✅ Etapa 2 completada")
            else:
                self._fail("Error en Etapa 2")

        # ---------- ETAPA 3 ----------
        elif self.current_stage == 3:
            if self.bot.etap_3(self.aseguradora, self.polizas_ubicacion, self.pago_ubicacion, self.excel_ubicacion, self.guardado_ubicacion):
                self.current_stage = 4
                self.automation_ok.emit("✅ Etapa 3 completada")
            else:
                self._fail("Error en Etapa 3")

        # ---------- ETAPA 4 ----------
        elif self.current_stage == 4:
            if self.bot.etap_4(self.aseguradora, self.polizas_ubicacion, self.pago_ubicacion, self.excel_ubicacion, self.guardado_ubicacion):
                self._reset_bot("🎉 Automatización finalizada")
            else:
                self._fail("Error en Etapa 3")

    # ==================================================
    # RESET / FAIL
    # ==================================================
    def _reset_bot(self, msg):
        try:
            if self.bot:
                self.bot.detener()
        except Exception:
            pass

        self.state = BotState.IDLE
        self.current_stage = 1
        self.bot = None
        self.automation_ok.emit(msg)
        self.ubicaciones = []
        
    def _fail(self, msg):
        self._reset_bot(f"❌ {msg}")

