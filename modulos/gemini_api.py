import os
import json
import requests
from typing import Dict, List, Tuple, Optional

class GeminiAPI:
    """Clase para manejar las consultas a la API de Gemini"""
    
    def __init__(self, api_key=None):
        """Inicializa la conexión con la API de Gemini
        
        Args:
            api_key: Clave de API para Gemini. Si no se proporciona, se intentará
                    obtener del archivo de configuración o de la variable de entorno GEMINI_API_KEY.            
                    
        """
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        # Modificar la ruta para que apunte a config/gemini_config.txt
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "gemini_config.txt")
        
        # Intentar cargar la API key del archivo de configuración
        self.api_key = self._cargar_api_key()
        
        # Si no se encontró en el archivo, usar el valor proporcionado o la variable de entorno
        if not self.api_key:
            self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
            
        if not self.api_key:
            print("Advertencia: No se ha proporcionado una clave de API para Gemini.")
    
    def _cargar_api_key(self) -> Optional[str]:
        """Carga la API key desde el archivo de configuración
        
        Returns:
            La API key si existe en el archivo, None en caso contrario
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    return f.read().strip()
        except Exception as e:
            print(f"Error al leer el archivo de configuración: {str(e)}")
        return None
    
    def set_api_key(self, api_key: str) -> None:
        """Establece la clave de API para Gemini y la guarda en el archivo de configuración
        
        Args:
            api_key: Clave de API para Gemini
        """
        self.api_key = api_key
        try:
            # Asegurarse de que el directorio 'config' exista
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w") as f:
                f.write(api_key)
        except Exception as e:
            print(f"Error al guardar la API key: {str(e)}")
    
    def traducir_a_sql(self, consulta_natural: str, estructura_bd: Dict) -> Optional[str]:
        """Traduce una consulta en lenguaje natural a SQL utilizando Gemini
        
        Args:
            consulta_natural: Consulta en lenguaje natural
            estructura_bd: Diccionario con la estructura de la base de datos
                          {tabla: {columnas: [...], relaciones: [...]}}
        
        Returns:
            Consulta SQL generada o None si hubo un error
        """
        if not self.api_key:
            return None
        
        # Formatear la estructura de la base de datos para enviarla a Gemini
        estructura_formateada = self._formatear_estructura_bd(estructura_bd)
        
        # Construir el prompt para Gemini
        prompt = f"""Actúa como un experto en bases de datos MySQL. Traduce la siguiente consulta en lenguaje natural a una consulta SQL válida para la estructura de la base de datos proporcionada. Utiliza la estructura de la base de datos que te proporciono. Asegúrate de que la consulta sea válida y compatible con MySQL.

Estructura de la base de datos:
{estructura_formateada}

Consulta en lenguaje natural:
{consulta_natural}

Genera ÚNICAMENTE el código SQL sin explicaciones adicionales. La consulta debe ser compatible con MySQL.

En caso de que alguna tabla consultada no exista, genera ÚNICAMENTE el código SQL de alguna tabla que si exista, sin explicaciones adicionales. Esta consulta debe ser compatible con MYSQL.
"""
        
        try:
            # Preparar la solicitud para la API de Gemini
            headers = {
                "Content-Type": "application/json",
            }
            
            params = {
                "key": self.api_key
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            # Realizar la solicitud a la API
            response = requests.post(
                self.api_url,
                headers=headers,
                params=params,
                json=data
            )
            
            # Verificar si la solicitud fue exitosa
            if response.status_code == 200:
                response_data = response.json()
                
                # Extraer la consulta SQL generada
                if 'candidates' in response_data and len(response_data['candidates']) > 0:
                    candidate = response_data['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        for part in candidate['content']['parts']:
                            if 'text' in part:
                                # Limpiar la respuesta para obtener solo la consulta SQL
                                sql = part['text'].strip()
                                # Eliminar comillas de código si existen
                                if sql.startswith('```sql'):
                                    sql = sql[6:]
                                if sql.startswith('```'):
                                    sql = sql[3:]
                                if sql.endswith('```'):
                                    sql = sql[:-3]
                                return sql.strip()
                
                return None
            else:
                print(f"Error en la API de Gemini: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error al comunicarse con la API de Gemini: {str(e)}")
            return None
    
    def _formatear_estructura_bd(self, estructura: Dict) -> str:
        """Formatea la estructura de la base de datos para enviarla a Gemini
        
        Args:
            estructura: Diccionario con la estructura de la base de datos
                      {tabla: {columnas: [...], relaciones: [...]}}
        
        Returns:
            Texto formateado con la estructura de la base de datos
        """
        resultado = ""
        
        # Iterar sobre cada tabla
        for tabla, info in estructura.items():
            resultado += f"Tabla: {tabla}\n"
            
            # Agregar columnas
            resultado += "Columnas:\n"
            for columna in info['columnas']:
                nombre = columna[0]
                tipo = columna[1]
                nulo = 'NULL' if columna[2] == 'YES' else 'NOT NULL'
                clave = 'PRIMARY KEY' if columna[3] == 'PRI' else ''
                resultado += f"  - {nombre}: {tipo} {nulo} {clave}\n"
            
            # Agregar relaciones
            if info['relaciones']:
                resultado += "Relaciones:\n"
                for relacion in info['relaciones']:
                    columna_origen = relacion[0]
                    tabla_destino = relacion[1]
                    columna_destino = relacion[2]
                    resultado += f"  - {columna_origen} -> {tabla_destino}.{columna_destino}\n"
            
            resultado += "\n"
        
        return resultado