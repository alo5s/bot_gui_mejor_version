# bot/paginas/bot_manager.py

from bot.config.urls import URL_HOME, ETAP_1, ETAP_2, ETAP_3, ETAP_4, ETAP_5, ETAP_6, URL_CONF
from bot.config.settings import TIMEOUT_1, TIMEOUT_2
from tools.proceso_dato import ProcesadorXLSX, BuscarPDFPoliza, Comprobante_pago

import unicodedata
from datetime import datetime
import os
from playwright.sync_api import expect


import time
class ManagerBot:
    def __init__(self, page):
        self.page = page
        self.page.set_default_timeout(30000)
        self.page.set_default_navigation_timeout(60000)

    # ===============================
    # UTIL
    # ===============================
    def normalizar(self, texto: str) -> str:
        if not texto:
            return ""
        texto = texto.strip()
        texto = unicodedata.normalize("NFKD", texto)
        texto = texto.encode("ascii", "ignore").decode("ascii")
        return texto.lower()

    # ===============================
    # SUBIDAS
    # ===============================
    def subir_comprobante(self, pago_ubicacion):
        # Si no mandan ubicación → no hacemos nada
        if not pago_ubicacion:
            return

        archivos = Comprobante_pago(pago_ubicacion).buscar()

        # Si no encontró archivo → no hacemos nada
        if not archivos:
            print("⚠ No se encontró comprobante, se continúa sin subir archivo")
            return

        contenedor = self.page.locator(
            'div.space-y-2:has(label:text-is("Comprobante de pago (Opcional)"))'
        )

        btn_remove = contenedor.locator('button:has(svg.lucide-x)')
        if btn_remove.count() > 0:
            btn_remove.first.click()

        ruta = archivos[0]
        contenedor.locator('input[name="insurancePaymentFile"]').set_input_files(ruta)

    def subir_poliza(self, polizas_ubicacion):
        contenedor = self.page.locator(
            'div.space-y-2:has(label:text-is("Póliza"))'
        )

        btn_remove = contenedor.locator('button:has(svg.lucide-x)')
        if btn_remove.count() > 0:
            btn_remove.first.click()

        ruta = BuscarPDFPoliza(polizas_ubicacion).buscar()[0]
        contenedor.locator('input[name="insuranceFile"]').set_input_files(ruta)

    # ===============================
    # STOP
    # ===============================
    def detener(self):
        try:
            self.page.goto(URL_HOME, wait_until="domcontentloaded")
        except:
            pass

    # ===============================
    # ETAPA 1
    # ===============================
    def etap_1(self):
        try:
            self.page.goto(ETAP_1, wait_until="domcontentloaded")

            self.page.get_by_text(
                "Subí tu Cobertura Particular", exact=True
            ).click()

            self.page.get_by_text(
                "Continuar con Cobertura Particular", exact=True
            ).click()

            self.page.wait_for_url(f"{ETAP_2}*", timeout=8000)
            return True

        except Exception as e:
            print("❌ Etapa 1:", e)
            return False

    # ===============================
    # ETAPA 2
    # ===============================
    def etap_2(self, ls_ubicaciones):
        try:
            if not self.page.url.startswith(ETAP_2):
                return False

            combobox = self.page.locator('button[role="combobox"]')

            for ubicacion in ls_ubicaciones:
                try:
                    combobox.click()

                    opcion = self.page.locator(
                        f'span:text-is("{ubicacion}")'
                    )
                    opcion.click()

                    self.page.get_by_role(
                        "button", name="Confirmar selección"
                    ).click()

                except:
                    print(f"⚠ Ubicación no encontrada: {ubicacion}")
                    return False

            self.page.get_by_text("Siguiente", exact=True).click()
            self.page.wait_for_url(f"{ETAP_3}*", timeout=8000)

            return True

        except Exception as e:
            print("❌ Etapa 2:", e)
            return False

    # ===============================
    # ETAPA 3
    # ===============================
    def etap_3(self, aseguradora, polizas_ubicacion,
               pago_ubicacion, excel_ubicacion, guardado_ubicacion):
            
        print("DEBUG ETAPA 3")
        print("aseguradora:", aseguradora)
        print("polizas_ubicacion:", polizas_ubicacion)
        print("pago_ubicacion:", pago_ubicacion)
        print("excel_ubicacion:", excel_ubicacion)
        print("guardado_ubicacion:", guardado_ubicacion)

        try:
            if not self.page.url.startswith(ETAP_3):
                return False

            # Aseguradora
            label = self.page.get_by_text("Aseguradora", exact=True)
            combobox = label.locator(
                'xpath=following::button[@aria-haspopup="dialog"][1]'
            )
            combobox.click()

            search_input = self.page.locator(
                'input[placeholder="Buscar..."]'
            )
            aseg = str(aseguradora[0])
            search_input.fill(aseg)

            self.page.locator(
                f'div[role="dialog"] span:text-is("{aseg}")'
            ).click()

            # Datos Excel
            datos = ProcesadorXLSX(excel_ubicacion).procesar()
            base = datos[0]

            idpropuesta = base["idpropuesta"]
            fecha_pago = base["fecha_pago"]
            fin_vigencia = base["fin_vigencia"]

            self.page.locator(
                'input[placeholder="Ingresa el número de póliza"]'
            ).fill(idpropuesta)

            fecha_inicio = datetime.strptime(
                fecha_pago, "%d/%m/%Y"
            ).strftime("%Y-%m-%d")

            fecha_final = datetime.strptime(
                fin_vigencia, "%d/%m/%Y"
            ).strftime("%Y-%m-%d")

            self.page.locator(
                'input[name="startDate"]'
            ).fill(fecha_inicio)

            self.page.locator(
                'input[name="endDate"]'
            ).fill(fecha_final)

            self.subir_comprobante(pago_ubicacion)  # opcional
            self.subir_poliza(polizas_ubicacion)    # obligatorio

            # Esperar que el botón Siguiente esté habilitado
            btn_siguiente = self.page.locator('button[type="submit"]')
            expect(btn_siguiente).to_be_enabled(timeout=120000)
            btn_siguiente.click()



            self.page.get_by_role("button", name="Continuar").click()

            self.page.wait_for_url(f"{ETAP_4}*", timeout=10000)
            return True

        except Exception as e:
            print("❌ Etapa 3:", e)
            return False

    # ===============================
    # ETAPA 4
    # ===============================
    def etap_4(self, aseguradora, polizas_ubicacion,
               pago_ubicacion, excel_ubicacion, guardado_ubicacion):

        try:
            if not self.page.url.startswith(ETAP_4):
                return False

            datos = ProcesadorXLSX(excel_ubicacion).procesar()

            for persona in datos:
                dni = str(persona["documento_asegurado"])
                idpropuesta = persona["idpropuesta"]
                nombre = persona["asegurado"]

                self.page.get_by_role(
                    "button", name="Nuevo trabajador"
                ).click()

                self.page.locator('input[name="dni"]').fill(dni)

                self.page.get_by_role(
                    "button", name="Buscar"
                ).click()
                try:
                    # Espera máximo 5 segundos a que aparezca cualquiera de los dos
                    self.page.wait_for_selector(
                        "h2:has-text('Persona encontrada'), h2:has-text('Persona no encontrada')",
                        timeout=3000
                    )
                    print("⛔ Resultado detectado, deteniendo bot:", dni)
                    return {
                        "dni": dni,
                        "poliza": idpropuesta,
                        "asegurado": nombre
                    }

                except:
                    pass


            self.page.get_by_role(
                "button", name="Siguiente"
            ).click()
            
            self.page.wait_for_url(f"{ETAP_5}*", timeout=10000)
            return True

        except Exception as e:
            print("❌ Etapa 4:", e)
            return False

    # ===============================
    # ETAPA 5
    # ===============================
    def etap_5(self):
        try:
            # NO hacemos goto innecesario
            btn = self.page.get_by_role("button", name="Siguiente")
            # btn.wait_for(state="visible", timeout=30000)
            # expect(btn).to_be_enabled(timeout=30000)
            btn.click()
            
            # Esperar que aparezca Confirmar
            btn_confirmar = self.page.get_by_role("button", name="Confirmar")
            btn_confirmar.wait_for(state="visible", timeout=10000)
            btn_confirmar.click()

            self.page.wait_for_url(f"{ETAP_6}*", timeout=10000)
            return True

        except Exception as e:
            print("❌ Etapa 5:", e)
            return False

    # ===============================
    # ETAPA 6
    # ===============================
    def etap_6(self, excel_ubicacion, guardado_ubicacion):
        try:
            datos = ProcesadorXLSX(excel_ubicacion).procesar()

            self.page.wait_for_url(f"{ETAP_6}*", timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)

            self.page.goto(URL_CONF, wait_until="domcontentloaded")
            self.page.wait_for_load_state("networkidle", timeout=30000)

            input_poliza = self.page.locator('input[placeholder="Número de póliza"]')
            input_poliza.wait_for(state="visible", timeout=30000)

            idpropuesta = datos[0]["idpropuesta"]
            id_numeros = "".join(c for c in idpropuesta if c.isdigit())

            input_poliza.fill(id_numeros)
            self.page.wait_for_timeout(6000)  # 60000 ms = 6 segundos

            if not os.path.exists(guardado_ubicacion):
                os.makedirs(guardado_ubicacion)

            contenedor = self.page.locator("div.space-y-4")
            # contenedor = self.page.wait_for_selector(
            #     'div.space-y-4',  # contenedor raíz de la tabla
            #     timeout=1000  # hasta 60 segundos
            # )

            ruta = os.path.join(
                guardado_ubicacion,
                f"poliza_{id_numeros}.png"
            )

            contenedor.screenshot(path=ruta)

            return True

        except Exception as e:
            print("❌ Etapa 6:", e)
            return False

