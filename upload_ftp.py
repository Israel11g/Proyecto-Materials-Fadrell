import ftplib
import os
from pathlib import Path
from datetime import datetime

# Configuración FTP - REEMPLAZA CON TUS DATOS REALES
FTP_SERVER = 'ftp.tudominio.com'
FTP_USERNAME = 'tu_usuario_ftp'
FTP_PASSWORD = 'tu_contraseña_ftp'

# Directorios a crear en el servidor FTP
DIRECTORIES = [
    'materials_fadrell',
    'materials_fadrell/static',
    'materials_fadrell/media',
    'materials_fadrell/templates',
    'materials_fadrell/webapp',
    'materials_fadrell/webapp/migrations'
]

# Archivos a subir
FILES_TO_UPLOAD = [
    'manage.py',
    'requirements.txt',
    '.env',
    'materials_fadrell/__init__.py',
    'materials_fadrell/settings.py',
    'materials_fadrell/urls.py',
    'materials_fadrell/wsgi.py',
    'webapp/__init__.py',
    'webapp/admin.py',
    'webapp/apps.py',
    'webapp/forms.py',
    'webapp/models.py',
    'webapp/urls.py',
    'webapp/views.py'
]

def upload_files():
    try:
        # Conectar al servidor FTP
        print(f"Conectando a {FTP_SERVER}...")
        ftp = ftplib.FTP(FTP_SERVER)
        ftp.login(FTP_USERNAME, FTP_PASSWORD)
        print("Conexión FTP establecida correctamente")
        
        # Crear directorios
        print("Creando directorios...")
        for directory in DIRECTORIES:
            try:
                ftp.mkd(directory)
                print(f"Directorio {directory} creado")
            except ftplib.error_perm as e:
                if "550" in str(e):
                    print(f"El directorio {directory} ya existe")
                else:
                    raise
        
        # Cambiar al directorio principal
        ftp.cwd('/')
        
        # Subir archivos
        print("Subiendo archivos...")
        for file_path in FILES_TO_UPLOAD:
            if os.path.exists(file_path):
                # Determinar el directorio de destino
                if '/' in file_path:
                    remote_dir = os.path.dirname(file_path)
                    try:
                        ftp.cwd(remote_dir)
                    except:
                        # Crear directorio si no existe
                        Path(remote_dir).mkdir(parents=True, exist_ok=True)
                        ftp.mkd(remote_dir)
                        ftp.cwd(remote_dir)
                    
                    with open(file_path, 'rb') as file:
                        filename = os.path.basename(file_path)
                        ftp.storbinary(f'STOR {filename}', file)
                    print(f"Archivo {file_path} subido correctamente")
                    ftp.cwd('/')  # Volver al directorio raíz
                else:
                    with open(file_path, 'rb') as file:
                        ftp.storbinary(f'STOR {file_path}', file)
                    print(f"Archivo {file_path} subido correctamente")
            else:
                print(f"Advertencia: El archivo {file_path} no existe")
        
        # Cerrar conexión
        ftp.quit()
        print("Todos los archivos han sido subidos correctamente")
        return True
        
    except Exception as e:
        print(f"Error al subir archivos: {e}")
        return False

def create_backup():
    """Crear una copia de seguridad de los archivos antes de subir"""
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    for file_path in FILES_TO_UPLOAD:
        if os.path.exists(file_path):
            # Crear la estructura de directorios en el backup
            dest_dir = os.path.join(backup_dir, os.path.dirname(file_path))
            os.makedirs(dest_dir, exist_ok=True)
            
            # Copiar el archivo
            with open(file_path, 'rb') as src_file:
                with open(os.path.join(backup_dir, file_path), 'wb') as dest_file:
                    dest_file.write(src_file.read())
    
    print(f"Copia de seguridad creada en: {backup_dir}")

if __name__ == "__main__":
    print("=== Script de Subida FTP para Materials Fadrell (Django) ===")
    
    # Crear copia de seguridad
    create_backup()
    
    # Subir archivos
    success = upload_files()
    
    if success:
        print("Proceso completado con éxito!")
    else:
        print("Hubo errores durante el proceso de subida")