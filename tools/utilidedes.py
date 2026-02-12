import os
import re

def cargar_aseguradoras(path="aseguradoras.txt"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    aseguradoras = []

    with open(path, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()

            if not linea:
                continue
            if linea.lower().startswith(("lista completa", "total", "nota")):
                continue

            match = re.match(r"^\d+\.\s+(.*)$", linea)
            if match:
                aseguradoras.append(match.group(1).strip())

    return aseguradoras

