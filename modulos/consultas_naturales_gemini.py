import customtkinter as ctk
import mysql.connector
from tkinter import ttk
from typing import List, Tuple, Optional
import re
from modulos.gemini_api import GeminiAPI
from tkinter.messagebox import askyesno

class PestanaConsultasNaturales(ctk.CTkFrame):
    def __init__(self, parent, obtener_conexion, obtener_bd):
        super().__init__(parent)
        self.obtener_conexion = obtener_conexion
        self.obtener_bd = obtener_bd
        self.gemini_api = GeminiAPI()
        self.crear_widgets()

    def crear_widgets(self):
        # Frame principal
        frame_principal = ctk.CTkFrame(self)
        frame_principal.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Frame superior para editor y controles
        frame_superior = ctk.CTkFrame(frame_principal)
        frame_superior.pack(fill="x", padx=10, pady=5)
        
        # Frame izquierdo para el editor
        frame_editor = ctk.CTkFrame(frame_superior)
        frame_editor.pack(side="left", fill="both", expand=True, padx=5)

        # Label instructivo
        ctk.CTkLabel(
            frame_editor,
            text="Escribe tu consulta en lenguaje natural",
            wraplength=300
        ).pack(pady=5)

        # Editor de texto
        self.editor_natural = ctk.CTkTextbox(frame_editor, height=100)
        self.editor_natural.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Frame derecho para controles
        frame_controles = ctk.CTkFrame(frame_superior)
        frame_controles.pack(side="left", fill="y", padx=5)
        
        # Botón para mostrar/ocultar ejemplos
        self.btn_ejemplos = ctk.CTkButton(
            frame_controles,
            text="Mostrar Ejemplos",
            command=self.toggle_ejemplos,
            width=150
        )
        self.btn_ejemplos.pack(pady=5)
        
        # Frame para API key
        frame_api = ctk.CTkFrame(frame_controles)
        frame_api.pack(fill="x", pady=5)
        
        ctk.CTkLabel(frame_api, text="API Key:").pack(side="left", padx=2)
        self.api_key_entry = ctk.CTkEntry(frame_api, show="*", width=150)
        self.api_key_entry.pack(side="left", padx=2)
        
        self.btn_guardar_api = ctk.CTkButton(
            frame_api,
            text="Guardar",
            command=self.guardar_api_key,
            width=70
        )
        self.btn_guardar_api.pack(side="left", padx=2)
        
        # Frame para botones de acción
        frame_acciones = ctk.CTkFrame(frame_controles)
        frame_acciones.pack(fill="x", pady=5)
        
        self.btn_ejecutar = ctk.CTkButton(
            frame_acciones,
            text="Generar y Ejecutar",
            command=self.procesar_consulta_natural,
            width=150
        )
        self.btn_ejecutar.pack(pady=2)

        self.btn_limpiar = ctk.CTkButton(
            frame_acciones,
            text="Limpiar",
            command=self.limpiar_campos,
            width=150
        )
        self.btn_limpiar.pack(pady=2)
        
        # Frame para ejemplos (inicialmente oculto)
        self.frame_ejemplos = ctk.CTkFrame(frame_principal)
        self.frame_ejemplos_visible = False
        
        # Contenido de ejemplos
        self.crear_contenido_ejemplos()

        # Frame para consulta SQL generada
        frame_sql = ctk.CTkFrame(frame_principal)
        frame_sql.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame_sql, text="Consulta SQL generada:").pack(pady=2)
        self.sql_generado = ctk.CTkTextbox(frame_sql, height=50)
        self.sql_generado.pack(fill="both", expand=True, padx=5, pady=5)

        # Frame para resultados
        frame_resultados = ctk.CTkFrame(frame_principal)
        frame_resultados.pack(fill="both", expand=True, padx=10, pady=5)

        # Título de resultados
        ctk.CTkLabel(
            frame_resultados,
            text="Resultados de la consulta",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        # Frame para la tabla con scrollbars
        frame_tabla = ctk.CTkFrame(frame_resultados)
        frame_tabla.pack(fill="both", expand=True, padx=5, pady=5)

        # Contenedor para scrollbars y tabla
        container = ttk.Frame(frame_tabla)
        container.pack(fill="both", expand=True)

        # Scrollbars para la tabla
        scroll_y = ttk.Scrollbar(container, orient="vertical")
        scroll_x = ttk.Scrollbar(container, orient="horizontal")

        # Tabla de resultados con estilo personalizado
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            rowheight=25,
            borderwidth=0,
            font=("Arial", 10)
        )
        style.configure(
            "Treeview.Heading",
            background="#2b2b2b",
            foreground="white",
            relief="flat",
            font=("Arial", 10, "bold"),
            borderwidth=1
        )
        style.map(
            "Treeview",
            background=[("selected", "#1f538d")],
            foreground=[("selected", "white")]
        )
        style.map(
            "Treeview.Heading",
            background=[("active", "#3c3c3c")],
            relief=[("pressed", "groove"), ("!pressed", "ridge")]
        )
        
        self.tabla_resultados = ttk.Treeview(
            container,
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            style="Treeview"
        )
        
        # Configurar scrollbars
        scroll_y.config(command=self.tabla_resultados.yview)
        scroll_x.config(command=self.tabla_resultados.xview)

        # Posicionar elementos usando grid
        self.tabla_resultados.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        # Configurar expansión del grid
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Label para mensajes
        self.mensaje_label = ctk.CTkLabel(frame_principal, text="")
        self.mensaje_label.pack(pady=5)

    def guardar_api_key(self):
        """Guarda la API key de Gemini"""
        api_key = self.api_key_entry.get().strip()
        if api_key:
            self.gemini_api.set_api_key(api_key)
            self.mensaje_label.configure(
                text="API Key guardada correctamente",
                text_color="green"
            )
        else:
            self.mensaje_label.configure(
                text="La API Key no puede estar vacía",
                text_color="red"
            )

    def limpiar_tabla(self):
        for item in self.tabla_resultados.get_children():
            self.tabla_resultados.delete(item)
        self.tabla_resultados['columns'] = ()

    def mostrar_resultados(self, columnas: List[str], datos: List[Tuple]):
        self.limpiar_tabla()

        # Configurar columnas
        self.tabla_resultados['columns'] = columnas
        self.tabla_resultados['show'] = 'headings'

        # Configurar encabezados
        for columna in columnas:
            self.tabla_resultados.heading(columna, text=columna)
            self.tabla_resultados.column(columna, minwidth=100)

        # Insertar datos
        for fila in datos:
            self.tabla_resultados.insert('', 'end', values=fila)
    
    def actualizar_estado_bd(self):
        """Actualiza el estado de la base de datos en la interfaz"""
        try:
            conexion, cursor = self.obtener_conexion()
            
            if not conexion or not cursor:
                self.bd_label.configure(
                    text="Base de datos: No conectada",
                    text_color="red"
                )
                return
                
            # Obtener la base de datos directamente del método obtener_bd
            bd_actual = self.obtener_bd()
            
            if bd_actual:
                self.bd_label.configure(
                    text=f"Base de datos actual: {bd_actual}",
                    text_color="green"
                )
            else:
                self.bd_label.configure(
                    text="Base de datos: No seleccionada",
                    text_color="orange"
                )
                
        except mysql.connector.Error:
            self.bd_label.configure(
                text="Base de datos: Error de conexión",
                text_color="red"
            )

    def toggle_ejemplos(self):
        """Muestra u oculta el panel de ejemplos"""
        if self.frame_ejemplos_visible:
            # Ocultar ejemplos
            self.frame_ejemplos.pack_forget()
            self.btn_ejemplos.configure(text="Mostrar Ejemplos")
            self.frame_ejemplos_visible = False
        else:
            # Mostrar ejemplos
            self.frame_ejemplos.pack(side="right", fill="both", expand=True, padx=5, pady=5)
            self.btn_ejemplos.configure(text="Ocultar Ejemplos")
            self.frame_ejemplos_visible = True
            # Actualizar ejemplos solo si hay conexión
            conexion, cursor = self.obtener_conexion()
            if conexion and cursor and self.obtener_bd():
                self.actualizar_ejemplos()
    
    def actualizar_ejemplos(self):
        """Actualiza los ejemplos basados en la estructura actual de la base de datos"""
        # Limpiar ejemplos anteriores
        for widget in self.frame_ejemplos.winfo_children():
            widget.destroy()
            
        # Verificar conexión
        conexion, cursor = self.obtener_conexion()
        if not conexion or not cursor:
            ctk.CTkLabel(
                self.frame_ejemplos,
                text="No hay conexión a la base de datos",
                wraplength=300,
                text_color="red"
            ).pack(pady=10)
            return
            
        # Obtener ejemplos
        ejemplos = self.generar_ejemplos_por_bd()
        
        # Crear frame scrollable para los ejemplos
        frame_scroll = ctk.CTkScrollableFrame(self.frame_ejemplos)
        frame_scroll.pack(fill="both", expand=True)
        
        # Mostrar título
        ctk.CTkLabel(
            frame_scroll,
            text="Ejemplos de consultas:",
            font=("Arial", 12, "bold")
        ).pack(pady=5)
        
        # Mostrar cada ejemplo
        for ejemplo in ejemplos:
            frame_ejemplo = ctk.CTkFrame(frame_scroll)
            frame_ejemplo.pack(fill="x", padx=5, pady=2)
            
            # Crear una etiqueta para el texto con ajuste de línea
            label_ejemplo = ctk.CTkLabel(
                frame_ejemplo,
                text=ejemplo,
                wraplength=250,
                justify="left",
                anchor="w"
            )
            label_ejemplo.pack(fill="x", padx=5, pady=2)
            
            # Crear el botón para usar el ejemplo
            btn_ejemplo = ctk.CTkButton(
                frame_ejemplo,
                text="Usar este ejemplo",
                command=lambda e=ejemplo: self.insertar_ejemplo(e),
                width=120,
                height=30
            )
            btn_ejemplo.pack(pady=2)

    def generar_ejemplos_por_bd(self) -> List[str]:
        """Genera ejemplos basados en la estructura de la base de datos actual"""
        # Verificar primero la conexión a la base de datos
        conexion, cursor = self.obtener_conexion()
        
        # Verificar que la conexión esté disponible
        if not conexion or not cursor:
            return ["Por favor, asegúrate de estar conectado a una base de datos antes de generar ejemplos."]
            
        try:
            # Obtener la base de datos actual
            cursor.execute("SELECT DATABASE()")
            bd_actual = cursor.fetchone()[0] or self.obtener_bd()
            
            if not bd_actual:
                return ["Por favor, selecciona una base de datos antes de generar ejemplos."]
        except mysql.connector.Error as e:
            return [f"Error al obtener la base de datos: {str(e)}"]

        estructura = self.obtener_estructura_bd()
        ejemplos = []

        if not estructura:
            return ["La base de datos seleccionada no contiene tablas."]

        # Generar ejemplos basados en las tablas disponibles
        for tabla, info in estructura.items():
            # Ejemplo básico de SELECT
            ejemplos.append(f"Muestra todos los registros de la tabla {tabla}")
            
            # Ejemplos con columnas específicas
            columnas_texto = [col[0] for col in info['columnas'] if 'CHAR' in col[1].upper() or 'TEXT' in col[1].upper()]
            columnas_numericas = [col[0] for col in info['columnas'] if 'INT' in col[1].upper() or 'DECIMAL' in col[1].upper() or 'FLOAT' in col[1].upper()]
            columnas_fecha = [col[0] for col in info['columnas'] if 'DATE' in col[1].upper() or 'TIME' in col[1].upper()]
            
            # Ejemplos con columnas de texto
            if columnas_texto:
                ejemplos.append(f"Busca en {tabla} donde {columnas_texto[0]} contenga un texto específico")
            
            # Ejemplos con columnas numéricas
            if columnas_numericas:
                ejemplos.append(f"Calcula el promedio de {columnas_numericas[0]} en {tabla}")
                ejemplos.append(f"Encuentra el valor máximo y mínimo de {columnas_numericas[0]} en {tabla}")
            
            # Ejemplos con fechas
            if columnas_fecha:
                ejemplos.append(f"Muestra registros de {tabla} ordenados por {columnas_fecha[0]}")
            
            # Ejemplos de agrupación
            if columnas_texto and columnas_numericas:
                ejemplos.append(f"Agrupa los registros de {tabla} por {columnas_texto[0]} y calcula el total de {columnas_numericas[0]}")
            
            # Ejemplos con relaciones
            for relacion in info['relaciones']:
                columna_origen = relacion[0]
                tabla_destino = relacion[1]
                columna_destino = relacion[2]
                ejemplos.append(f"Muestra los datos de {tabla} junto con la información relacionada de {tabla_destino}")
                if columnas_numericas:
                    ejemplos.append(f"Calcula el total de {columnas_numericas[0]} en {tabla} para cada {tabla_destino}")

        # Eliminar duplicados y limitar a 10 ejemplos
        ejemplos = list(dict.fromkeys(ejemplos))  # Eliminar duplicados preservando el orden
        return ejemplos[:10]  # Limitar a 10 ejemplos para no sobrecargar la interfaz

    def crear_contenido_ejemplos(self):
        """Crea el contenido del panel de ejemplos"""
        # Título
        ctk.CTkLabel(
            self.frame_ejemplos,
            text="Ejemplos de consultas en lenguaje natural",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Obtener ejemplos dinámicos
        ejemplos = self.generar_ejemplos_por_bd()
        
        # Frame para contener los ejemplos
        frame_lista = ctk.CTkScrollableFrame(self.frame_ejemplos, height=300)
        frame_lista.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Mostrar cada ejemplo como un botón que al hacer clic lo inserta en el editor
        for ejemplo in ejemplos:
            btn = ctk.CTkButton(
                frame_lista,
                text=ejemplo,
                command=lambda e=ejemplo: self.insertar_ejemplo(e),
                anchor="w",
                height=30
            )
            btn.pack(fill="x", pady=2)
    
    def insertar_ejemplo(self, ejemplo: str):
        """Inserta un ejemplo en el editor"""
        self.editor_natural.delete("1.0", "end")
        self.editor_natural.insert("1.0", ejemplo)

    def limpiar_campos(self):
        """Limpia los campos de texto de la consulta natural y SQL generada"""
        self.editor_natural.delete("1.0", "end")
        self.sql_generado.delete("1.0", "end")
        self.mensaje_label.configure(text="")
    
    def obtener_estructura_bd(self):
        """Obtiene la estructura de la base de datos actual"""
        conexion, cursor = self.obtener_conexion()
        if not conexion or not cursor:
            return {}

        bd_actual = self.obtener_bd()
        if not bd_actual:
            return {}

        cursor.execute(f"USE {bd_actual}")
        cursor.execute("SHOW TABLES")
        tablas = cursor.fetchall()

        estructura = {}
        for tabla in tablas:
            nombre_tabla = tabla[0]
            # Obtener estructura de la tabla
            cursor.execute(f"DESCRIBE {nombre_tabla}")
            columnas = cursor.fetchall()
            estructura[nombre_tabla] = {
                'columnas': columnas,
                'relaciones': []
            }

            # Obtener claves foráneas
            cursor.execute(f"""
                SELECT 
                    COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                FROM
                    INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE
                    TABLE_SCHEMA = '{bd_actual}'
                    AND TABLE_NAME = '{nombre_tabla}'
                    AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            relaciones = cursor.fetchall()
            estructura[nombre_tabla]['relaciones'] = relaciones

        return estructura
            
    def procesar_consulta_natural(self):
        """Procesa la consulta en lenguaje natural y ejecuta la consulta SQL generada"""
        texto_natural = self.editor_natural.get("1.0", "end-1c").strip()
        if not texto_natural:
            self.mensaje_label.configure(
                text="La consulta está vacía",
                text_color="red"
            )
            return
        
        # Verificar que se haya configurado la API key
        if not self.gemini_api.api_key:
            self.mensaje_label.configure(
                text="Debes configurar una API Key de Gemini para continuar",
                text_color="red"
            )
            return
        
        # Obtener la estructura de la base de datos
        estructura_bd = self.obtener_estructura_bd()
        if not estructura_bd:
            self.mensaje_label.configure(
                text="No hay conexión a la base de datos o no se ha seleccionado una base de datos",
                text_color="red"
            )
            return
        
        # Traducir a SQL usando Gemini
        self.mensaje_label.configure(
            text="Generando consulta SQL con Gemini...",
            text_color="blue"
        )
        self.update_idletasks()  # Actualizar la interfaz para mostrar el mensaje
        
        consulta_sql = self.gemini_api.traducir_a_sql(texto_natural, estructura_bd)
        
        if not consulta_sql:
            self.mensaje_label.configure(
                text="No se pudo generar una consulta SQL válida con Gemini",
                text_color="red"
            )
            return
        
        # Mostrar la consulta SQL generada
        self.sql_generado.delete("1.0", "end")
        self.sql_generado.insert("1.0", consulta_sql)
        
        # --- ADVERTENCIA PARA SENTENCIAS PELIGROSAS ---
        consulta_lower = consulta_sql.strip().lower()
        sentencias_peligrosas = ("drop", "update", "insert", "delete", "alter", "truncate", "create")
        if any(consulta_lower.startswith(s) for s in sentencias_peligrosas):
            respuesta = askyesno(
                title="Advertencia",
                message="La consulta generada puede modificar la base de datos:\n\n"
                        f"{consulta_sql}\n\n¿Estás seguro de que quieres continuar?",
                icon="warning"
            )
            if not respuesta:
                self.mensaje_label.configure(
                    text="Operación cancelada por el usuario.",
                    text_color="orange"
                )
                return

        # Ejecutar la consulta SQL
        conexion, cursor = self.obtener_conexion()
        if not conexion or not cursor:
            self.mensaje_label.configure(
                text="No hay conexión a la base de datos",
                text_color="red"
            )
            return
        
        try:
            cursor.execute(consulta_sql)
            
            # Verificar si la consulta devuelve resultados
            if cursor.description:
                # Obtener nombres de columnas
                columnas = [col[0] for col in cursor.description]
                
                # Obtener datos
                datos = cursor.fetchall()
                
                # Mostrar resultados en la tabla
                self.mostrar_resultados(columnas, datos)
                
                self.mensaje_label.configure(
                    text=f"Consulta ejecutada correctamente. {len(datos)} filas encontradas.",
                    text_color="green"
                )
            else:
                # La consulta no devuelve resultados (INSERT, UPDATE, DELETE)
                filas_afectadas = cursor.rowcount
                self.limpiar_tabla()
                self.mensaje_label.configure(
                    text=f"Consulta ejecutada correctamente. {filas_afectadas} filas afectadas.",
                    text_color="green"
                )
                
                # Hacer commit si es una operación de escritura
                conexion.commit()
                
        except mysql.connector.Error as e:
            self.mensaje_label.configure(
                text=f"Error al ejecutar la consulta: {str(e)}",
                text_color="red"
            )
            return
      