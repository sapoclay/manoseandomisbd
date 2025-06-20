# ManoseandoMisBD Versión: 0.01

![about](https://github.com/user-attachments/assets/85785ebd-ce61-4b86-9e3a-8a037f8159bb)

Se trata de una aplicación de escritorio moderna y sencilla para la gestión, visualización y consulta de bases de datos MySQL. 
Ha sido diseñada para hacer las consultas y el análisis de datos más accesible mediante una interfaz gráfica intuitiva que ha sido creada con tkinter y customtkinter. Además cuenta con capacidades de procesamiento de lenguaje natural para que incluso si no tienes ni idea de SQL puedas realizar consultas u operaciones con la base de datos SQL.

## Características principales

- 🔗 **Gestión de conexiones MySQL** - Conexión y gestión intuitiva de bases de datos. Por el momento SOLO SQL
- 📊 **Visualización de datos** - Generación de gráficos interactivos con Matplotlib
- 📝 **Editor SQL** - Editor de consultas con resaltado de sintaxis y gestión de sentencias favoritas
- 🤖 **Consultas en lenguaje natural** - Utiliza IA (Gemini, gemini-2.0-flash que es gratuita) para traducir preguntas en español a SQL. No se envían los datos a Gemini, solo la estructura de la Base de Datos
- 🎨 **Interfaz moderna** - Diseño elegante y responsive con CustomTkinter
- 🔄 **Monitoreo en tiempo Real** - Estado del servidor y conexiones en tiempo real
- 🌍 **Soporte multilingüe** - Interfaz en español

## Requisitos previos

- Python 3.12 o superior
- MySQL Server 8.0 o superior
- Acceso a la API de Google Cloud (para funcionalidades de Gemini)
- Sistemas operativos probados: Windows y Gnu/Linux

## Instalación

1. Clonar el repositorio:
```powershell
git clone https://github.com/sapoclay/manoseandomisbd.git
cd ManoseandoMisBD
```

2. Crear y activar un entorno virtual (en Windows esto es opcional):
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

3. Instalar dependencias:
```powershell
pip install -r requirements.txt
```

4. Inicia el programa:
```powershell
python main.py
```

## Configuración

1. **MySQL Server**
   - Asegúrate de que MySQL Server esté instalado y ejecutándose en el puerto 3306
   - Crea un usuario con los permisos necesarios y su contraseña correspondiente

2. **Configuración de Gemini**
   - Obtén una API key de Google Cloud Platform
   - Pega SOLO la key en `config/gemini_config.txt` o añádela desde el formulario `Consultas en Lenguaje Natural`

![add-gemini-key](https://github.com/user-attachments/assets/ffe3f911-3938-479d-9db9-bbd9d8e7074b)

   - La API Key se puede obtener en la web  https://ai.google.dev/gemini-api/docs?hl=es-419

## Uso

1. **Ejecutar la aplicación**
```powershell
python main.py
```

2. **Conexión a base de datos**
   - En la pestaña "Conexión", introduce los datos de tu servidor MySQL
   - Click en "Conectar"

3. **Realizar consultas**
   - **SQL Directo**: Usa la pestaña "Consultas SQL"
   - **Lenguaje Natural**: Usa la pestaña "Consultas en Lenguaje Natural"
   - **Visualización**: Genera gráficos en la pestaña "Visualización"

## Capturas

### Pestaña conexión
![conexion](https://github.com/user-attachments/assets/d0007f51-816b-4b5c-94c5-eacfccdedc29)

### Pestaña visualización
![visualizacion](https://github.com/user-attachments/assets/40b5fa96-e49b-43a1-8e12-8e9f0d39e93b)

### Pestaña sentencias sql
![sentencias_sql](https://github.com/user-attachments/assets/002df344-2fc7-4d20-b3ac-8b704e659898)

### Pestaña lenguaje natural
![lenguaje-natural](https://github.com/user-attachments/assets/ce4e4677-0408-4b7a-86fa-b2eda748dca2)

## Estructura del proyecto

```
ManoseandoMisBD/                        # Aplicación de gestión de bases de datos MySQL
│
├── config/                             # Configuración del proyecto
│   ├── consultas_favoritas.json        # Almacena consultas SQL favoritas del usuario
│   └── gemini_config.txt               # Configuración de la API de Gemini
│
├── img/                                # Recursos gráficos
│   ├── diagrama_bd_temp.png            # Imagen temporal para diagramas de BD
│   └── logo_app.jpg                    # Logo de la aplicación
│
├── modulos/                            # Módulos principales de la aplicación
│   ├── __pycache__/                    # Archivos de caché de Python (generados automáticamente)
│   ├── __init__.py                     # Inicializador del paquete
│   ├── acerca_de.py                    # Módulo para la implementación de la pestaña "Acerca de"
│   ├── conexion.py                     # Módulo para la gestión de conexiones MySQL y la pestaña "Conexión"
│   ├── consultas_naturales_gemini.py   # Módulo para el procesamiento de lenguaje natural con Gemini y la pestaña "Lenguaje natural"
│   ├── consultas_sql.py                # Módulo para la gestión de consultas SQL directas y la pestaña "Consultas sql"
│   ├── gemini_api.py                   # Módulo para la integración con API de Gemini
│   └── visualizacion_matplotlib.py     # Módulo para la visualización de datos con Matplotlib
│
│
├── main.py                             # Punto de entrada principal
│                                       # - Implementa la interfaz gráfica principal
│                                       # - Gestiona las pestañas y la interacción entre módulos
│                                       # - Monitorea el estado de la conexión MySQL
│                                       # - Implementa la actualización de fecha/hora
│
└── requirements.txt                    # Lista de dependencias del proyecto
                                        # Dependencias incluidas:
                                        # - customtkinter: Framework moderno para crear interfaces gráficas con Tkinter,
                                        #   proporciona widgets modernos y temas personalizables
                                        # - mysql-connector-python: Conector oficial de MySQL para Python,
                                        #   permite la comunicación con bases de datos MySQL
                                        # - Pillow: Biblioteca para el procesamiento de imágenes,
                                        #   usada para manejar los iconos y gráficos de la interfaz
                                        # - sqlglot: Parser y formateador de SQL,
                                        #   ayuda en el análisis y formateo de consultas SQL
                                        # - matplotlib: Biblioteca de visualización de datos,
                                        #   utilizada para crear gráficos y diagramas interactivos
                                        # - networkx: Biblioteca para crear y manipular grafos,
                                        #   usada en la visualización de relaciones entre tablas
                                        # - requests: Biblioteca para realizar peticiones HTTP,
                                        #   necesaria para la comunicación con la API de Gemini
                                        # - sqlparse: Analizador de SQL,
                                        #   permite formatear y validar consultas SQL
```

## Contribución

1. Fork del repositorio
2. Crear una rama para tu feature:
```powershell
git checkout -b feature/CaracteristicaIncreible
```
3. Commit de los cambios:
```powershell
git commit -m 'Add: CaracteristicaIncreible'
```
4. Push a la rama:
```powershell
git push origin feature/CaracteristicaIncreible
```
5. Abrir un Pull Request

### Convenciones de commits

- `Add:` Nueva funcionalidad
- `Fix:` Corrección de bugs
- `Doc:` Cambios en documentación
- `Style:` Cambios de formato/estilo
- `Refactor:` Refactorización de código
- `Test:` Añadir/modificar tests

## Mejoras a medio y largo plazo

Se planean implementar las siguientes mejoras y características al programa:

### Mejoras en la interfaz
- 🎨 Temas personalizables y modo claro/oscuro configurable
- 📱 Diseño responsive mejorado para diferentes resoluciones de pantalla
- ⌨️ Atajos de teclado personalizables para operaciones comunes
- 📋 Historial de consultas con búsqueda y filtrado

### Funcionalidades de base de datos
- 🔄 Exportación de resultados en múltiples formatos (CSV, Excel, JSON)
- 📊 Más tipos de visualizaciones y gráficos interactivos
- 🔍 Autocompletado mejorado en el editor SQL
- 📝 Editor visual de consultas (Query Builder)
- 🔒 Gestión avanzada de permisos y roles de usuario
- 📦 Soporte para backups y restauración de bases de datos
- 🔄 Sincronización de esquemas entre diferentes bases de datos

### Integración y extensibilidad
- 🔌 Sistema de plugins para extender funcionalidades
- 📤 Integración con herramientas populares de BI
- 🤖 Más modelos de IA para procesamiento de lenguaje natural
- 📱 Versión web para acceso remoto
- 🔗 Soporte para más sistemas de bases de datos (PostgreSQL, SQLite)

### Características avanzadas
- 📈 Análisis de rendimiento de consultas
- 🔍 Herramientas de diagnóstico y optimización
- 📊 Generación automática de informes
- 🤖 Sugerencias inteligentes basadas en el uso
- 📱 Aplicación móvil complementaria

Si tienes alguna sugerencia adicional para futuras versiones, no dudes en abrir un issue o contribuir al proyecto.

## Contacto y soporte

- **Bugs y problemas**: Crear un issue en GitHub
- **Sugerencias**: Abrir una discusión en el repositorio
- **Contacto**: admin@entreunosyceros.net

### ¿Encontraste un bug?

1. Verifica que el bug no haya sido reportado ya en los issues
2. Crea un nuevo issue con:
   - Título claro y descriptivo
   - Pasos para reproducir el error
   - Comportamiento esperado vs actual
   - Screenshots si es posible
   - Información del sistema (OS, versión de Python, etc)

## Licencia

Este proyecto está bajo la licencia [MIT](LICENSE).
