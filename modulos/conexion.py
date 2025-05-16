import customtkinter as ctk
import mysql.connector
from mysql.connector import Error
from typing import List, Tuple, Optional

class PestanaConexion(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.conexion = None
        self.cursor = None
        self.crear_widgets()

    def crear_widgets(self):
        # Frame para los datos de conexión con scroll vertical
        frame_conexion = ctk.CTkScrollableFrame(self)
        frame_conexion.pack(padx=20, pady=20, fill="both", expand=True)

        # Frame izquierdo para conexión
        frame_izquierdo = ctk.CTkFrame(frame_conexion)
        frame_izquierdo.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        # Etiquetas y campos de entrada en el frame izquierdo
        ctk.CTkLabel(frame_izquierdo, text="Servidor:").grid(row=0, column=0, padx=5, pady=5)
        self.servidor = ctk.CTkEntry(frame_izquierdo)
        self.servidor.insert(0, "localhost")
        self.servidor.grid(row=0, column=1, padx=5, pady=5)
    
        ctk.CTkLabel(frame_izquierdo, text="Puerto:").grid(row=1, column=0, padx=5, pady=5)
        self.puerto = ctk.CTkEntry(frame_izquierdo)
        self.puerto.insert(0, "3306")
        self.puerto.grid(row=1, column=1, padx=5, pady=5)
    
        ctk.CTkLabel(frame_izquierdo, text="Usuario:").grid(row=2, column=0, padx=5, pady=5)
        self.usuario = ctk.CTkEntry(frame_izquierdo)
        self.usuario.insert(0, "root")
        self.usuario.grid(row=2, column=1, padx=5, pady=5)
    
        ctk.CTkLabel(frame_izquierdo, text="Contraseña:").grid(row=3, column=0, padx=5, pady=5)
        self.contrasena = ctk.CTkEntry(frame_izquierdo, show="*")
        self.contrasena.grid(row=3, column=1, padx=5, pady=5)
    
        # Combobox para bases de datos
        ctk.CTkLabel(frame_izquierdo, text="Base de datos:").grid(row=4, column=0, padx=5, pady=5)
        self.combo_bd = ctk.CTkOptionMenu(frame_izquierdo, values=[""])
        self.combo_bd.grid(row=4, column=1, padx=5, pady=5)
        self.combo_bd.configure(state="disabled")
    
        # Botones de conexión
        frame_botones = ctk.CTkFrame(frame_izquierdo)
        frame_botones.grid(row=5, column=0, columnspan=2, pady=10)
        
        self.btn_conectar = ctk.CTkButton(frame_botones, text="Conectar al Servidor", command=self.conectar)
        self.btn_conectar.pack(side="left", padx=5)
        
        self.btn_desconectar = ctk.CTkButton(frame_botones, text="Desconectar", command=self.desconectar_servidor, state="disabled")
        self.btn_desconectar.pack(side="left", padx=5)
        # Estado de la conexión
        self.estado_label = ctk.CTkLabel(frame_izquierdo, text="Estado: No conectado", text_color="red")
        self.estado_label.grid(row=6, column=0, columnspan=2, pady=5)
    
        # Frame derecho para crear base de datos
        frame_derecho = ctk.CTkFrame(frame_conexion)
        frame_derecho.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        # Widgets para crear base de datos
        ctk.CTkLabel(frame_derecho, text="Crear Nueva Base de Datos", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        ctk.CTkLabel(frame_derecho, text="Nombre:").grid(row=1, column=0, padx=5, pady=5)
        self.nueva_bd = ctk.CTkEntry(frame_derecho)
        self.nueva_bd.grid(row=1, column=1, padx=5, pady=5)
        
        self.btn_crear_bd = ctk.CTkButton(frame_derecho, text="Crear Base de Datos", command=self.crear_base_datos, state="disabled")
        self.btn_crear_bd.grid(row=2, column=0, columnspan=2, pady=10)
    
        # Frame para eliminar base de datos
        frame_eliminar = ctk.CTkFrame(frame_conexion)
        frame_eliminar.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")
        
        # Widgets para eliminar base de datos
        ctk.CTkLabel(frame_eliminar, text="Eliminar Base de Datos", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        ctk.CTkLabel(frame_eliminar, text="Seleccionar BD:").grid(row=1, column=0, padx=5, pady=5)
        self.combo_eliminar_bd = ctk.CTkOptionMenu(frame_eliminar, values=[""])
        self.combo_eliminar_bd.grid(row=1, column=1, padx=5, pady=5)
        self.combo_eliminar_bd.configure(state="disabled")
        
        self.btn_eliminar_bd = ctk.CTkButton(frame_eliminar, text="Eliminar Base de Datos", 
                                            command=self.eliminar_base_datos, 
                                            state="disabled",
                                            fg_color="red",
                                            hover_color="darkred")
        self.btn_eliminar_bd.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Nueva fila para exportar e importar
        # Frame para exportación de base de datos
        frame_exportar = ctk.CTkFrame(frame_conexion)
        frame_exportar.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        
        # Título para la sección de exportación
        ctk.CTkLabel(
            frame_exportar,
            text="Exportar Base de Datos",
            font=("Arial", 12, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=10)
        
        # ComboBox para seleccionar la base de datos a exportar
        ctk.CTkLabel(frame_exportar, text="Seleccionar BD:").grid(row=1, column=0, padx=5, pady=5)
        self.combo_bd_exportar = ctk.CTkComboBox(
            frame_exportar,
            values=[],
            state="disabled"
        )
        self.combo_bd_exportar.grid(row=1, column=1, padx=5, pady=5)
        
        # Botón para exportar
        self.btn_exportar = ctk.CTkButton(
            frame_exportar,
            text="Exportar como SQL",
            command=self.exportar_base_datos,
            state="disabled"
        )
        self.btn_exportar.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Frame para importación de base de datos
        frame_importar = ctk.CTkFrame(frame_conexion)
        frame_importar.grid(row=1, column=2, columnspan=2, padx=10, pady=5, sticky="nsew")
        
        # Título para la sección de importación
        ctk.CTkLabel(
            frame_importar,
            text="Importar Base de Datos",
            font=("Arial", 12, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Campo para mostrar el archivo seleccionado
        self.archivo_importar = ctk.CTkEntry(frame_importar, state="disabled")
        self.archivo_importar.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        # Botón para seleccionar archivo
        self.btn_seleccionar = ctk.CTkButton(
            frame_importar,
            text="Seleccionar SQL",
            command=self.seleccionar_archivo_sql,
            state="disabled"
        )
        self.btn_seleccionar.grid(row=1, column=1, padx=5, pady=5)
        
        # Botón para importar
        self.btn_importar = ctk.CTkButton(
            frame_importar,
            text="Importar Base de Datos",
            command=self.importar_base_datos,
            state="disabled"
        )
        self.btn_importar.grid(row=2, column=0, columnspan=2, pady=10)

    def actualizar_lista_bd_exportar(self):
        """Actualiza la lista de bases de datos en el combobox de exportación"""
        if self.conexion and self.conexion.is_connected():
            cursor = self.conexion.cursor()
            cursor.execute("SHOW DATABASES")
            bases_datos = [bd[0] for bd in cursor.fetchall()]
            self.combo_bd_exportar.configure(values=bases_datos, state="normal")
            self.btn_exportar.configure(state="normal")
            cursor.close()
        else:
            self.combo_bd_exportar.configure(values=[], state="disabled")
            self.btn_exportar.configure(state="disabled")
            
    def exportar_base_datos(self):
        """Exporta la base de datos seleccionada a un archivo SQL"""
        from tkinter import filedialog, messagebox
        
        bd_seleccionada = self.combo_bd_exportar.get()
        if not bd_seleccionada:
            messagebox.showwarning("Advertencia", "Por favor seleccione una base de datos")
            return
            
        # Abrir diálogo para guardar archivo
        archivo = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL files", "*.sql"), ("All files", "*.*")],
            initialfile=f"{bd_seleccionada}_backup.sql"
        )
        
        if not archivo:
            return
            
        try:
            # Usar mysqldump para exportar la base de datos
            import subprocess
            
            # Obtener credenciales de conexión
            host = self.conexion.server_host
            usuario = self.conexion.user
            password = self.conexion._password  # Acceder al password guardado
            
            # Construir comando mysqldump
            comando = [
                "mysqldump",
                f"--host={host}",
                f"--user={usuario}",
                f"--password={password}",
                "--databases",
                bd_seleccionada,
                "--result-file=" + archivo,
                "--skip-comments",
                "--skip-add-locks"
            ]
            
            # Ejecutar comando
            proceso = subprocess.run(
                comando,
                capture_output=True,
                text=True
            )
            
            if proceso.returncode == 0:
                messagebox.showinfo(
                    "Éxito",
                    f"Base de datos {bd_seleccionada} exportada correctamente a {archivo}"
                )
            else:
                messagebox.showerror(
                    "Error",
                    f"Error al exportar la base de datos:\n{proceso.stderr}"
                )
                
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al exportar la base de datos:\n{str(e)}"
            )
    
    def conectar(self):
        try:
            self.conexion = mysql.connector.connect(
                host=self.servidor.get(),
                port=int(self.puerto.get()),
                user=self.usuario.get(),
                password=self.contrasena.get()
            )
            self.cursor = self.conexion.cursor()
            self.estado_label.configure(text="Estado: Conectado", text_color="green")
            self.actualizar_bases_datos()
            self.combo_bd.configure(state="normal")
            self.btn_desconectar.configure(state="normal")
            self.btn_conectar.configure(state="disabled")
            self.btn_crear_bd.configure(state="normal")
            self.combo_eliminar_bd.configure(state="normal")  # Habilitar combo de eliminar
            self.btn_eliminar_bd.configure(state="normal")    # Habilitar botón de eliminar
            
            # Habilitar controles de importación y exportación
            self.btn_seleccionar.configure(state="normal")
            self.archivo_importar.configure(state="disabled")  # Mantener deshabilitado hasta que se seleccione archivo
            self.btn_importar.configure(state="disabled")      # Se habilitará cuando se seleccione un archivo
            self.combo_bd_exportar.configure(state="normal")  # Habilitar combo de exportación
            self.btn_exportar.configure(state="normal")       # Habilitar botón de exportación
            
            # Actualizar las listas de bases de datos
            self.actualizar_bases_datos()
            self.actualizar_lista_bd_exportar()
            # Notificar a la aplicación principal del cambio de estado
            if hasattr(self.master.master.master, 'actualizar_estado_conexion'):
                self.master.master.master.actualizar_estado_conexion()
        except Error as e:
            self.estado_label.configure(text=f"Error: {str(e)}", text_color="red")

    def actualizar_bases_datos(self) -> None:
        if self.cursor:
            self.cursor.execute("SHOW DATABASES")
            bases_datos = [bd[0] for bd in self.cursor.fetchall()]
            self.combo_bd.configure(values=bases_datos)
            self.combo_eliminar_bd.configure(values=bases_datos)  # Actualizar también el combo de eliminar
            if bases_datos:
                self.combo_bd.set(bases_datos[0])
                self.combo_eliminar_bd.set(bases_datos[0])

    def desconectar_servidor(self):
        if self.conexion:
            if self.cursor:
                self.cursor.close()
                self.cursor = None
            self.conexion.close()
            self.conexion = None
            self.estado_label.configure(text="Estado: No conectado", text_color="red")
            self.combo_bd.configure(state="disabled", values=[""])
            self.combo_bd.set("")
            self.combo_eliminar_bd.configure(state="disabled", values=[""])  # Deshabilitar combo de eliminar
            self.combo_eliminar_bd.set("")
            self.btn_eliminar_bd.configure(state="disabled")  # Deshabilitar botón de eliminar
            self.btn_desconectar.configure(state="disabled")
            self.btn_conectar.configure(state="normal")
            self.btn_crear_bd.configure(state="disabled")
            
            # Deshabilitar controles de importación
            self.btn_seleccionar.configure(state="disabled")
            self.btn_importar.configure(state="disabled")
            self.archivo_importar.configure(state="normal")
            self.archivo_importar.delete(0, 'end')
            self.archivo_importar.configure(state="disabled")
            
            # Notificar a la aplicación principal del cambio de estado
            if hasattr(self.master.master.master, 'actualizar_estado_conexion'):
                self.master.master.master.actualizar_estado_conexion()

    def crear_base_datos(self):
        """Crea una nueva base de datos"""
        if not self.conexion or not self.cursor:
            return
        
        nombre_bd = self.nueva_bd.get().strip()
        if not nombre_bd:
            self.estado_label.configure(text="Error: Nombre de BD vacío", text_color="red")
            return
        
        try:
            # Crear la base de datos
            self.cursor.execute(f"CREATE DATABASE `{nombre_bd}`")
            self.estado_label.configure(text=f"Base de datos '{nombre_bd}' creada con éxito", text_color="green")
            
            # Limpiar el campo de entrada
            self.nueva_bd.delete(0, 'end')
            
            # Actualizar la lista de bases de datos
            self.actualizar_bases_datos()
            
            # Actualizar la lista de bases de datos para exportar
            self.actualizar_lista_bd_exportar()
            
            # Seleccionar la nueva base de datos en el combobox
            self.combo_bd.set(nombre_bd)
        except Error as e:
            self.estado_label.configure(text=f"Error al crear BD: {str(e)}", text_color="red")

    def eliminar_base_datos(self):
        """Elimina la base de datos seleccionada"""
        if not self.conexion or not self.cursor:
            return
        
        nombre_bd = self.combo_eliminar_bd.get().strip()
        if not nombre_bd:
            self.estado_label.configure(text="Error: No se ha seleccionado una BD", text_color="red")
            return
        
        # Mostrar diálogo de confirmación
        dialog = ctk.CTkInputDialog(
            text=f"¿Está seguro de que desea eliminar la base de datos '{nombre_bd}'?\nEscriba 'CONFIRMAR' para continuar:",
            title="Confirmar eliminación"
        )
        respuesta = dialog.get_input()
        
        if respuesta == "CONFIRMAR":
            try:
                self.cursor.execute(f"DROP DATABASE `{nombre_bd}`")
                self.estado_label.configure(text=f"Base de datos '{nombre_bd}' eliminada con éxito", text_color="green")
                self.actualizar_bases_datos()
                # Actualizar la lista de bases de datos para exportar
                self.actualizar_lista_bd_exportar()
            except Error as e:
                self.estado_label.configure(text=f"Error al eliminar BD: {str(e)}", text_color="red")
        else:
            self.estado_label.configure(text="Eliminación cancelada", text_color="orange")
            
            # Notificar a la aplicación principal del cambio de estado
            if hasattr(self.master.master.master, 'actualizar_estado_conexion'):
                self.master.master.master.actualizar_estado_conexion()

    def obtener_conexion_actual(self) -> Tuple[Optional[mysql.connector.connection.MySQLConnection], Optional[mysql.connector.cursor.MySQLCursor]]:
        return self.conexion, self.cursor

    def obtener_base_datos_actual(self) -> str:
        return self.combo_bd.get()
        
    def desconectar_servidor(self) -> None:
        if self.conexion:
            if self.cursor:
                self.cursor.close()
                self.cursor = None
            self.conexion.close()
            self.conexion = None
            self.estado_label.configure(text="Estado: No conectado", text_color="red")
            self.combo_bd.configure(state="disabled", values=[""])
            self.combo_bd.set("")
            self.combo_eliminar_bd.configure(state="disabled", values=[""])  # Deshabilitar combo de eliminar
            self.combo_eliminar_bd.set("")
            self.btn_eliminar_bd.configure(state="disabled")  # Deshabilitar botón de eliminar
            self.btn_desconectar.configure(state="disabled")
            self.btn_conectar.configure(state="normal")
            self.btn_crear_bd.configure(state="disabled")
            
            # Notificar a la aplicación principal del cambio de estado
            if hasattr(self.master.master.master, 'actualizar_estado_conexion'):
                self.master.master.master.actualizar_estado_conexion()
        
        # Después de establecer la conexión exitosamente
        self.actualizar_lista_bd_exportar()
    
    def seleccionar_archivo_sql(self):
        """Permite seleccionar un archivo SQL para importar"""
        from tkinter import filedialog
        
        archivo = filedialog.askopenfilename(
            defaultextension=".sql",
            filetypes=[("SQL files", "*.sql"), ("All files", "*.*")]
        )
        
        if archivo:
            self.archivo_importar.configure(state="normal")
            self.archivo_importar.delete(0, 'end')
            self.archivo_importar.insert(0, archivo)
            self.archivo_importar.configure(state="disabled")
            self.btn_importar.configure(state="normal")
            
    def importar_base_datos(self):
        """Importa una base de datos desde un archivo SQL"""
        from tkinter import messagebox
        import subprocess
        
        archivo = self.archivo_importar.get()
        if not archivo:
            messagebox.showwarning("Advertencia", "Por favor selecciona un archivo SQL")
            return
            
        try:
            # Obtener credenciales de conexión
            host = self.conexion.server_host
            usuario = self.conexion.user
            password = self.conexion._password
            
            # Construir comando mysql
            comando = [
                "mysql",
                f"--host={host}",
                f"--user={usuario}",
                f"--password={password}"
            ]
            
            # Ejecutar comando
            with open(archivo, 'r', encoding='utf-8') as f:
                proceso = subprocess.run(
                    comando,
                    input=f.read(),
                    text=True,
                    capture_output=True
                )
            
            if proceso.returncode == 0:
                messagebox.showinfo(
                    "Éxito",
                    "Base de datos importada correctamente"
                )
                self.actualizar_bases_datos()
                self.actualizar_lista_bd_exportar()
            else:
                messagebox.showerror(
                    "Error",
                    f"Error al importar la base de datos:\n{proceso.stderr}"
                )
                
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al importar la base de datos:\n{str(e)}"
            )

