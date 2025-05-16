import tkinter as tk
import customtkinter as ctk
import sys
import os

# Importar módulos
from modulos.conexion import PestanaConexion
from modulos.visualizacion_matplotlib import PestanaVisualizacionMatplotlib
from modulos.consultas_sql import PestanaConsultasSQL
from modulos.consultas_naturales_gemini import PestanaConsultasNaturales
from modulos.acerca_de import PestanaAcercaDe
from mysql.connector import Error

# Configuración de la apariencia de customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class AplicacionBD(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Manoseando mis Bases de Datos MySQL")
        self.geometry("1200x768")
        
        # Permitir que la ventana sea redimensionable y que los componentes se adapten
        self.minsize(800, 600)  # Tamaño mínimo para asegurar usabilidad
        
        # Iniciar en pantalla completa
        self.state('zoomed')

        # Crear panel de estado de conexión en la parte inferior
        self.panel_estado = ctk.CTkFrame(self, height=30)
        self.panel_estado.pack(fill="x", side="bottom", padx=10, pady=5)
        
        # Etiqueta para mostrar el estado de la conexión
        self.estado_conexion_label = ctk.CTkLabel(
            self.panel_estado,
            text="Verificando estado del servidor MySQL...",
            text_color="orange"
        )
        self.estado_conexion_label.pack(side="left", padx=10)
        
        # Etiqueta para mostrar fecha y hora
        self.fecha_hora_label = ctk.CTkLabel(
            self.panel_estado,
            text="",
            text_color="white"
        )
        self.fecha_hora_label.pack(side="right", padx=10)
        
        # Iniciar actualización de fecha y hora
        self.actualizar_fecha_hora()

        # Verificar estado del servidor inmediatamente
        self.verificar_estado_servidor()

        # Crear el contenedor de pestañas
        self.pestanas = ctk.CTkTabview(self)
        self.pestanas.pack(expand=True, fill="both", padx=10, pady=(10, 0))

        # Agregar el evento de cambio de pestaña
        original_command = self.pestanas._segmented_button._command
        def combined_command(value):
            if original_command:
                original_command(value)
            self.verificar_estado_servidor()
            
        self.pestanas._segmented_button.configure(command=combined_command)

        # Agregar pestañas
        self.pestanas.add("Conexión")
        self.pestanas.add("Visualización")
        self.pestanas.add("Consultas SQL")
        self.pestanas.add("Consultas en Lenguaje Natural")
        self.pestanas.add("Acerca de")
        
        # Inicializar pestañas con sus respectivos módulos
        self.pestana_conexion = PestanaConexion(self.pestanas.tab("Conexión"))
        self.pestana_conexion.pack(expand=True, fill="both")

        # Frame para la pestaña de visualización
        frame_visualizacion = self.pestanas.tab("Visualización")
        
        # Inicializar la pestaña de visualización
        self.pestana_visualizacion = PestanaVisualizacionMatplotlib(
            frame_visualizacion,
            self.pestana_conexion.obtener_conexion_actual,
            self.pestana_conexion.obtener_base_datos_actual
        )
        self.pestana_visualizacion.pack(expand=True, fill="both")

        self.pestana_consultas_sql = PestanaConsultasSQL(
            self.pestanas.tab("Consultas SQL"),
            self.pestana_conexion.obtener_conexion_actual,
            self.pestana_conexion.obtener_base_datos_actual
        )
        self.pestana_consultas_sql.pack(expand=True, fill="both")

        self.pestana_consultas_naturales = PestanaConsultasNaturales(
            self.pestanas.tab("Consultas en Lenguaje Natural"),
            self.pestana_conexion.obtener_conexion_actual,
            self.pestana_conexion.obtener_base_datos_actual
        )
        self.pestana_consultas_naturales.pack(expand=True, fill="both")

        self.pestana_acerca_de = PestanaAcercaDe(self.pestanas.tab("Acerca de"))
        self.pestana_acerca_de.pack(expand=True, fill="both")
        
        # Configurar el callback para actualizar el estado de conexión
        self.actualizar_estado_conexion()

        # Centrar la ventana en la pantalla
        # self.center_window()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    
    def verificar_estado_servidor(self):
        """Verifica si el servidor MySQL está operativo"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)  # Timeout corto para la verificación
            result = sock.connect_ex(('localhost', 3306))
            sock.close()
            
            if result == 0:
                estado_servidor = "Estado: Servidor MySQL operativo y aceptando conexiones"
                color = "green"
            else:
                estado_servidor = "Estado: Servidor MySQL no está en ejecución"
                color = "red"
        except Exception as e:
            estado_servidor = "Estado: Servidor MySQL no está en ejecución"
            color = "red"
            
        self.estado_conexion_label.configure(
            text=estado_servidor,
            text_color=color
        )
        return estado_servidor, color

    def actualizar_estado_conexion(self):
        """Actualiza el estado de la conexión en el panel inferior"""
        try:
            conexion, cursor = self.pestana_conexion.obtener_conexion_actual()
            if conexion and conexion.is_connected():
                bd_actual = self.pestana_conexion.obtener_base_datos_actual()
                if bd_actual:
                    estado_conexion = f"Conectado a {bd_actual} en {conexion.server_host}"
                else:
                    estado_conexion = f"Conectado a {conexion.server_host}"
                self.estado_conexion_label.configure(
                    text=estado_conexion,
                    text_color="green"
                )
            else:
                # Solo verificar el servidor si no hay conexión activa
                estado_servidor, color_servidor = self.verificar_estado_servidor()
                self.estado_conexion_label.configure(
                    text=estado_servidor,
                    text_color=color_servidor
                )
        except Error as e:
            # En caso de error, verificar el estado del servidor
            estado_servidor, color_servidor = self.verificar_estado_servidor()
            self.estado_conexion_label.configure(
                text=estado_servidor,
                text_color=color_servidor
            )
        
        # Programar la próxima actualización en 5 segundos
        self.after(5000, self.actualizar_estado_conexion)

    def actualizar_fecha_hora(self):
        """Actualiza la fecha y hora en el panel inferior"""
        from datetime import datetime
        import locale
        
        # Configurar locale para español
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'Spanish_Spain')
            except locale.Error:
                pass
        
        # Obtener fecha y hora actual
        ahora = datetime.now()
        fecha_hora = ahora.strftime("%d de %B de %Y, %H:%M:%S")
        
        # Actualizar etiqueta
        self.fecha_hora_label.configure(text=fecha_hora)
        
        # Actualizar cada segundo
        self.after(1000, self.actualizar_fecha_hora)

if __name__ == "__main__":
    app = AplicacionBD()
    app.mainloop()