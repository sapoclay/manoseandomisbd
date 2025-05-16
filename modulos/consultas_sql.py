import customtkinter as ctk
import mysql.connector
from tkinter import ttk
import tkinter as tk
from typing import List, Tuple, Dict, Optional # Añadido Dict y Optional
import json
import os
from tkinter.messagebox import askyesno, showinfo # Añadido showinfo
import sqlparse
import tkinter.simpledialog

# Nueva clase para la ventana de gestión de favoritos
class VentanaGestionFavoritos(ctk.CTkToplevel):
    def __init__(self, master, consultas_dict: Dict[str, str], callback_eliminar, callback_eliminar_todos): 
        super().__init__(master)
        self.consultas_dict = consultas_dict
        self.callback_eliminar = callback_eliminar
        self.callback_eliminar_todos = callback_eliminar_todos # Guardar el nuevo callback
        self.vars_checkboxes: Dict[str, tk.BooleanVar] = {}

        self.title("Gestionar Consultas Favoritas")
        self.geometry("500x450") # Ajustar un poco la altura si es necesario
        self.grab_set() # Hacer la ventana modal

        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Frame para los checkboxes (scrollable)
        scrollable_frame = ctk.CTkScrollableFrame(main_frame)
        scrollable_frame.pack(expand=True, fill="both", pady=(0, 10))

        if not self.consultas_dict:
            ctk.CTkLabel(scrollable_frame, text="No hay consultas favoritas guardadas.").pack(pady=20)
        else:
            for nombre_consulta in self.consultas_dict.keys():
                var = tk.BooleanVar()
                self.vars_checkboxes[nombre_consulta] = var
                cb = ctk.CTkCheckBox(scrollable_frame, text=nombre_consulta, variable=var)
                cb.pack(anchor="w", padx=5, pady=2)

        # Frame para botones de acción (Seleccionar/Deseleccionar Todos)
        action_frame = ctk.CTkFrame(main_frame)
        action_frame.pack(fill="x", pady=(0,5)) # Añadido pady

        btn_seleccionar_todos = ctk.CTkButton(action_frame, text="Seleccionar Todos", command=self.seleccionar_todos)
        btn_seleccionar_todos.pack(side="left", padx=5, pady=5)

        btn_deseleccionar_todos = ctk.CTkButton(action_frame, text="Deseleccionar Todos", command=self.deseleccionar_todos)
        btn_deseleccionar_todos.pack(side="left", padx=5, pady=5)

        # Frame para botones de confirmación y acción
        confirm_frame = ctk.CTkFrame(self)
        confirm_frame.pack(fill="x", padx=10, pady=(5,10)) # Añadido pady

        btn_eliminar_seleccionados = ctk.CTkButton(confirm_frame, text="Eliminar Seleccionados", command=self.confirmar_eliminacion_seleccionados, fg_color="orange")
        btn_eliminar_seleccionados.pack(side="left", padx=5, pady=5, expand=True)
        
        btn_eliminar_todos = ctk.CTkButton(confirm_frame, text="Eliminar Todos", command=self.ejecutar_eliminar_todos, fg_color="red") # Nuevo botón
        btn_eliminar_todos.pack(side="left", padx=5, pady=5, expand=True)
        
        btn_cancelar = ctk.CTkButton(confirm_frame, text="Cancelar", command=self.destroy)
        btn_cancelar.pack(side="right", padx=5, pady=5, expand=True) # Movido a la derecha para mejor flujo
        
        if not self.consultas_dict:
            btn_seleccionar_todos.configure(state="disabled")
            btn_deseleccionar_todos.configure(state="disabled")
            btn_eliminar_seleccionados.configure(state="disabled")
            btn_eliminar_todos.configure(state="disabled") # Deshabilitar si no hay favoritos


    def seleccionar_todos(self):
        for var in self.vars_checkboxes.values():
            var.set(True)

    def deseleccionar_todos(self):
        for var in self.vars_checkboxes.values():
            var.set(False)

    def confirmar_eliminacion_seleccionados(self): # Renombrado para claridad
        consultas_a_eliminar = [nombre for nombre, var in self.vars_checkboxes.items() if var.get()]
        
        if not consultas_a_eliminar:
            showinfo("Sin Selección", "No has seleccionado ninguna consulta para eliminar.")
            return

        if self.callback_eliminar:
            self.callback_eliminar(consultas_a_eliminar)
        self.destroy()

    def ejecutar_eliminar_todos(self): # Nuevo método
        """Ejecuta el callback para eliminar todos los favoritos y cierra la ventana."""
        if self.callback_eliminar_todos:
            self.callback_eliminar_todos() # Llama al método de PestanaConsultasSQL
        self.destroy()


