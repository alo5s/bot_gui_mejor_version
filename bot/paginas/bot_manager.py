# bot/paginas/bot_manager.py

from bot.config.urls import URL_HOME, ETAP_1, ETAP_2, ETAP_3, ETAP_4
from bot.config.settings import TIMEOUT_1, TIMEOUT_2
from tools.proceso_dato import ProcesadorXLSX, BuscarPDFPoliza

from datetime import datetime
import os

class ManagerBot:
    def __init__(self, page):
        self.page = page

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

                    print(f"✅ Ubicación seleccionada: {ubicacion}")

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
        print("etapa 3")
        print("Aseguradora:", aseguradora)
        print("DEBUG aseguradora:", aseguradora, type(aseguradora))

        print("Ubicacion:", polizas_ubicacio, pago_ubicacion, excel_ubiacion, guardado_ubicacion)
        try:
            if not self.page.url.startswith(ETAP_3):
                return False


            print("Listo etap 3 confirmadada")

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
                print(idpropuesta, fecha_pago, fin_vigencia)


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
            
            #
            #  Subida de Poliza 
            #
            buscador = BuscarPDFPoliza(polizas_ubicacio) 
            pdfs = buscador.buscar()
            print(pdfs[0])

            nombre_pdf = os.path.basename(pdfs[0])

            if self.page.locator(f'text="{nombre_pdf}"').count() > 0:
                print("📎 PDF ya presente")
            else:
                self.page.set_input_files(
                'input[type="file"][name="insuranceFile"]',
                pdfs[0]
            )


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
        print("etapa 4")
        print("Ubicacion:", polizas_ubicacio, pago_ubicacion, excel_ubiacion, guardado_ubicacion)
        try:
            if not self.page.url.startswith(ETAP_4):
                return False

            #
            # procesaremos los datos 
            #
            procesador = ProcesadorXLSX(excel_ubiacion)
            datos = procesador.procesar()
            print(datos)
        
            
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
                btn_buscar.wait_for(state="visible", timeout=30000)
                btn_buscar.click()
                self.page.wait_for_timeout(1500)
 
                #
                # fila = self.page.wait_for_selector(
                #     f'tbody tr:has(td:text-is("{dni}"))',
                #     timeout=15000,
                #     state="visible"
                # )


            self.page.wait_for_timeout(1000000)

            return True

        except Exception as e:
            print("❌ Error en Etapa 3:", e)
            return False

