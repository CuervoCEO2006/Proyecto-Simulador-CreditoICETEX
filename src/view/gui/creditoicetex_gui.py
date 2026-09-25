import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout

from model import logica_credito

COLOR_FONDO = (0.95, 0.96, 0.98, 1)
COLOR_TEXTO = (0.15, 0.15, 0.2, 1)
COLOR_EXITO = '2e7d32'
COLOR_ERROR = 'c62828'

class CreditoICETEXApp(App):
    def build(self):
        self.title = 'Simulador de Credito Educativo'

        Window.clearcolor = COLOR_FONDO
        Window.softinput_mode = 'below_target'
        raiz = BoxLayout(orientation='vertical',padding=[20, 15],spacing=10)

        # Scroll para pantallas pequeñas
        scroll = ScrollView(do_scroll_x=False,do_scroll_y=True)
        self.scroll = scroll

        # Contenido interno del ScrollView
        contenido = BoxLayout(orientation='vertical',spacing=15,padding=[5, 5],size_hint_y=None)
        contenido.bind(minimum_height=contenido.setter('height'))

        titulo = Label(
            text='Simulador de Credito Educativo',
            font_size='22sp',
            bold=True,
            color=COLOR_TEXTO,
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=60
        )
        contenido.add_widget(titulo)

        label_monto = self._crear_label('Monto del credito')
        contenido.add_widget(label_monto)

        self.monto_credito = TextInput(
            hint_text='Ej: 10000000',
            multiline=False,
            input_filter='float',
            font_size='16sp',
            size_hint_y=None,
            height=55,
            padding=[10, 10]
        )

        self.monto_credito.bind(
            focus=self._cuando_enfoca
        )
        contenido.add_widget(self.monto_credito)

        label_tasa = self._crear_label('Tasa de interes mensual (%)')
        contenido.add_widget(label_tasa)

        self.tasa_interes = TextInput(
            hint_text='Ej: 1.5',
            multiline=False,
            input_filter='float',
            font_size='16sp',
            size_hint_y=None,
            height=55,
            padding=[10, 10]
        )

        self.tasa_interes.bind(
            focus=self._cuando_enfoca
        )

        contenido.add_widget(self.tasa_interes)

        label_cuotas = self._crear_label('Numero de cuotas')

        contenido.add_widget(label_cuotas)
        self.cantidad_cuotas = TextInput(
            hint_text='Ej: 24',
            multiline=False,
            input_filter='int',
            font_size='16sp',
            size_hint_y=None,
            height=55,
            padding=[10, 10]
        )

        self.cantidad_cuotas.bind(
            focus=self._cuando_enfoca
        )

        contenido.add_widget(self.cantidad_cuotas)

        botones = BoxLayout(orientation='horizontal',spacing=10,size_hint_y=None,height=55)
        boton_calcular = Button(text='Calcular',bold=True,font_size='16sp')
        boton_calcular.bind(on_press=self.calcular)
        botones.add_widget(boton_calcular)
        boton_tabla = Button(text='Ver Tabla',font_size='16sp')
        boton_tabla.bind(on_press=self.mostrar_tabla_amortizacion)
        botones.add_widget(boton_tabla)
        boton_limpiar = Button(text='Limpiar',font_size='16sp')

        boton_limpiar.bind(on_press=self.limpiar)
        botones.add_widget(boton_limpiar)
        contenido.add_widget(botones)

        self.resultado = Label(
            text='Aqui apareceran los resultados',
            markup=True,
            font_size='16sp',
            color=COLOR_TEXTO,
            halign='left',
            valign='top',
            size_hint_y=None,
            padding=[10, 10]
        )

        self.resultado.bind(width=self._actualizar_ancho_resultado)

        self.resultado.bind(texture_size=self._actualizar_alto_resultado)
        contenido.add_widget(self.resultado)

        scroll.add_widget(contenido)

        raiz.add_widget(scroll)
        return raiz

    def _crear_label(self, texto):
        return Label(
            text=texto,
            color=COLOR_TEXTO,
            font_size='15sp',
            halign='left',
            valign='middle',
            size_hint_y=None,
            height=30
        )

    def _cuando_enfoca(self, widget, tiene_foco):
        if tiene_foco:
            Clock.schedule_once(
                lambda dt: self.scroll.scroll_to(
                    widget,
                    padding=20
                ),
                0.2
            )

    def _actualizar_ancho_resultado(self, sender, width):
        sender.text_size = (width - 20, None)

    def _actualizar_alto_resultado(self, sender, texture_size):
        sender.height = max(80,texture_size[1] + 20)

    def limpiar(self, sender):
        self.monto_credito.text = ''
        self.tasa_interes.text = ''
        self.cantidad_cuotas.text = ''
        self.resultado.text = ('Aqui apareceran los resultados')


    def calcular(self, sender):
        try:
            (monto_credito,tasa_interes_mensual,cantidad_cuotas) = self._leer_datos_formulario()
        except ValueError:
            self._mostrar_error(
                'Por favor complete los tres campos '
                'con numeros validos.')

            return
        try:
            (cuota,total_pagado,total_intereses) = self._calcular_resultados(monto_credito,tasa_interes_mensual,cantidad_cuotas)

            texto_resultado = (
                self._construir_texto_resultado(
                    cuota,
                    total_pagado,
                    total_intereses
                )
            )

            self._mostrar_exito(texto_resultado)

        except logica_credito.MontoInvalido:
            self._mostrar_error('El monto del credito debe ser mayor que cero.')

        except logica_credito.TasaInvalida:
            self._mostrar_error('La tasa de interes no puede ser negativa.')

        except logica_credito.PlazoInvalido:
            self._mostrar_error('El numero de cuotas debe ser al menos 1.')

        except Exception:
            self._mostrar_error(
                'No se pudo calcular la cuota. '
                'Verifique los datos ingresados.'
            )

    def _mostrar_exito(self, texto):
        self.resultado.text = (
            f'[color={COLOR_EXITO}]{texto}[/color]')

    def _mostrar_error(self, mensaje):
        self.resultado.text = (
            f'[color={COLOR_ERROR}]{mensaje}[/color]')

    def _leer_datos_formulario(self):
        monto_credito = float(self.monto_credito.text)
        tasa_interes_mensual = float(self.tasa_interes.text) / 100
        cantidad_cuotas = int(self.cantidad_cuotas.text)

        return (
            monto_credito,
            tasa_interes_mensual,
            cantidad_cuotas
        )

    def _calcular_resultados(self,monto_credito,tasa_interes_mensual,cantidad_cuotas):
        cuota = round(logica_credito.calcular_cuota(monto_credito,tasa_interes_mensual,cantidad_cuotas),2)
        total_pagado = round(logica_credito.calcular_total_pagado(monto_credito,tasa_interes_mensual,cantidad_cuotas),2)
        total_intereses = round(logica_credito.calcular_total_intereses(monto_credito,tasa_interes_mensual,cantidad_cuotas),2)

        return (
            cuota,
            total_pagado,
            total_intereses
        )

    def _construir_texto_resultado(self,cuota,total_pagado,total_intereses):
        return (
            f'Cuota mensual: $ {cuota:,.2f}\n'
            f'Total pagado: $ {total_pagado:,.2f}\n'
            f'Total intereses: $ {total_intereses:,.2f}'
        )

    def mostrar_tabla_amortizacion(self, sender):
        # 1. Leer y validar los datos del formulario
        try:
            (monto_credito, tasa_interes_mensual, cantidad_cuotas) = self._leer_datos_formulario()
            cuota_mensual = logica_credito.calcular_cuota(monto_credito, tasa_interes_mensual, cantidad_cuotas)
        except ValueError:
            self._mostrar_error('Por favor complete los tres campos con numeros validos.')
            return
        except Exception as e:
            self._mostrar_error(str(e))
            return

        # 2. Construir el contenido del popup
        contenido = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Color claro para que se vea sobre el fondo oscuro del popup
        color_popup = (1, 1, 1, 1)

        # Encabezados de la tabla
        encabezados = GridLayout(cols=5, size_hint_y=None, height=40)
        encabezados.add_widget(Label(text='Mes', bold=True, color=color_popup))
        encabezados.add_widget(Label(text='Cuota', bold=True, color=color_popup))
        encabezados.add_widget(Label(text='Interes', bold=True, color=color_popup))
        encabezados.add_widget(Label(text='Capital', bold=True, color=color_popup))
        encabezados.add_widget(Label(text='Saldo', bold=True, color=color_popup))
        contenido.add_widget(encabezados)

        # Tabla scrollable con las filas
        scroll_tabla = ScrollView(size_hint=(1, 1))
        tabla = GridLayout(cols=5, size_hint_y=None, row_default_height=30)
        tabla.bind(minimum_height=tabla.setter('height'))

        saldo = monto_credito
        for i in range(1, cantidad_cuotas + 1):
            if tasa_interes_mensual == logica_credito.TASA_MINIMA:
                interes = 0.0
                abono = cuota_mensual
            else:
                interes = saldo * tasa_interes_mensual
                abono = cuota_mensual - interes

            saldo -= abono
            if saldo < 0 or i == cantidad_cuotas:
                saldo = 0.0

            tabla.add_widget(Label(text=str(i), color=color_popup))
            tabla.add_widget(Label(text=f'${interes + abono:,.2f}', color=color_popup))
            tabla.add_widget(Label(text=f'${interes:,.2f}', color=color_popup))
            tabla.add_widget(Label(text=f'${abono:,.2f}', color=color_popup))
            tabla.add_widget(Label(text=f'${saldo:,.2f}', color=color_popup))

        scroll_tabla.add_widget(tabla)
        contenido.add_widget(scroll_tabla)

        # Boton para cerrar el popup
        cerrar = Button(text='Cerrar', size_hint_y=None, height=40)
        contenido.add_widget(cerrar)

        popup = Popup(
            title='Tabla de Amortizacion',
            content=contenido,
            size_hint=(0.9, 0.9),
        )
        cerrar.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == '__main__':
    CreditoICETEXApp().run()