class PestanaConsultasSQL(ctk.CTkFrame):
    def __init__(self, parent, obtener_conexion, obtener_bd):
        super().__init__(parent)
        self.obtener_conexion = obtener_conexion
        self.obtener_bd = obtener_bd
        self.historial_consultas = []
        self.placeholder_favoritos = "Consultas Guardadas" 
        self.consultas_favoritas: Dict[str, str] = self.cargar_favoritos() # Especificar tipo
        self.indice_historial = -1
        self.crear_widgets()
        self.palabras_clave_sql = [
            "SELECT", "FROM", "WHERE", "INSERT", "UPDATE", "DELETE",
            "JOIN", "LEFT", "RIGHT", "INNER", "GROUP BY", "ORDER BY",
            "HAVING", "LIMIT", "OFFSET", "CREATE", "ALTER", "DROP",
            "TABLE", "DATABASE", "INDEX", "VIEW", "AND", "OR", "NOT", "RENAME",
            "TRUNCATE", "MERGE", "UNION", "TRIGGER",
        ]

    def crear_widgets(self):
        # Frame principal con scroll vertical
        frame_principal = ctk.CTkScrollableFrame(self)
        frame_principal.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Frame para botones de historial y favoritos
        frame_botones = ctk.CTkFrame(frame_principal)
        frame_botones.pack(fill="x", padx=10, pady=5)
        
        # Botones de navegación del historial
        self.btn_anterior = ctk.CTkButton(
            frame_botones,
            text="↑",
            command=self.consulta_anterior,
            width=30
        )
        self.btn_anterior.pack(side="left", padx=2)
        
        self.btn_siguiente = ctk.CTkButton(
            frame_botones,
            text="↓",
            command=self.consulta_siguiente,
            width=30
        )
        self.btn_siguiente.pack(side="left", padx=2)
        
        # Botón para guardar en favoritos
        self.btn_favorito = ctk.CTkButton(
            frame_botones,
            text="★ Guardar en Favoritos",
            command=self.guardar_favorito
        )
        self.btn_favorito.pack(side="left", padx=5)
        
        # Menú desplegable de favoritos
        self.favoritos_var = tk.StringVar(value=self.placeholder_favoritos) 
        
        current_keys = list(self.consultas_favoritas.keys())
        
        self.menu_favoritos = ctk.CTkOptionMenu(
            frame_botones,
            values=current_keys, 
            variable=self.favoritos_var,
            command=self.cargar_favorito
        )
        self.menu_favoritos.pack(side="left", padx=5)

        # Botón para abrir la ventana de gestión de eliminación de favoritos
        self.btn_gestionar_favoritos = ctk.CTkButton(
            frame_botones,
            text="Gestionar Favoritos", 
            command=self.abrir_ventana_gestion_favoritos 
        )
        self.btn_gestionar_favoritos.pack(side="left", padx=5)

        # Frame para el editor SQL
        frame_editor = ctk.CTkFrame(frame_principal)
        frame_editor.pack(fill="both", expand=True, padx=10, pady=5)

        # Editor SQL con autocompletado
        self.editor_sql = ctk.CTkTextbox(frame_editor, height=150)
        self.editor_sql.pack(fill="both", expand=True, padx=5, pady=5)
        self.editor_sql.bind('<KeyRelease>', self.resaltar_sintaxis)
        self.editor_sql.bind('<KeyRelease>', self.mostrar_autocompletado_al_escribir)
        self.editor_sql.bind('<space>', self.ocultar_autocompletado)

        # Lista de autocompletado
        self.lista_autocompletado = tk.Listbox(frame_editor)
        self.lista_autocompletado.bind('<Up>', lambda e: self.navegar_sugerencias('up'))
        self.lista_autocompletado.bind('<Down>', lambda e: self.navegar_sugerencias('down'))
        self.lista_autocompletado.bind('<Return>', lambda e: self.seleccionar_sugerencia())
        self.lista_autocompletado.bind('<Escape>', lambda e: self.ocultar_autocompletado())
        self.lista_autocompletado.bind('<Tab>', lambda e: self.seleccionar_sugerencia())
        
        # Agregar bindings al editor para manejar el foco
        self.editor_sql.bind('<Tab>', self.manejar_tab)
        self.editor_sql.bind('<Escape>', lambda e: self.ocultar_autocompletado())
        
        # Frame de botones
        frame_botones_ejecutar = ctk.CTkFrame(frame_editor)
        frame_botones_ejecutar.pack(fill="x", padx=5, pady=5)

        # Botón de validar
        self.btn_validar = ctk.CTkButton(
            frame_botones_ejecutar,
            text="Validar SQL",
            command=self.validar_sql
        )
        self.btn_validar.pack(side="left", padx=5)

        # Botón de ejecutar
        self.btn_ejecutar = ctk.CTkButton(
            frame_botones_ejecutar,
            text="Ejecutar Consulta",
            command=self.ejecutar_consulta
        )
        self.btn_ejecutar.pack(side="left", padx=5)

        # Frame para resultados
        frame_resultados = ctk.CTkFrame(self)
        frame_resultados.pack(fill="both", expand=True, padx=10, pady=5)

        # Contenedor para scrollbars y tabla
        container = ttk.Frame(frame_resultados)
        container.pack(fill="both", expand=True)

        # Scrollbars para la tabla
        scroll_y = ttk.Scrollbar(container, orient="vertical")
        scroll_x = ttk.Scrollbar(container, orient="horizontal")

        # Tabla de resultados (usando ttk.Treeview)
        self.tabla_resultados = ttk.Treeview(
            container,
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
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
        self.mensaje_label = ctk.CTkLabel(self, text="")
        self.mensaje_label.pack(pady=5)

    def limpiar_tabla(self):
        # Limpiar tabla existente
        for item in self.tabla_resultados.get_children():
            self.tabla_resultados.delete(item)
        
        # Limpiar columnas
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

    def navegar_sugerencias(self, direccion):
        """Maneja la navegación con teclas arriba/abajo en la lista de sugerencias"""
        if not self.lista_autocompletado.size():
            return
            
        seleccion = self.lista_autocompletado.curselection()
        if not seleccion:
            # Si no hay selección, seleccionar el primer o último elemento
            if direccion == 'down':
                self.lista_autocompletado.selection_set(0)
            else:  # up
                self.lista_autocompletado.selection_set(self.lista_autocompletado.size() - 1)
        else:
            # Mover la selección arriba o abajo
            actual = seleccion[0]
            if direccion == 'down':
                siguiente = (actual + 1) % self.lista_autocompletado.size()
            else:  # up
                siguiente = (actual - 1) % self.lista_autocompletado.size()
            
            self.lista_autocompletado.selection_clear(0, "end")
            self.lista_autocompletado.selection_set(siguiente)
            self.lista_autocompletado.see(siguiente)

    def manejar_tab(self, event):
        """Maneja la tecla Tab para alternar entre editor y sugerencias"""
        if self.lista_autocompletado.winfo_ismapped():
            self.lista_autocompletado.focus_set()
            if self.lista_autocompletado.size() > 0:
                self.lista_autocompletado.selection_set(0)
            return "break"  # Prevenir comportamiento por defecto del Tab
        return None

    def mostrar_autocompletado_al_escribir(self, event=None):
        """Muestra sugerencias de autocompletado mientras se escribe"""
        # Ignorar teclas especiales
        if event and event.keysym in ('Up', 'Down', 'Return', 'Escape', 'Tab', 'Shift_L', 'Shift_R', 
                                     'Control_L', 'Control_R', 'Alt_L', 'Alt_R'):
            return
            
        # Mantener el foco en el editor
        self.editor_sql.focus_set()
            
        texto = self.editor_sql.get("1.0", "end-1c")
        palabras = texto.split()
        
        if not palabras:
            self.lista_autocompletado.place_forget()
            return
            
        ultima_palabra = palabras[-1].upper()
        
        # Si la última palabra está completa, ocultar sugerencias
        if texto.endswith(' ') or texto.endswith(';'):
            self.lista_autocompletado.place_forget()
            return
        
        # Buscar sugerencias
        sugerencias = [p for p in self.palabras_clave_sql if p.startswith(ultima_palabra)]
        
        if sugerencias:
            self.lista_autocompletado.delete(0, "end")
            for sugerencia in sugerencias:
                self.lista_autocompletado.insert("end", sugerencia)
            
            # Posicionar lista cerca del cursor
            x, y, _, h = self.editor_sql.bbox("insert")
            x = x + self.editor_sql.winfo_x() + self.winfo_x()
            y = y + h + self.editor_sql.winfo_y() + self.winfo_y()
            
            self.lista_autocompletado.place(x=x, y=y)
        else:
            self.lista_autocompletado.place_forget()

    def seleccionar_sugerencia(self, event=None):
        """Selecciona una sugerencia de la lista y la inserta en el editor"""
        if not self.lista_autocompletado.winfo_ismapped():
            return "break"
            
        seleccion = self.lista_autocompletado.curselection()
        if seleccion:
            indice = seleccion[0]
            sugerencia = self.lista_autocompletado.get(indice)
            
            # Obtener la posición actual y la última palabra
            texto = self.editor_sql.get("1.0", "end-1c")
            palabras = texto.split()
            ultima_palabra = palabras[-1] if palabras else ""
            
            # Eliminar la palabra parcial y reemplazarla con la sugerencia
            linea, columna = self.editor_sql.index("insert").split('.')
            inicio = f"{linea}.{int(columna) - len(ultima_palabra)}"
            self.editor_sql.delete(inicio, "insert")
            self.editor_sql.insert("insert", sugerencia + " ")
            
        # Ocultar la lista y devolver el foco al editor
        self.lista_autocompletado.place_forget()
        self.editor_sql.focus_set()
        return "break"

    def resaltar_sintaxis(self, event=None):
        """Resalta la sintaxis SQL en el editor"""
        # Guardar la posición del cursor
        cursor_pos = self.editor_sql.index("insert")
        
        # Obtener el contenido actual
        contenido = self.editor_sql.get("1.0", "end-1c")
        
        # Solo proceder si hay contenido
        if contenido.strip():
            # Limpiar tags existentes
            for tag in self.editor_sql.tag_names():
                self.editor_sql.tag_remove(tag, "1.0", "end")
            
            # Resaltar palabras clave sin modificar el contenido
            for palabra in self.palabras_clave_sql:
                inicio = "1.0"
                while True:
                    inicio = self.editor_sql.search(palabra, inicio, "end", nocase=True)
                    if not inicio:
                        break
                    fin = f"{inicio}+{len(palabra)}c"
                    self.editor_sql.tag_add("keyword", inicio, fin)
                    inicio = fin
            
            # Configurar el color de las palabras clave
            self.editor_sql.tag_config("keyword", foreground="blue")
            
            # Restaurar la posición del cursor
            self.editor_sql.mark_set("insert", cursor_pos)

    def validar_sql(self):
        """Valida la sintaxis SQL antes de ejecutar"""
        consulta = self.editor_sql.get("1.0", "end-1c").strip()
        if not consulta:
            self.mensaje_label.configure(
                text="La consulta está vacía",
                text_color="red"
            )
            return False

        conexion, cursor = self.obtener_conexion()
        if not conexion or not cursor:
            self.mensaje_label.configure(
                text="No hay conexión a la base de datos",
                text_color="red"
            )
            return False

        bd_actual = self.obtener_bd()
        if not bd_actual:
            self.mensaje_label.configure(
                text="No se ha seleccionado una base de datos",
                text_color="red"
            )
            return False

        try:
            cursor.execute(f"USE {bd_actual}")
            palabras = consulta.upper().split()
            if palabras and palabras[0] == "SELECT":
                # Usar EXPLAIN para validar sintaxis SELECT
                cursor.execute(f"EXPLAIN {consulta}")
                cursor.fetchall()  # <-- Añade esta línea para consumir los resultados
                self.mensaje_label.configure(
                    text="Sintaxis SQL válida",
                    text_color="green"
                )
                return True
            else:
                # Para otras sentencias, solo advertir al usuario
                self.mensaje_label.configure(
                    text="La validación de sintaxis solo está disponible para consultas SELECT.",
                    text_color="orange"
                )
                return False
        except Exception as e:
            self.mensaje_label.configure(
                text=f"Error de sintaxis: {str(e)}",
                text_color="red"
            )
            return False

    def ejecutar_consulta(self):
        """Ejecuta la consulta SQL y guarda en el historial"""
        if not self.validar_sql():
            return

        conexion, cursor = self.obtener_conexion()
        if not conexion or not cursor:
            self.mensaje_label.configure(
                text="No hay conexión a la base de datos",
                text_color="red"
            )
            return

        bd_actual = self.obtener_bd()
        if not bd_actual:
            self.mensaje_label.configure(
                text="No se ha seleccionado una base de datos",
                text_color="red"
            )
            return

        consulta = self.editor_sql.get("1.0", "end-1c").strip()
        # Agregar al historial
        self.historial_consultas.append(consulta)
        self.indice_historial = len(self.historial_consultas) - 1

        # --- ADVERTENCIA PARA SENTENCIAS PELIGROSAS ---
        consulta_lower = consulta.strip().lower()
        sentencias_peligrosas = ("drop", "update", "insert", "delete", "alter", "truncate", "create")
        if any(consulta_lower.startswith(s) for s in sentencias_peligrosas):
            respuesta = askyesno(
                title="Advertencia",
                message="La consulta que vas a ejecutar puede modificar la base de datos o su contenido:\n\n"
                        f"{consulta}\n\n¿Deseas continuar?",
                icon="warning"
            )
            if not respuesta:
                self.mensaje_label.configure(
                    text="Operación cancelada por el usuario.",
                    text_color="orange"
                )
                return

        try:
            cursor.execute(f"USE {bd_actual}")
            cursor.execute(consulta)
            
            # Obtener resultados
            resultados = cursor.fetchall()
            if not resultados:
                self.mensaje_label.configure(
                    text="La consulta no devolvió resultados",
                    text_color="orange"
                )
                self.limpiar_tabla()
                return

            # Obtener nombres de columnas
            columnas = [desc[0] for desc in cursor.description]
            
            # Mostrar resultados
            self.mostrar_resultados(columnas, resultados)
            self.mensaje_label.configure(
                text=f"Se encontraron {len(resultados)} resultados",
                text_color="green"
            )

        except mysql.connector.Error as e:
            self.mensaje_label.configure(
                text=f"Error en la consulta: {str(e)}",
                text_color="red"
            )
            self.limpiar_tabla()

    def consulta_anterior(self):
        """Navega a la consulta anterior en el historial"""
        if self.indice_historial > 0:
            self.indice_historial -= 1
            self.editor_sql.delete("1.0", "end")
            self.editor_sql.insert("1.0", self.historial_consultas[self.indice_historial])

    def consulta_siguiente(self):
        """Navega a la consulta siguiente en el historial"""
        if self.indice_historial < len(self.historial_consultas) - 1:
            self.indice_historial += 1
            self.editor_sql.delete("1.0", "end")
            self.editor_sql.insert("1.0", self.historial_consultas[self.indice_historial])

    def guardar_favorito(self):
        """Guarda la consulta actual en favoritos"""
        consulta = self.editor_sql.get("1.0", "end-1c").strip()
        if not consulta:
            return
            
        nombre = tkinter.simpledialog.askstring("Guardar Favorito", "Escribe el nombre para la consulta:")
        if nombre:
            if nombre == self.placeholder_favoritos: 
                tkinter.messagebox.showwarning("Nombre Inválido", f"No puedes usar '{self.placeholder_favoritos}' como nombre.")
                return
            self.consultas_favoritas[nombre] = consulta
            self.guardar_favoritos() # Guarda en el archivo
            self.actualizar_menu_favoritos() # Actualiza la lista de opciones del menú
            self.favoritos_var.set(nombre) # Seleccionar el favorito recién guardado
            self.mensaje_label.configure(text=f"Consulta '{nombre}' guardada en favoritos.", text_color="green")

    def cargar_favorito(self, nombre_seleccionado):
        """Carga una consulta favorita en el editor"""
        if nombre_seleccionado == self.placeholder_favoritos:
            return

        if nombre_seleccionado in self.consultas_favoritas:
            self.editor_sql.delete("1.0", "end")
            self.editor_sql.insert("1.0", self.consultas_favoritas[nombre_seleccionado])


    def _procesar_eliminacion_favoritos(self, nombres_a_eliminar: List[str]):
        """Procesa la eliminación de las consultas seleccionadas desde la ventana de gestión."""
        if not nombres_a_eliminar:
            return

        confirmar = askyesno(
            title="Confirmar Eliminación",
            message=f"¿Estás seguro de que deseas eliminar las {len(nombres_a_eliminar)} consultas favoritas seleccionadas?",
            icon="warning"
        )

        if confirmar:
            eliminadas_count = 0
            for nombre in nombres_a_eliminar:
                if nombre in self.consultas_favoritas:
                    del self.consultas_favoritas[nombre]
                    eliminadas_count += 1
            
            if eliminadas_count > 0:
                self.guardar_favoritos()
                self.actualizar_menu_favoritos() # Esto se encargará de resetear el placeholder si es necesario
                self.mensaje_label.configure(text=f"{eliminadas_count} consulta(s) favorita(s) eliminada(s).", text_color="green")
            else:
                # Esto es improbable si la ventana de gestión muestra la lista actual
                self.mensaje_label.configure(text="No se eliminó ninguna consulta.", text_color="orange")


    def abrir_ventana_gestion_favoritos(self):
        """Abre la ventana para gestionar (eliminar) consultas favoritas."""
        if not self.consultas_favoritas:
            showinfo("Gestionar Favoritos", "No hay consultas favoritas guardadas para gestionar.")
            return
        
        ventana = VentanaGestionFavoritos(
            self, 
            dict(self.consultas_favoritas), 
            self._procesar_eliminacion_favoritos,
            self.eliminar_todos_favoritos 
        )
        # self.wait_window(ventana) # Descomentar si es necesario esperar a que se cierre

    def eliminar_todos_favoritos(self):
        """Elimina todas las consultas favoritas guardadas."""
        if not self.consultas_favoritas:
            tkinter.messagebox.showinfo("Eliminar Favoritos", "No hay consultas favoritas para eliminar.")
            return

        confirmar = askyesno(
            title="Confirmar Eliminación Total",
            message="¿Estás seguro de que deseas eliminar TODAS las consultas favoritas? Esta acción no se puede deshacer.",
            icon="warning"
        )

        if confirmar:
            self.consultas_favoritas.clear()
            self.guardar_favoritos()
            self.actualizar_menu_favoritos() # Esto también se encargará de poner el placeholder
            self.mensaje_label.configure(text="Todas las consultas favoritas han sido eliminadas.", text_color="green")

    def cargar_favoritos(self):
        """Carga las consultas favoritas desde el archivo"""
        ruta_archivo = 'config/consultas_favoritas.json'
        try:
            with open(ruta_archivo, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"Error al cargar favoritos: {e}") # para depuración
            return {}

    def guardar_favoritos(self):
        """Guarda las consultas favoritas en un archivo"""
        ruta_archivo = 'config/consultas_favoritas.json'
        try:
            # Asegurarse de que el directorio 'config' exista
            os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
            with open(ruta_archivo, 'w') as f:
                json.dump(self.consultas_favoritas, f, indent=4) # indent para mejor legibilidad
        except Exception as e:
            print(f"Error al guardar favoritos: {e}") # para depuración


    def actualizar_menu_favoritos(self):
        """Actualiza el menú desplegable de favoritos y el valor de self.favoritos_var."""
        current_keys = list(self.consultas_favoritas.keys())
        
        # Configurar el OptionMenu solo con las claves reales
        self.menu_favoritos.configure(values=current_keys)

        current_selection_in_var = self.favoritos_var.get()

        if not current_keys:
            # No hay favoritos, mostrar placeholder
            self.favoritos_var.set(self.placeholder_favoritos)
        elif current_selection_in_var not in current_keys and current_selection_in_var != self.placeholder_favoritos:
            # Si la selección actual no está en las claves y no es el placeholder, restablecer al placeholder
            self.favoritos_var.set(self.placeholder_favoritos)
        elif not current_selection_in_var: # Si por alguna razón la variable está vacía
             self.favoritos_var.set(self.placeholder_favoritos) 
        
        # Si el valor actual de favoritos_var (lo que se muestra en el botón)
        # no está en las claves actuales Y no es el placeholder,
        # significa que una consulta seleccionada fue eliminada. Restablecer al placeholder.
        if self.favoritos_var.get() not in current_keys and self.favoritos_var.get() != self.placeholder_favoritos:
            self.favoritos_var.set(self.placeholder_favoritos)
        # Si no hay consultas favoritas, asegurarse de que se muestre el placeholder.
        elif not current_keys:
            self.favoritos_var.set(self.placeholder_favoritos)

    def ocultar_autocompletado(self, event=None):
        """Oculta la lista de autocompletado"""
        if self.lista_autocompletado.winfo_ismapped():
            self.lista_autocompletado.place_forget()
            self.editor_sql.focus_set()