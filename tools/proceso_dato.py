# tools/proceso_dato.py

import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ProcesadorXLSX:
    def __init__(self, directorio: str):
        self.directorio = Path(directorio)
        self.archivo_xlsx = self._buscar_xlsx()

    # -----------------------------------------
    # Buscar archivo XLSX
    # -----------------------------------------
    def _buscar_xlsx(self) -> Path:
        archivos = list(self.directorio.glob("*.xlsx"))
        if not archivos:
            raise FileNotFoundError("No se encontró ningún archivo .xlsx")
        return archivos[0]

    # -----------------------------------------
    # Cargar Excel
    # -----------------------------------------
    def _cargar_excel(self) -> pd.DataFrame:
        return pd.read_excel(self.archivo_xlsx)

    # -----------------------------------------
    # Procesar datos
    # -----------------------------------------
    def procesar(self) -> list[dict]:
        df = self._cargar_excel()
        resultados = []

        for _, fila in df.iterrows():
            fecha = pd.to_datetime(fila["fecha"], dayfirst=True)
            meses = int(fila["meses"])

            resultados.append({
                "idpropuesta": fila["idpropuesta"],
                "fecha_pago": fecha.strftime("%d/%m/%Y"),
                "fin_vigencia": (fecha + relativedelta(months=meses)).strftime("%d/%m/%Y"),
                "asegurado": fila["asegurado(a)"],
                "documento_asegurado": fila["Documento asegurado(a)"],
            })

        return resultados

class BuscarPDFPoliza:
    def __init__(self, directorio: str):
        self.directorio = Path(directorio)

    def buscar(self) -> list[str]:
        if not self.directorio.exists():
            raise FileNotFoundError("El directorio no existe")

        pdfs = list(self.directorio.glob("*.pdf"))

        if not pdfs:
            raise FileNotFoundError("No se encontró ningún archivo PDF")

        # Devuelve rutas completas en string
        return [str(pdf.resolve()) for pdf in pdfs]



class Comprobante_pago:
    def __init__(self, directorio: str | None):
        if not directorio:
            self.directorio = None
        else:
            self.directorio = Path(directorio)

    def buscar(self) -> list[str]:
        if not self.directorio:
            return []

        if not self.directorio.exists():
            print("⚠ Directorio de pago no existe:", self.directorio)
            return []

        archivos = []
        for extension in ("*.pdf", "*.jpg"):
            archivos.extend(self.directorio.glob(extension))

        return [str(archivo.resolve()) for archivo in archivos]

