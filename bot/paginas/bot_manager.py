# bot/paginas/bot_manager.py

from bot.config.urls import URL_HOME, ETAP_1, ETAP_2, ETAP_3, ETAP_4, ETAP_5, ETAP_6, URL_CONF
from bot.config.settings import TIMEOUT_1, TIMEOUT_2
from tools.proceso_dato import ProcesadorXLSX, BuscarPDFPoliza, Comprobante_pago

import unicodedata

from datetime import datetime
import os

class ManagerBot:
    def __init__(self, page):
        self.page = page


    def normalizar(self, texto: str) -> str:
        if not texto:
            return ""

        texto = texto.strip()
        texto = unicodedata.normalize("NFKD", texto)
        texto = texto.encode("ascii", "ignore").decode("ascii")
        return texto.lower()

    def subir_comprobante(self, pago_ubicacion):
        contenedor = self.page.locator(
            'div.space-y-2:has(label:text-is("Comprobante de pago (Opcional)"))'
        )

        # 🔹 Si ya hay archivo, click en X para eliminarlo
        btn_remove = contenedor.locator('button:has(svg.lucide-x)')
        if btn_remove.count() > 0:
            print("♻ Eliminando archivo previo de comprobante...")
            btn_remove.first.click()
            self.page.wait_for_timeout(800)  # espera que React limpie el input

        # 🔹 Subir el archivo
        ruta_archivo = Comprobante_pago(pago_ubicacion).buscar()[0]
        input_file = contenedor.locator('input[name="insurancePaymentFile"]')
        print(f"⬆ Subiendo comprobante {os.path.basename(ruta_archivo)}")
        input_file.set_input_files(ruta_archivo)

    def subir_poliza(self, polizas_ubicacio):
        # Localizar el contenedor de Póliza
        contenedor = self.page.locator(
            'div.space-y-2:has(label:text-is("Póliza"))'
        )

        # 🔹 Si ya hay archivo subido, hacer click en la X para eliminarlo
        btn_remove = contenedor.locator('button:has(svg.lucide-x)')
        if btn_remove.count() > 0:
            print("♻ Eliminando archivo previo de póliza...")
            btn_remove.first.click()
            self.page.wait_for_timeout(800)  # esperar que se limpie el input

        # 🔹 Subir el archivo
        ruta_archivo = BuscarPDFPoliza(polizas_ubicacio).buscar()[0]
        input_file = contenedor.locator('input[name="insuranceFile"]')
        print(f"⬆ Subiendo póliza {os.path.basename(ruta_archivo)}")
        input_file.set_input_files(ruta_archivo)



    # ===============================
    # STOP
    # ===============================
    def detener(self):
        try:
            self.page.goto(URL_HOME)
            print("🛑 Bot detenido")
        except Exception as e:
            print("❌ Error al detener:", e)

    # ===============================
    # ETAPA 1
    # ===============================
    def etap_1(self):
        try:
            self.page.goto(ETAP_1)

            particular_div = self.page.wait_for_selector(
                'text="Subí tu Cobertura Particular"',
                timeout=TIMEOUT_1,
                state='visible'
            )
            particular_div.click()

            self.page.wait_for_timeout(500)

            continuar_btn = self.page.wait_for_selector(
                'text="Continuar con Cobertura Particular"',
                timeout=TIMEOUT_1,
                state='visible'
            )
            continuar_btn.click()

            self.page.wait_for_timeout(500)

            if self.page.url.startswith(ETAP_2):
                print("✅ Etapa 1 completada")
                return True

            return False

        except Exception as e:
            print("❌ Error en Etapa 1:", e)
            return False

    # ===============================
    # ETAPA 2
    # ===============================
    def etap_2(self, ls_ubicaciones):
        print("etapa 2")
        print(ls_ubicaciones)

        try:
            if not self.page.url.startswith(ETAP_2):
                return False

            combobox_btn = self.page.wait_for_selector(
                'button[role="combobox"]',
                timeout=TIMEOUT_2,
                state='visible'
            )
            # combobox_btn.click()
            for ubicacion in ls_ubicaciones:
                try:
                    combobox_btn.click()

                    self.page.wait_for_timeout(500)
                    # opcion = self.page.get_by_text(ubicacion, exact=True).locator("..")
                    # opcion.click()
                    opcion = self.page.wait_for_selector(
                        # f'div.relative.flex.cursor-pointer:has-text("{ubicacion}")',
                        f'span:text-is("{ubicacion}")',
                        timeout=TIMEOUT_2,
                        state='visible'
                    )
                    self.page.wait_for_timeout(500)

                    opcion.click()
                    self.page.wait_for_timeout(500)
        
                    confirmar_btn = self.page.wait_for_selector(
                        'button:has-text("Confirmar selección")',
                    timeout=TIMEOUT_2
                    )
                    self.page.wait_for_timeout(500)

                    confirmar_btn.click()


                except Exception:
                    print(f"⚠ Ubicación no encontrada: {ubicacion}")

            # btn confirmar seleccionada 
            # self.page.wait_for_timeout(5000)
            #
            #
            # self.confirmar_btn.click()
            print("listo") 
            self.page.wait_for_timeout(500)

            siguiente_btn = self.page.wait_for_selector(
                'text="Siguiente"',
                timeout=TIMEOUT_2,
                state='visible'
            )
            siguiente_btn.click()


            self.page.wait_for_timeout(500)
            print("listo")
            if self.page.url.startswith(ETAP_3):
                print("✅ Etapa 2 completada")
                return True

            return False

        except Exception as e:
            print("❌ Error en Etapa 2:", e)
            return False

    # ===============================
    # ETAPA 3 (placeholder)
    # ===============================
    def etap_3(self, aseguradora, polizas_ubicacio, pago_ubicacion, excel_ubiacion, guardado_ubicacion ):
        try:
            if not self.page.url.startswith(ETAP_3):
                return False



            try:
                close_btn = self.page.get_by_role("button", name="Close")
                close_btn.wait_for(state="visible", timeout=1500)
                click_btn.click()
            except:
                print("no se clcik")
                pass  

            #
            # 1 parte selecion Aseguradora y la asegurador y click el btn combobox
            #

            label = self.page.get_by_text("Aseguradora", exact=True)

            combobox_btn = label.locator(
                'xpath=following::button[@aria-haspopup="dialog"][1]'
            )       

            combobox_btn.scroll_into_view_if_needed()
            self.page.wait_for_timeout(500)

            combobox_btn.click()
            self.page.wait_for_timeout(500)

            search_input = self.page.wait_for_selector(
                'input[placeholder="Buscar..."]',
                timeout=TIMEOUT_2,
                state="visible"
            )
            self.page.wait_for_timeout(500)

            search_input.fill("")
            self.page.wait_for_timeout(500)
            aseg = str(aseguradora[0])
            search_input.type(aseg, delay=80)



            self.page.wait_for_timeout(500)

            resultado = self.page.wait_for_selector(
                f'div[role="dialog"] div:has(span:text-is("{aseg}"))',
                timeout=TIMEOUT_2,
                state="visible"
            )
            resultado.click()
            
            #
            # procesaremos los datos 
            #
            procesador = ProcesadorXLSX(excel_ubiacion)
            datos = procesador.procesar()
            if datos:
                base = datos[0]
                idpropuesta = base["idpropuesta"]
                fecha_pago = base["fecha_pago"]
                fin_vigencia = base["fin_vigencia"]


            #
            # Inputo de fecha
            #
            input_poliza = self.page.wait_for_selector(
                'input[placeholder="Ingresa el número de póliza"]',
                timeout=TIMEOUT_2,
                state="visible"
            )

            input_poliza.click()
            input_poliza.fill("")              # por si trae algo 
            input_poliza.type(idpropuesta, delay=80)

            #
            # fechas
            #
            fecha_inicio = datetime.strptime(fecha_pago, "%d/%m/%Y").strftime("%Y-%m-%d")
            fecha_final = datetime.strptime(fin_vigencia, "%d/%m/%Y").strftime("%Y-%m-%d")

            input_fecha = self.page.wait_for_selector(
                'input[type="date"][name="startDate"]',
                timeout=TIMEOUT_2,
                state="visible"
            )
            input_fecha.fill(fecha_inicio)

            input_fecha_fin = self.page.wait_for_selector(
                'input[type="date"][name="endDate"]',
                timeout=TIMEOUT_2,
                state="visible"
            )

            input_fecha_fin.fill(fecha_final)



            # Subir póliza
            self.subir_poliza(polizas_ubicacio)
            # Subir comprobante
            self.subir_comprobante(pago_ubicacion)

            #
            # BTO FINALES
            #
            btn = self.page.wait_for_selector(
                'button[type="submit"]',
                state='visible',
                timeout=30000
            )
            btn.click()

            self.btn_continuar = self.page.get_by_role("button", name="Continuar")
            self.btn_continuar.wait_for(state="visible", timeout=30000)
            self.btn_continuar.scroll_into_view_if_needed()
            self.btn_continuar.click(force=True)
                       
            self.page.wait_for_timeout(1500)
            self.page.wait_for_load_state("networkidle")
            if self.page.url.startswith(ETAP_4):
                print("✅ Etapa 3 completada")
                return True

            return False

        except Exception as e:
            print("❌ Error en Etapa 3:", e)
            return False



    def etap_4(self, aseguradora, polizas_ubicacio, pago_ubicacion, excel_ubiacion, guardado_ubicacion ):
        try:
            if not self.page.url.startswith(ETAP_4):
                return False

            #
            # procesaremos los datos 
            #
            procesador = ProcesadorXLSX(excel_ubiacion)
            datos = procesador.procesar()
        
            
            ##
            for persona in datos:
                dni = str(persona["documento_asegurado"])
                print("Persona dni:",dni)
                btn_nuevo = self.page.wait_for_selector(
                    'button:has-text("Nuevo trabajador")',
                    state="visible",
                    timeout=30000
                )

                btn_nuevo.click()
                # 1️⃣ Input DNI
                self.page.wait_for_timeout(500)

                input_dni = self.page.wait_for_selector(
                    'input[name="dni"]',
                    state="visible",
                    timeout=30000
                )
                input_dni.click()
                self.page.wait_for_timeout(500)

                input_dni.fill("")          # limpia por las dudas
                self.page.wait_for_timeout(500)

                input_dni.type(dni, delay=80)

                # 2️⃣ Click en Buscar
                btn_buscar = self.page.get_by_role("button", name="Buscar")
                btn_buscar.wait_for(state="visible", timeout=50000)
                btn_buscar.click()
                self.page.wait_for_timeout(1500)
 
                #
                # fila = self.page.wait_for_selector(
                #     f'tbody tr:has(td:text-is("{dni}"))',
                #     timeout=15000,
                #     state="visible"
                # )

            btn_siguiente = self.page.get_by_role("button", name="Siguiente")
            btn_siguiente.wait_for(state="visible", timeout=10000)
            btn_siguiente.click()


            return True

        except Exception as e:
            print("❌ Error en Etapa 4:", e)
            return False


    # ===============================
    # ETAPA 5
    # ===============================
    def etap_5(self):
        try:
            self.page.goto(ETAP_5)
            # Click en Siguiente
            btn = self.page.get_by_role("button", name="Siguiente")
            btn.wait_for(state="visible", timeout=10000)
            btn.click()

            # Esperar que aparezca Confirmar
            btn_confirmar = self.page.get_by_role("button", name="Confirmar")
            btn_confirmar.wait_for(state="visible", timeout=10000)

            # Click en Confirmar
            btn_confirmar.click()
            
            self.page.wait_for_url(f"{ETAP_6}*", timeout=15000)
            if self.page.url.startswith(ETAP_6):
                print("✅ Etapa 5 completada")
                return True
        

        except Exception as e:
            print("❌ Error en Etapa 5:", e)
            return False



    # ===============================
    # ETAPA 6 y Caputo
    # ===============================
    def etap_6(self, excel_ubiacion,guardado_ubicacion):
        try:
                        
            procesador = ProcesadorXLSX(excel_ubiacion)
            datos = procesador.procesar()
            # print(datos)
            # Esperar hasta que la página esté en ETAP_6 (procesando)
            self.page.wait_for_url(f"{ETAP_6}*", timeout=60000)  # espera hasta 60s

            # Asegurarse que la página termine de cargar
            self.page.wait_for_load_state("networkidle", timeout=60000)

            print("✅ ETAP_6 cargada correctamente, redirigiendo a configuración...")

            # Ir a la página final
            self.page.goto(URL_CONF)
            self.page.wait_for_load_state("networkidle", timeout=60000)
            print("✅ Página de configuración cargada. Esperando input de 'Número de póliza'...")


            # Esperar el input de "Número de póliza"
            input_poliza = self.page.wait_for_selector(
                'input[placeholder="Número de póliza"]',
                timeout=6000,
                state="visible"
            )

            # Tomar la primera propuesta y extraer solo números de 'idpropuesta'
            idpropuesta = datos[0]["idpropuesta"]  # ejemplo: 'CA5965'
            id_numeros = "".join([c for c in idpropuesta if c.isdigit()])  # '5965'

            # 6️⃣Rellenar el input
            input_poliza.click()
            input_poliza.fill("")  # limpiar por si tiene valor
            input_poliza.type(id_numeros, delay=80)
            self.page.wait_for_timeout(6000)  # 60000 ms = 6 segundos
           

            # 🔹 Asegurar que el directorio de guardado exista
            if not os.path.exists(guardado_ubicacion):
                os.makedirs(guardado_ubicacion)

            # 🔹 Tomar captura de pantalla del contenedor
            contenedor = self.page.wait_for_selector(
                'div.space-y-4',  # contenedor raíz de la tabla
                timeout=6000  # hasta 60 segundos
            )

            ruta_captura = os.path.join(guardado_ubicacion, f"poliza_{id_numeros}.png")
            contenedor.screenshot(path=ruta_captura)
            print(f"✅ Input 'Número de póliza' completado con: {id_numeros}")
            return True

        except Exception as e:
            print("❌ Error en Etapa 6:", e)
            return False


