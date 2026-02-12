# ==============================
# UI THEME CONFIG
# ==============================

class UISettings:
    COLORS = {
        "background": "#f2f4f8",
        "white": "#ffffff",
        "border": "#e0e0e0",
        "primary": "#4a90e2",
        "primary_hover": "#357ABD",
        "danger": "#e74c3c",
        "danger_hover": "#c0392b",
        "text": "#333333",
        "text_muted": "#777777",
    }

    FONTS = {
        "header_size": "16px",
        "title_size": "20px",
        "normal": "13px",
    }


# ==============================
# LOGIN STYLE
# ==============================

LOGIN_STYLE = """
#login_widget {
    background-color: #f2f4f8;
}
#login_card {
    background-color: white;
    border-radius: 12px;
    min-width: 360px;
    max-width: 360px;
    border: 1px solid #e0e0e0;
}
#login_title {
    font-size: 22px;
    font-weight: bold;
}
#login_input {
    padding: 10px;
    border-radius: 6px;
    border: 1px solid #ccc;
    font-size: 14px;
}
#login_button {
    background-color: #4a90e2;
    color: white;
    padding: 10px;
    border-radius: 6px;
    font-size: 15px;
    font-weight: bold;
}
#login_error {
    color: red;
    font-size: 12px;
}

#remember {
    color: black;
    padding: 10px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: bold;
}
"""


# ==============================
# APP STYLE
# ==============================

APP_STYLE = f"""
#app_widget {{
    background-color: {UISettings.COLORS['background']};
}}

#app_header {{
    background-color: {UISettings.COLORS['white']};
    border-radius: 10px;
    border: 1px solid {UISettings.COLORS['border']};
}}

#user_label {{
    font-weight: bold;
    font-size: {UISettings.FONTS['header_size']};
}}

#status_label {{
    font-weight: bold;
    color: {UISettings.COLORS['primary']};
}}

#control_card, #paths_card, #logs_card {{
    background-color: {UISettings.COLORS['white']};
    border-radius: 12px;
    border: 1px solid {UISettings.COLORS['border']};
}}

QPushButton {{
    padding: 8px 14px;
    border-radius: 6px;
    border: 1px solid #ccc;
    background: #f8f9fb;
    font-weight: 600;
}}

QPushButton:hover {{
    background: #e9edf5;
}}


QComboBox {{
    padding: 8px 14px;
    border-radius: 6px;
    border: 1px solid #ccc;
    background: #f8f9fb;
}}
QComboBox::drop-down {{
    border: none;
    width: 0px;
}}

QComboBox::down-arrow {{
    width: 0px;
    height: 0px;
}}
QAbstractItemView {{
    background-color: #ffffff;

}}



#logout_btn {{
    background: {UISettings.COLORS['danger']};
    color: {UISettings.COLORS['white']};
    border: none;
}}

#logout_btn:hover {{
    background: {UISettings.COLORS['danger_hover']};
}}

#path_title {{
    font-weight: bold;
}}

#path_label {{
    color: {UISettings.COLORS['text_muted']};
}}

#path_btn {{
    background: {UISettings.COLORS['primary']};
    color: {UISettings.COLORS['white']};
    border: none;
}}

#path_btn:hover {{
    background: {UISettings.COLORS['primary_hover']};
}}

#logs_title {{
    font-weight: bold;
    font-size: {UISettings.FONTS['header_size']};
}}

#logs_box {{
    border-radius: 6px;
    border: 1px solid #ddd;
    background: #fcfcfc;
}}

#btn_logs {{
    background: {UISettings.COLORS['primary']};
    color: {UISettings.COLORS['white']};
    border: none;
}}
"""


# ==============================
# COMPONENTS STYLE
# ==============================

COMPONENTS_STYLE = f"""
QWidget {{
    font-family: 'Segoe UI', Arial, sans-serif;
}}

QPushButton:disabled {{
    background: #e0e0e0;
    color: #999;
}}

QLineEdit {{
    padding: 8px;
    border: 1px solid {UISettings.COLORS['border']};
    border-radius: 4px;
    background: {UISettings.COLORS['white']};
}}

QLineEdit:focus {{
    border: 2px solid {UISettings.COLORS['primary']};
}}

QLabel {{
    color: {UISettings.COLORS['text']};
}}

.card {{
    background-color: {UISettings.COLORS['white']};
    border-radius: 8px;
    border: 1px solid {UISettings.COLORS['border']};
}}

.status-running {{
    color: #27ae60;
    font-weight: bold;
}}

.status-paused {{
    color: #f39c12;
    font-weight: bold;
}}

.status-stopped {{
    color: #e74c3c;
    font-weight: bold;
}}
"""


# ==============================
# EXPORT
# ==============================

def get_combined_styles() -> str:
    """Retorna todos los estilos combinados"""
    return LOGIN_STYLE + "\n" + APP_STYLE + "\n" + COMPONENTS_STYLE


