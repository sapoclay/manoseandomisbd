import customtkinter as ctk
import webbrowser

class PestanaAcercaDe(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.crear_widgets()

    def crear_widgets(self):
        # Frame principal con scroll vertical
        frame_principal = ctk.CTkScrollableFrame(self)
        frame_principal.pack(expand=True, fill="both", padx=20, pady=20)

        # Título
        titulo = ctk.CTkLabel(
            frame_principal,
            text="Manoseando mis Bases de Datos MySQL",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        titulo.pack(pady=20)

        # Descripción del programa
        descripcion = """
        Esta aplicación permite visualizar y gestionar bases de datos MySQL de manera gráfica e intuitiva.
        
        Características principales:
        • Conexión a servidores MySQL locales y remotos
        • Creación y eliminación de bases de datos
        • Gestión de tablas, campos y registros
        • Visualización gráfica de la estructura de bases de datos
        • Generación de diagramas de relaciones entre tablas
        • Exportación de diagramas en formato PNG
        • Ejecución de consultas SQL, con sugerencias y coloreado de sintaxis (básico)
        • Consultas en lenguaje natural (Gracias a Pablo por la idea)
        • Para las consultas en lenguaje natura es necesario tener una clave API de Gemini https://ai.google.dev/gemini-api/docs?hl=es-419
        
        Desarrollado con café, Python, tkinter y customtkinter.
        """

        descripcion_label = ctk.CTkLabel(
            frame_principal,
            text=descripcion,
            wraplength=600,
            justify="left"
        )
        descripcion_label.pack(pady=20)

        # Cargar imagen del logo
        try:
            from PIL import Image
            logo_img = ctk.CTkImage(light_image=Image.open("img/logo_app.jpg"),
                                   dark_image=Image.open("img/logo_app.jpg"),
                                   size=(300, 150))
            
            # Mostrar la imagen del logo
            logo_label = ctk.CTkLabel(frame_principal, text="", image=logo_img)
            logo_label.pack(pady=10)
        except Exception as e:
            # En caso de error, mostrar un mensaje en lugar de la imagen
            error_label = ctk.CTkLabel(frame_principal, text="No se pudo cargar la imagen del logo")
            error_label.pack(pady=10)

        # Botón para abrir el repositorio
        btn_repo = ctk.CTkButton(
            frame_principal,
            text="Visitar Repositorio en GitHub",
            command=lambda: webbrowser.open("https://github.com/sapoclay/manoseandomisbd.git")
        )
        btn_repo.pack(pady=20)

        # Versión
        version_label = ctk.CTkLabel(
            frame_principal,
            text="Versión 0.0.1"
        )
        version_label.pack(pady=10)