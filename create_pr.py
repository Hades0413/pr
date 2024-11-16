import os
import time
import json
import requests
from dotenv import load_dotenv
import subprocess

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configura tus variables
TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = 'Hades0415'
REPO_NAME = 'pr'
BASE_BRANCH = 'main'
PR_TITLE_TEMPLATE = 'Merge pull request #{} from Hades0415/{}'
PR_BODY_TEMPLATE = 'Descripción del Pull Request {}'

# Define el año y el mes manualmente
YEAR = '2023'
MONTH = '05'

# URL de la API de GitHub para crear un pull request
url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls'

# Encabezados para la autenticación y formato
headers = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'Content-Type': 'application/json'
}

# Función para ejecutar comandos en la terminal
def run_command(command):
    print(f"Ejecutando comando: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        print("Salida estándar:", result.stdout)
    if result.stderr:
        print("Error estándar:", result.stderr)
    return result.stdout.strip(), result.stderr.strip()

# Crear y empujar nuevas ramas de características
def create_and_push_branches():
    print("Creando y empujando nuevas ramas de características...")
    for i in range(1, 5):
        branch_name = f"feature-branch-{YEAR}-{MONTH}-{i}"
        file_name = f"file-{i}.txt"

        # Crear la nueva rama desde la rama base
        run_command(f"git checkout {BASE_BRANCH}")
        run_command(f"git pull origin {BASE_BRANCH}")
        run_command(f"git checkout -b {branch_name}")

        # Crear un archivo específico para el commit
        with open(file_name, 'w') as f:
            f.write(f"Este es un commit dummy para la rama {branch_name}")

        # Agregar y hacer commit
        run_command(f"git add {file_name}")
        run_command(f"git commit -m 'Commit dummy para la rama {branch_name}'")
        
        # Empujar la rama
        run_command(f"git push origin {branch_name}")

        # Regresar a la rama principal
        run_command(f"git checkout {BASE_BRANCH}")

# Crear y fusionar pull requests
def create_and_merge_pull_requests():
    print("Creando y fusionando Pull Requests...")
    for i in range(1, 5):
        feature_branch = f'feature-branch-{YEAR}-{MONTH}-{i}'
        pr_title = PR_TITLE_TEMPLATE.format(i, feature_branch)
        pr_body = PR_BODY_TEMPLATE.format(f'{YEAR}-{MONTH}-{i}')
        
        # Configurar los datos del pull request
        data = {
            'title': pr_title,
            'body': pr_body,
            'head': feature_branch,
            'base': BASE_BRANCH
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 201:
                print(f"Pull request {i} creado exitosamente.")
                pr_url = response.json()['html_url']
                print(f"URL del PR: {pr_url}")

                # Fusionar automáticamente el PR
                merge_url = response.json()['url'] + '/merge'
                merge_data = {
                    'commit_title': f'Merge pull request #{i} from {feature_branch}',
                    'commit_message': f'Merge pull request #{i}'
                }
                merge_response = requests.put(merge_url, headers=headers, data=json.dumps(merge_data))
                if merge_response.status_code == 200:
                    print(f"Pull request {i} fusionado exitosamente.")
                else:
                    print(f"Error al fusionar PR {i}: {merge_response.status_code}")
            else:
                print(f"Error al crear el pull request {i}: {response.status_code}")
                print("Respuesta:", response.json())
        except requests.exceptions.RequestException as e:
            print(f"Error al realizar la solicitud para PR {i}: {e}")
        
        time.sleep(2)

# Eliminar archivos, hacer commit y fusionar
def delete_files_and_commit():
    print("Eliminando archivos y realizando commit...")
    for i in range(1, 5):
        file_name = f"file-{i}.txt"
        
        # Eliminar el archivo localmente
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Archivo {file_name} eliminado.")
        
        # Agregar el cambio
        run_command("git add -A")
        
        # Hacer commit
        commit_message = f"Eliminar archivo {file_name}"
        run_command(f"git commit -m '{commit_message}'")
        
        # Empujar los cambios
        run_command(f"git push origin {BASE_BRANCH}")

# Eliminar ramas remotas después de procesarlas
def delete_remote_branches():
    print("Eliminando ramas remotas...")
    for i in range(1, 5):
        branch_name = f"feature-branch-{YEAR}-{MONTH}-{i}"
        run_command(f"git push origin --delete {branch_name}")
        print(f"Rama remota {branch_name} eliminada.")

# Ejecutar todo el flujo
print("Iniciando el proceso completo...")
create_and_push_branches()
create_and_merge_pull_requests()
delete_files_and_commit()
delete_remote_branches()
