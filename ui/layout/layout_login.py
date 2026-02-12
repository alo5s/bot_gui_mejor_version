# ui/layout/layout_login.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox

from PySide6.QtCore import Qt, Signal, QSettings
from .styles import LOGIN_STYLE, get_combined_styles


class LoginView(QWidget):

    login_requested = Signal(str, str)   # usuario, password

    def __init__(self):
        super().__init__()

        self.settings = QSettings("BotRPA", "Login")

        self.setObjectName("login_widget")

        wrapper = QVBoxLayout()
        wrapper.setAlignment(Qt.AlignCenter)

        card = QWidget()
        card.setObjectName("login_card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 40, 40, 40)

        self.title = QLabel("Iniciar sesión")
        self.title.setObjectName("login_title")
        self.title.setAlignment(Qt.AlignCenter)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuario")
        self.user_input.setObjectName("login_input")

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setObjectName("login_input")

        self.error = QLabel("")
        self.error.setObjectName("login_error")
        self.error.setAlignment(Qt.AlignCenter)


        self.remember = QCheckBox("Recordarme")
        self.remember.setObjectName("remember")

        # Wrapper para centrar el checkbox
        remember_wrapper = QWidget()
        hlayout = QHBoxLayout(remember_wrapper)
        hlayout.addWidget(self.remember)
        hlayout.setAlignment(Qt.AlignCenter)
        hlayout.setContentsMargins(0, 0, 0, 0)


        self.btn = QPushButton("Ingresar")
        self.btn.setObjectName("login_button")
        self.btn.clicked.connect(self.on_login)

        layout.addWidget(self.title)
        layout.addWidget(self.user_input)
        layout.addWidget(self.pass_input)
        layout.addWidget(self.error)
        layout.addWidget(remember_wrapper)
        layout.addWidget(self.btn)

        wrapper.addWidget(card)
        self.setLayout(wrapper)
        self.setStyleSheet(get_combined_styles())

        # Cargar valores guardados
        self.user_input.setText(self.settings.value("username", ""))
        self.pass_input.setText(self.settings.value("password", ""))
        self.remember.setChecked(self.settings.value("remember", False, type=bool))
    
    def on_login(self):
        usuario = self.user_input.text().strip()
        password = self.pass_input.text().strip()

        if not usuario or not password:
            self.error.setText("⚠️ Complete usuario y contraseña")
            return

        self.error.setText("")
       
        # 💾 Guardar
        self.settings.setValue("remember", self.remember.isChecked())
        if self.remember.isChecked():
            self.settings.setValue("username", usuario)
            self.settings.setValue("password", password)
        else:
            self.settings.clear()

        # 🔒 Bloquear UI
        self.btn.setEnabled(False)
        self.btn.setText("⏳ Espere...")
        
        self.login_requested.emit(usuario, password)

    def show_error(self, msg: str):
        self.error.setText(msg)
        print(msg)
    def reset(self):
        self.btn.setEnabled(True)
        self.btn.setText("Ingresar")
