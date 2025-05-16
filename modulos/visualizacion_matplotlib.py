import customtkinter as ctk
import mysql.connector
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import networkx as nx
from PIL import Image, ImageTk
from tkinter import filedialog, Canvas, Scrollbar
import os
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np

class PestanaVisualizacionMatplotlib(ctk.CTkFrame):
    def __init__(self, parent, obtener_conexion, obtener_bd):
        super().__init__(parent)
        self.obtener_conexion = obtener_conexion
        self.obtener_bd = obtener_bd
        self.crear_widgets()
        self.diagrama_generado = False
        self.figura = None
        self.ruta_temp = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'img', 'diagrama_bd_temp.png')
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.start_x = 0
        self.start_y = 0
        self.is_panning = False
        self.grafo = None
        self.posiciones = None
        self.nodo_seleccionado = None
        self.modo_interactivo = False

    def crear_widgets(self):
        # Frame principal que ocupa todo el espacio
        self.pack(expand=True, fill="both")

        # Frame superior para botones
        frame_botones = ctk.CTkFrame(self)
        frame_botones.pack(fill="x", padx=5, pady=5)

        # Botones
        self.btn_generar = ctk.CTkButton(
            frame_botones,
            text="Generar Diagrama",
            command=self.generar_diagrama
        )
        self.btn_generar.pack(side="left", padx=5)

        self.btn_exportar = ctk.CTkButton(
            frame_botones,
            text="Exportar como PNG",
            command=self.exportar_diagrama
        )
        self.btn_exportar.pack(side="left", padx=5)
        
        # Botón para activar modo interactivo
        self.btn_modo_interactivo = ctk.CTkButton(
            frame_botones,
            text="Desactivar Modo Interactivo",
            command=self.activar_modo_interactivo
        )
        self.btn_modo_interactivo.pack(side="left", padx=5)
        
        # Botones de zoom
        self.btn_zoom_in = ctk.CTkButton(
            frame_botones,
            text="Zoom +",
            command=self.zoom_in
        )
        self.btn_zoom_in.pack(side="left", padx=5)
        
        self.btn_zoom_out = ctk.CTkButton(
            frame_botones,
            text="Zoom -",
            command=self.zoom_out
        )
        self.btn_zoom_out.pack(side="left", padx=5)
        
        self.btn_reset_zoom = ctk.CTkButton(
            frame_botones,
            text="Reset Vista",
            command=self.reset_zoom
        )
        self.btn_reset_zoom.pack(side="left", padx=5)

        # Frame contenedor para el diagrama y scrollbars
        self.frame_diagrama = ctk.CTkFrame(self)
        self.frame_diagrama.pack(fill="both", expand=True, padx=5, pady=5)

        # Label para mostrar información inicial sin scrollbars
        self.info_label = ctk.CTkLabel(
            self.frame_diagrama,
            text="Genera un diagrama para ver la estructura de la base de datos",
            wraplength=600
        )
        self.info_label.pack(expand=True, pady=20)

        # El canvas y scrollbars se crearán solo cuando se genere el diagrama
        self.canvas = None
        self.scrollbar_x = None
        self.scrollbar_y = None

    def obtener_estructura_tablas(self) -> Dict:
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

    def generar_diagrama(self):
        estructura = self.obtener_estructura_tablas()
        if not estructura:
            self.info_label.configure(text="No hay conexión a la base de datos o no se ha seleccionado una base de datos")
            return

        # Crear un grafo dirigido
        G = nx.DiGraph()
        
        # Agregar nodos (tablas)
        for tabla, info in estructura.items():
            # Preparar el texto para el nodo
            contenido = f"{tabla}\n\n"
            for columna in info['columnas']:
                nombre = columna[0]
                tipo = columna[1]
                nulo = 'NULL' if columna[2] == 'YES' else 'NOT NULL'
                clave = ' PK' if columna[3] == 'PRI' else ''
                contenido += f"{nombre} : {tipo} {nulo}{clave}\n"
            
            # Determinar el color del nodo según si tiene relaciones
            tiene_relaciones = len(info['relaciones']) > 0
            G.add_node(tabla, label=contenido, has_relations=tiene_relaciones)

        # Añadir aristas (relaciones)
        for tabla, info in estructura.items():
            for relacion in info['relaciones']:
                columna_origen = relacion[0]
                tabla_destino = relacion[1]
                columna_destino = relacion[2]
                G.add_edge(tabla, tabla_destino, label=f"{columna_origen} -> {columna_destino}")

        # Crear figura para el diagrama con un tamaño adecuado
        plt.figure(figsize=(14, 10))
        plt.clf()  # Limpiar la figura actual
        
        # Usar un layout para diagramas de bases de datos con mayor separación entre tablas
        if len(G.nodes()) <= 5:
            pos = nx.spring_layout(G, k=2.5, iterations=200)  # Aumentado el espacio entre nodos para pocos nodos
        else:
            # Para más nodos, usar un layout más espaciado pero organizado
            try:
                # Intentar primero con kamada_kawai pero con mucho más espacio
                pos = nx.kamada_kawai_layout(G)
                # Aplicar un factor de escala mayor para separar más los nodos
                pos = {node: (coord[0]*3.0, coord[1]*3.0) for node, coord in pos.items()}
            except:
                # Fallback con mucha más separación
                pos = nx.spring_layout(G, k=2.0, iterations=200, seed=42)
        
        # Dibujar nodos como cuadrados con los campos dentro
        for node in G.nodes():
            # Obtener posición del nodo
            x, y = pos[node]
            
            # Calcular tamaño del cuadrado basado en la cantidad de columnas y longitud del nombre
            num_columnas = len(estructura[node]['columnas'])
            # Ajustar el ancho basado en la longitud del nombre de la tabla y el contenido de los campos
            # Calcular la longitud máxima de los nombres de campos para ajustar el ancho
            max_campo_len = max([len(col[0]) for col in estructura[node]['columnas']], default=0)
            ancho_base = max(0.25, len(node) * 0.012)
            ancho = ancho_base + (max_campo_len * 0.012)  # Ancho proporcional a la longitud máxima de los campos
            alto = 0.18 + (num_columnas * 0.04)    # Alto proporcional a la cantidad de columnas con más espacio
            
            # El tamaño de los nodos para evitar superposiciones
            ancho *= 0.9
            alto *= 0.9
            
            # Color del nodo según si tiene relaciones
            color = '#4CAF50' if G.nodes[node].get('has_relations', False) else '#2196F3'
            
            # Crear un rectángulo para el nodo
            rect = plt.Rectangle((x - ancho/2, y - alto/2), ancho, alto, 
                                 facecolor=color, alpha=0.8, edgecolor='black', zorder=2)
            plt.gca().add_patch(rect)
            
            # Agregar el nombre de la tabla en la parte superior del cuadrado con más margen
            # El margen superior se reduce para acercar el título a los campos
            plt.text(x, y + alto/2 - 0.008, node, 
                     horizontalalignment='center', verticalalignment='top',
                     fontsize=10, fontweight='bold', color='black', zorder=3)
            
            # Agregar los campos de la tabla dentro del cuadrado
            campos_texto = []
            campos_info = []
            for i, columna in enumerate(estructura[node]['columnas']):
                nombre = columna[0]
                tipo = columna[1]
                es_pk = ' (PK)' if columna[3] == 'PRI' else ''
                campo_texto = f"{nombre}{es_pk}"
                campos_texto.append(campo_texto)
                campos_info.append((nombre, es_pk, columna[3] == 'PRI'))
                
                # Limitar la cantidad de campos mostrados si son muchos
                if i >= 6 and len(estructura[node]['columnas']) > 8:
                    campos_texto.append(f"... y {len(estructura[node]['columnas']) - 7} más")
                    campos_info.append((f"... y {len(estructura[node]['columnas']) - 7} más", "", False))
                    break
            
            # Calcular posición para cada campo con mejor espaciado vertical
            # Ajustamos el espaciado según la cantidad de campos para optimizar el espacio
            total_campos = len(campos_texto)
            
            # Calcular el espacio disponible dentro del rectángulo para los campos
            espacio_disponible = alto - 0.06  # Reservar espacio para el título
            espacio_por_campo = espacio_disponible / max(total_campos, 1)  # Evitar división por cero
            
            # Dibujar un separador después del título
            separador_y = y + alto/2 - 0.04
            plt.plot([x - ancho/2 + 0.01, x + ancho/2 - 0.01], [separador_y, separador_y], 
                     color='black', linewidth=0.5, alpha=0.5, zorder=3)
            
            for i, (campo, info) in enumerate(zip(campos_texto, campos_info)):
                # Calcular posición vertical con mejor distribución
                # Empezamos desde arriba (después del título) y vamos bajando
                offset_y = alto/2 - 0.06 - ((i + 0.7) * espacio_por_campo)
                
                # Determinar si es clave primaria para destacarla
                es_pk = info[2]  # Es clave primaria
                
                # Dibujar el texto del campo con un fondo para mejor legibilidad
                plt.text(x, y + offset_y, campo, 
                         horizontalalignment='center', verticalalignment='center',
                         fontsize=8, color='black', zorder=3,
                         bbox=dict(facecolor='#E8F5E9' if es_pk else 'white', 
                                  alpha=0.8, edgecolor='#CCCCCC' if es_pk else None, 
                                  pad=2, boxstyle="round,pad=0.4"))
        
        # Dibujar aristas después de los nodos para que aparezcan por encima
        nx.draw_networkx_edges(G, pos, edge_color='#9C27B0', arrows=True, arrowsize=20, width=1.5, alpha=0.9)
        
        # Dibujar etiquetas de aristas (relaciones) con mejor formato y por encima de todo
        edge_labels = {(u, v): G[u][v]['label'] for u, v in G.edges()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, font_color='#D81B60')
        
        # Ajustar el diseño
        plt.axis('off')
        plt.tight_layout()
        
        # Asegurar que todo el gráfico esté visible dentro de los límites
        ax = plt.gca()
        ax.set_xlim(ax.get_xlim()[0] - 0.1, ax.get_xlim()[1] + 0.1)
        ax.set_ylim(ax.get_ylim()[0] - 0.1, ax.get_ylim()[1] + 0.1)
        
        # Asegurarse de que el directorio 'img' exista
        try:
            os.makedirs(os.path.dirname(self.ruta_temp), exist_ok=True)
        except Exception as e:
            print(f"Error al crear el directorio para el diagrama: {e}") # Opcional para depuración
            # Podrías mostrar un mensaje al usuario aquí si la creación falla
            self.info_label.configure(text=f"Error al preparar la ruta para guardar el diagrama: {e}")
            return

        # Guardar la figura temporalmente
        if os.path.exists(self.ruta_temp):
            try:
                os.remove(self.ruta_temp)
            except:
                pass # Si no se puede borrar, savefig lo sobrescribirá
        
        plt.savefig(self.ruta_temp, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        
        # Actualizar el estado antes de mostrar el diagrama
        self.diagrama_generado = True
        
        # Mostrar el diagrama en la interfaz
        self.mostrar_diagrama()
        
        # Crear una nueva etiqueta de información después de mostrar el diagrama
        self.info_label = ctk.CTkLabel(
            self.frame_diagrama,
            text="Diagrama generado exitosamente !!!",
            wraplength=600
        )
        self.info_label.pack(pady=5)

    def mostrar_diagrama(self):
        # Limpiar el frame de diagrama
        for widget in self.frame_diagrama.winfo_children():
            widget.destroy()
        
        # Cargar la imagen del diagrama
        try:
            self.original_img = Image.open(self.ruta_temp)
            self.img_width, self.img_height = self.original_img.size
            
            # Crear un frame para contener la imagen y la información detallada
            frame_contenido = ctk.CTkFrame(self.frame_diagrama)
            frame_contenido.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Frame para la imagen con zoom
            frame_imagen = ctk.CTkFrame(frame_contenido)
            frame_imagen.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            
            # Canvas para la imagen con zoom y desplazamiento
            self.canvas_frame = ctk.CTkFrame(frame_imagen)
            self.canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Canvas para mostrar la imagen con capacidad de zoom y desplazamiento
            self.canvas = Canvas(self.canvas_frame, bg="#2b2b2b", highlightthickness=0)
            self.canvas.pack(fill="both", expand=True)
            
            # Crear scrollbars pero usando place para superponerlos sobre el canvas
            h_scrollbar = Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
            v_scrollbar = Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
            
            # Usar place para superponer los scrollbars sobre el canvas
            h_scrollbar.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw", height=15)
            v_scrollbar.place(relx=1.0, rely=0, relheight=1.0, anchor="ne", width=15)
            
            self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
            
            # Configurar eventos del canvas para zoom y desplazamiento
            self.canvas.bind("<ButtonPress-1>", self.start_pan)
            self.canvas.bind("<B1-Motion>", self.pan_image)
            self.canvas.bind("<ButtonRelease-1>", self.stop_pan)
            self.canvas.bind("<MouseWheel>", self.zoom_with_mouse)  # Para Windows
            
            # Mostrar la imagen inicial
            self.update_image()
            
            # Frame para mostrar detalles de las tablas
            frame_detalles = ctk.CTkFrame(frame_contenido)
            frame_detalles.pack(side="right", fill="both", expand=True, padx=5, pady=5)
            
            # Título para el panel de detalles
            ctk.CTkLabel(
                frame_detalles,
                text="Detalles de las tablas",
                font=("Arial", 14, "bold")
            ).pack(pady=5)
            
            # Obtener la estructura de las tablas para mostrar detalles
            estructura = self.obtener_estructura_tablas()
            
            # Crear un combobox para seleccionar la tabla
            ctk.CTkLabel(frame_detalles, text="Selecciona una tabla:").pack(pady=5)
            combo_tablas = ctk.CTkComboBox(
                frame_detalles,
                values=list(estructura.keys()),
                command=self.mostrar_detalles_tabla
            )
            combo_tablas.pack(pady=5)
            
            # Frame para mostrar los detalles de la tabla seleccionada
            self.frame_info_tabla = ctk.CTkScrollableFrame(frame_detalles, height=300)
            self.frame_info_tabla.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Etiqueta inicial
            self.label_info_tabla = ctk.CTkLabel(
                self.frame_info_tabla,
                text="Selecciona una tabla para ver sus detalles",
                wraplength=300
            )
            self.label_info_tabla.pack(pady=10)
            
            # Guardar la estructura para acceder desde el callback
            self.estructura_tablas = estructura
            
            # Agregar etiqueta informativa
            ctk.CTkLabel(
                frame_imagen,
                text="Usa el ratón para mover y la rueda para hacer zoom",
                font=("Arial", 10)
            ).pack(pady=5)
            
        except Exception as e:
            self.info_label = ctk.CTkLabel(
                self.frame_diagrama,
                text=f"Error al mostrar el diagrama: {str(e)}",
                wraplength=600
            )
            self.info_label.pack(pady=20)
            
    def mostrar_detalles_tabla(self, tabla_seleccionada):
        """Muestra los detalles de la tabla seleccionada"""
        # Limpiar el frame de información
        for widget in self.frame_info_tabla.winfo_children():
            widget.destroy()
        
        if not tabla_seleccionada or tabla_seleccionada not in self.estructura_tablas:
            ctk.CTkLabel(
                self.frame_info_tabla,
                text="Tabla no encontrada",
                wraplength=300
            ).pack(pady=10)
            return
        
        # Mostrar información de la tabla
        info_tabla = self.estructura_tablas[tabla_seleccionada]
        
        # Título de la tabla
        ctk.CTkLabel(
            self.frame_info_tabla,
            text=f"Tabla: {tabla_seleccionada}",
            font=("Arial", 12, "bold"),
            wraplength=300
        ).pack(pady=5)
        
        # Mostrar columnas
        ctk.CTkLabel(
            self.frame_info_tabla,
            text="Columnas:",
            font=("Arial", 11, "bold"),
            wraplength=300
        ).pack(pady=5, anchor="w")
        
        # Crear un frame para las columnas con estilo de tabla
        frame_columnas = ctk.CTkFrame(self.frame_info_tabla)
        frame_columnas.pack(fill="x", padx=5, pady=5)
        
        # Mostrar cada columna con sus detalles
        for columna in info_tabla['columnas']:
            nombre = columna[0]
            tipo = columna[1]
            nulo = 'NULL' if columna[2] == 'YES' else 'NOT NULL'
            clave = 'PK' if columna[3] == 'PRI' else ''
            
            # Crear un frame para cada fila de la tabla
            frame_fila = ctk.CTkFrame(frame_columnas)
            frame_fila.pack(fill="x", pady=2)
            
            # Colorear diferente las claves primarias
            bg_color = "#4CAF50" if clave == 'PK' else None
            
            # Mostrar los detalles de la columna
            ctk.CTkLabel(
                frame_fila,
                text=nombre,
                width=100,
                fg_color=bg_color
            ).pack(side="left", padx=2)
            
            ctk.CTkLabel(
                frame_fila,
                text=tipo,
                width=100
            ).pack(side="left", padx=2)
            
            ctk.CTkLabel(
                frame_fila,
                text=nulo,
                width=80
            ).pack(side="left", padx=2)
            
            if clave:
                ctk.CTkLabel(
                    frame_fila,
                    text=clave,
                    width=40,
                    fg_color="#4CAF50"
                ).pack(side="left", padx=2)
        
        # Mostrar relaciones
        if info_tabla['relaciones']:
            ctk.CTkLabel(
                self.frame_info_tabla,
                text="Relaciones:",
                font=("Arial", 11, "bold"),
                wraplength=300
            ).pack(pady=5, anchor="w")
            
            # Crear un frame para las relaciones
            frame_relaciones = ctk.CTkFrame(self.frame_info_tabla)
            frame_relaciones.pack(fill="x", padx=5, pady=5)
            
            for relacion in info_tabla['relaciones']:
                columna_origen = relacion[0]
                tabla_destino = relacion[1]
                columna_destino = relacion[2]
                
                # Crear un frame para cada relación
                frame_relacion = ctk.CTkFrame(frame_relaciones)
                frame_relacion.pack(fill="x", pady=2)
                
                # Mostrar la relación
                ctk.CTkLabel(
                    frame_relacion,
                    text=f"{columna_origen} → {tabla_destino}.{columna_destino}",
                    fg_color="#9C27B0",
                    text_color="white"
                ).pack(fill="x", padx=2, pady=2)
        else:
            ctk.CTkLabel(
                self.frame_info_tabla,
                text="Esta tabla no tiene relaciones con otras tablas",
                wraplength=300
            ).pack(pady=5)

    # Métodos para zoom y desplazamiento
    def update_image(self):
        # Aplicar zoom a la imagen original
        new_width = int(self.img_width * self.zoom_factor)
        new_height = int(self.img_height * self.zoom_factor)
        
        # Redimensionar la imagen con el factor de zoom
        resized_img = self.original_img.resize((new_width, new_height), Image.LANCZOS)
        
        # Convertir a formato compatible con tkinter
        self.tk_img = ImageTk.PhotoImage(resized_img)
        
        # Actualizar el canvas
        self.canvas.delete("all")
        self.canvas.create_image(self.pan_x, self.pan_y, anchor="nw", image=self.tk_img, tags="img")
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def zoom_in(self):
        self.zoom_factor *= 1.2
        self.update_image()
    
    def zoom_out(self):
        self.zoom_factor = max(0.1, self.zoom_factor / 1.2)
        self.update_image()
    
    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.update_image()
    
    def start_pan(self, event):
        self.is_panning = True
        self.start_x = event.x
        self.start_y = event.y
    
    def pan_image(self, event):
        if self.is_panning:
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            self.pan_x += dx
            self.pan_y += dy
            self.start_x = event.x
            self.start_y = event.y
            self.update_image()
    
    def stop_pan(self, event):
        self.is_panning = False
    
    def zoom_with_mouse(self, event):
        # Zoom con la rueda del ratón
        if event.delta > 0:
            self.zoom_factor *= 1.1
        else:
            self.zoom_factor = max(0.1, self.zoom_factor / 1.1)
        self.update_image()
    
    def exportar_diagrama(self):
        if not self.diagrama_generado:
            self.info_label = ctk.CTkLabel(
                self.frame_diagrama,
                text="Primero debes generar un diagrama",
                wraplength=600
            )
            self.info_label.pack(pady=20)
            return

        archivo = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")]
        )

        if archivo:
            try:
                # Copiar el archivo temporal al destino seleccionado
                from shutil import copyfile
                copyfile(self.ruta_temp, archivo)
                
                # Mostrar mensaje de éxito
                ctk.CTkLabel(
                    self.canvas_frame,
                    text=f"Diagrama exportado exitosamente a {archivo}",
                    wraplength=600
                ).pack(pady=5)
            except Exception as e:
                ctk.CTkLabel(
                    self.canvas_frame,
                    text=f"Error al exportar el diagrama: {str(e)}",
                    wraplength=600
                ).pack(pady=5)
    
    def activar_modo_interactivo(self):
        if not self.modo_interactivo:
            # Desactivar los eventos de pan y zoom normales
            self.canvas.unbind("<ButtonPress-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
            self.canvas.unbind("<MouseWheel>")
            
            # Activar los eventos de arrastre de tablas
            self.canvas.bind("<ButtonPress-1>", self.iniciar_arrastre_nodo)
            self.canvas.bind("<B1-Motion>", self.arrastrar_nodo)
            self.canvas.bind("<ButtonRelease-1>", self.finalizar_arrastre_nodo)
            
            self.modo_interactivo = True
            self.btn_modo_interactivo.configure(text="Activar Interactivo")
            self.info_label.configure(text="Modo Interactivo desactivado")
        else:
            # Restaurar los eventos de pan y zoom normales
            self.canvas.bind("<ButtonPress-1>", self.start_pan)
            self.canvas.bind("<B1-Motion>", self.pan_image)
            self.canvas.bind("<ButtonRelease-1>", self.stop_pan)
            self.canvas.bind("<MouseWheel>", self.zoom_with_mouse)
            
            self.modo_interactivo = False
            self.btn_modo_interactivo.configure(text="Desactivar Interactivo")
            self.info_label.configure(text="Modo interactivo activado. Haz clic y arrastra para mover la imagen.")

    def iniciar_arrastre_nodo(self, event):
        """Inicia el arrastre de un nodo"""
        self.start_x = event.x
        self.start_y = event.y
        self.nodo_seleccionado = None
        
        # Encontrar el nodo más cercano al punto de clic
        if self.grafo and self.posiciones:
            # Convertir coordenadas del canvas a coordenadas del grafo
            canvas_coords = (event.x, event.y)
            # Aquí implementarías la lógica para encontrar el nodo más cercano
            # Por ahora, simplemente guardamos las coordenadas iniciales
            self.nodo_seleccionado = canvas_coords

    def arrastrar_nodo(self, event):
        """Arrastra el nodo seleccionado"""
        if self.nodo_seleccionado:
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            self.start_x = event.x
            self.start_y = event.y
            # Aquí implementarías la lógica para mover el nodo
            # Por ahora, solo actualizamos las coordenadas
            self.nodo_seleccionado = (event.x, event.y)

    def finalizar_arrastre_nodo(self, event):
        """Finaliza el arrastre del nodo"""
        if self.nodo_seleccionado:
            # Aquí implementarías la lógica para finalizar el movimiento del nodo
            self.nodo_seleccionado = None
            
            # Desactivar eventos de arrastre
            self.canvas.unbind("<ButtonPress-1>")
            self.canvas.unbind("<B1-Motion>")

    
    def iniciar_mover_nodo(self, event):
        """Inicia el movimiento de un nodo"""
        if not self.modo_interactivo or not self.grafo or not self.posiciones:
            return
            
        # Convertir coordenadas del canvas a coordenadas del grafo
        x, y = self.canvas_a_grafo_coords(event.x, event.y)
        
        # Buscar el nodo más cercano
        nodo_cercano = None
        distancia_min = float('inf')
        
        for nodo, (nx, ny) in self.posiciones.items():
            distancia = ((nx - x) ** 2 + (ny - y) ** 2) ** 0.5
            if distancia < distancia_min and distancia < 0.2:  # Umbral de distancia
                distancia_min = distancia
                nodo_cercano = nodo
        
        self.nodo_seleccionado = nodo_cercano
        if nodo_cercano:
            self.start_x, self.start_y = x, y
    
    def mover_nodo(self, event):
        """Mueve el nodo seleccionado"""
        if not self.modo_interactivo or not self.nodo_seleccionado:
            return
            
        # Convertir coordenadas del canvas a coordenadas del grafo
        x, y = self.canvas_a_grafo_coords(event.x, event.y)
        
        # Calcular el desplazamiento
        dx = x - self.start_x
        dy = y - self.start_y
        
        # Actualizar la posición del nodo
        nx, ny = self.posiciones[self.nodo_seleccionado]
        self.posiciones[self.nodo_seleccionado] = (nx + dx, ny + dy)
        
        # Actualizar las coordenadas iniciales
        self.start_x, self.start_y = x, y
        
        # Redibujar el diagrama
        self.actualizar_diagrama_interactivo()
    
    def finalizar_mover_nodo(self, event):
        """Finaliza el movimiento del nodo"""
        self.nodo_seleccionado = None
    
    def canvas_a_grafo_coords(self, canvas_x, canvas_y):
        """Convierte coordenadas del canvas a coordenadas del grafo"""
        # Esta es una conversión aproximada que deberás ajustar según tu implementación
        # Depende de cómo estés dibujando el grafo en el canvas
        x = canvas_x / self.canvas.winfo_width() * 2 - 1
        y = -(canvas_y / self.canvas.winfo_height() * 2 - 1)
        return x, y
    
    def actualizar_diagrama_interactivo(self):
        """Actualiza el diagrama con las nuevas posiciones de los nodos"""
        if not self.grafo or not self.posiciones:
            return
            
        # Limpiar la figura actual
        plt.clf()
        
        # Redibujar el diagrama con las nuevas posiciones       
        # Guardar y mostrar el diagrama actualizado
        plt.savefig(self.ruta_temp, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        
        # Actualizar la imagen en el canvas
        self.update_image()
        # Dibujar aristas después de los nodos para que aparezcan por encima
        nx.draw_networkx_edges(G, pos, edge_color='#9C27B0', arrows=True, arrowsize=20, width=1.5, alpha=0.9)
        
        # Dibujar etiquetas de aristas (relaciones) con mejor formato
        edge_labels = {(u, v): G[u][v]['label'] for u, v in G.edges()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, font_color='#D81B60')
        
        # Ajustar el diseño
        plt.axis('off')
        plt.tight_layout()
        
        # Asegurar que todo el gráfico esté visible dentro de los límites
        ax = plt.gca()
        ax.set_xlim(ax.get_xlim()[0] - 0.1, ax.get_xlim()[1] + 0.1)
        ax.set_ylim(ax.get_ylim()[0] - 0.1, ax.get_ylim()[1] + 0.1)
        
        # Asegurarse de que el directorio 'img' exista
        try:
            os.makedirs(os.path.dirname(self.ruta_temp), exist_ok=True)
        except Exception as e:
            print(f"Error al crear el directorio para el diagrama: {e}") # Opcional para depuración
            # Podrías mostrar un mensaje al usuario aquí si la creación falla
            self.info_label.configure(text=f"Error al preparar la ruta para guardar el diagrama: {e}")
            return

        # Guardar la figura temporalmente
        if os.path.exists(self.ruta_temp):
            try:
                os.remove(self.ruta_temp)
            except:
                pass # Si no se puede borrar, savefig lo sobrescribirá
        
        plt.savefig(self.ruta_temp, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        
  