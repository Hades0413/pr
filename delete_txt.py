import os
import subprocess
import requests
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Configura tus variables
TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = os.getenv('REPO_OWNER')
REPO_NAME = os.getenv('REPO_NAME')
BASE_BRANCH = os.getenv('BASE_BRANCH', 'main')  # 'main' es el valor predeterminado

# URL para obtener los archivos en el repositorio
BASE_URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/'

# Encabezados para la autenticación
headers = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'Content-Type': 'application/json'
}

# Función para obtener todos los archivos .txt del repositorio
def get_txt_files():
    files = []
    try:
        response = requests.get(BASE_URL, headers=headers)
        if response.status_code == 200:
            contents = response.json()
            for file in contents:
                if file['name'].endswith('.txt'):
                    files.append(file['path'])
        else:
            print(f"Error al obtener archivos: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error al conectarse con GitHub: {e}")
    return files

# Función para eliminar los archivos .txt del repositorio
def delete_txt_files():
    txt_files = get_txt_files()
    
    if not txt_files:
        print("No se encontraron archivos .txt.")
        return
    
    for file in txt_files:
        print(f"Eliminando archivo: {file}")
        # Eliminar archivo en el repositorio remoto
        url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file}'
        data = {
            'message': f'Eliminando archivo {file}',
            'sha': get_file_sha(file)  # Necesitamos el SHA del archivo para eliminarlo
        }
        try:
            response = requests.delete(url, headers=headers, data=data)
            if response.status_code == 200:
                print(f'Archivo {file} eliminado correctamente.')
            else:
                print(f"Error al eliminar el archivo {file}: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error al eliminar el archivo {file}: {e}")

# Función para obtener el SHA de un archivo
def get_file_sha(file_path):
    try:
        response = requests.get(f'{BASE_URL}{file_path}', headers=headers)
        if response.status_code == 200:
            file_data = response.json()
            return file_data['sha']
        else:
            print(f"Error al obtener SHA de {file_path}: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error al obtener SHA de {file_path}: {e}")
    return None

# Función para hacer commit y push de los cambios
def commit_and_push():
    subprocess.run(["git", "checkout", BASE_BRANCH], check=True)
    subprocess.run(["git", "pull", "origin", BASE_BRANCH], check=True)

    # Añadir todos los archivos modificados y no rastreados al área de preparación
    subprocess.run(["git", "add", "."], check=True)  # Asegura que todos los archivos sean añadidos

    # Hacer commit de los cambios (eliminación de los archivos .txt)
    subprocess.run(["git", "commit", "-m", "Eliminados archivos .txt"], check=True)

    # Push de los cambios al repositorio
    subprocess.run(["git", "push", "origin", BASE_BRANCH], check=True)

# Función principal para eliminar archivos .txt y hacer commit
def main():
    delete_txt_files()
    commit_and_push()

if __name__ == "__main__":
    main()
