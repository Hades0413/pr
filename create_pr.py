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
REPO_OWNER = 'Hades0413'
REPO_NAME = 'pr'
BASE_BRANCH = 'main'
PR_TITLE_TEMPLATE = 'Título del Pull Request {}'
PR_BODY_TEMPLATE = 'Descripción del Pull Request {}'

# Define el año y el mes manualmente
YEAR = '2023'
MONTH = '05'  # Usa '01' para el mes

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
        print("Salida estándar:", result.stdout.strip())
    if result.stderr:
        print("Error estándar:", result.stderr.strip())
    return result.stdout.strip(), result.stderr.strip()

# Función para verificar si el usuario tiene acceso y es colaborador en el repositorio
def check_user_permissions():
    print("Verificando los permisos del usuario...")
    try:
        response = requests.get(f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/collaborators', headers=headers)
        if response.status_code == 200:
            collaborators = [collab['login'] for collab in response.json()]
            if REPO_OWNER in collaborators:
                print(f"El usuario '{REPO_OWNER}' es colaborador.")
            else:
                print(f"El usuario '{REPO_OWNER}' no es colaborador.")
        else:
            print(f"Error al verificar colaboradores: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud para verificar permisos: {e}")

# Eliminar ramas locales que siguen el patrón
def delete_local_branches():
    print("Eliminando ramas locales...")
    command = "git branch --list 'feature-branch-2023-05-*'"
    stdout, _ = run_command(command)
    branches = stdout.splitlines()
    for branch in branches:
        branch_name = branch.strip()
        run_command(f"git branch -D {branch_name}")

# Eliminar ramas remotas que siguen el patrón
def delete_remote_branches():
    print("Eliminando ramas remotas...")
    command = "git branch -r --list 'origin/feature-branch-2023-05-*'"
    stdout, _ = run_command(command)
    branches = stdout.splitlines()
    for branch in branches:
        branch_name = branch.replace('origin/', '').strip()
        run_command(f"git push origin --delete {branch_name}")

# Crear y empujar nuevas ramas de características
def create_and_push_branches():
    print("Creando y empujando nuevas ramas...")
    for i in range(1, 3):
        branch_name = f"feature-branch-{YEAR}-{MONTH}-{i}"
        file_name = f"file-{i}.txt"
        run_command(f"git checkout {BASE_BRANCH}")
        run_command(f"git pull origin {BASE_BRANCH}")
        run_command(f"git checkout -b {branch_name}")
        with open(file_name, 'w') as f:
            f.write(f"Commit dummy para la rama {branch_name}")
        run_command(f"git add {file_name}")
        run_command(f"git commit -m 'Commit dummy para {branch_name}'")
        run_command(f"git push origin {branch_name}")
        run_command(f"git checkout {BASE_BRANCH}")

# Crear múltiples pull requests
def create_pull_requests():
    print("Creando Pull Requests...")
    for i in range(1, 3):
        feature_branch = f"feature-branch-{YEAR}-{MONTH}-{i}"
        data = {
            'title': PR_TITLE_TEMPLATE.format(f'{YEAR}-{MONTH}-{i}'),
            'body': PR_BODY_TEMPLATE.format(f'{YEAR}-{MONTH}-{i}'),
            'head': feature_branch,
            'base': BASE_BRANCH
        }
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 201:
                print(f"PR creado: {response.json()['html_url']}")
            else:
                print(f"Error creando PR para {feature_branch}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        time.sleep(2)

# Eliminar archivos creados para commits dummy
def delete_files_and_commit():
    print("Eliminando archivos creados...")
    for i in range(1, 3):
        file_name = f"file-{i}.txt"
        if os.path.exists(file_name):
            os.remove(file_name)
            run_command(f"git add -A")
            run_command(f"git commit -m 'Eliminar archivo {file_name}'")
            run_command("git push origin main")

# Eliminar ramas remotas después de PRs
def delete_remote_branches_after_pr():
    print("Eliminando ramas remotas después de PRs...")
    for i in range(1, 3):
        branch_name = f"feature-branch-{YEAR}-{MONTH}-{i}"
        run_command(f"git push origin --delete {branch_name}")

# Ejecutar las funciones
if __name__ == "__main__":
    print("Iniciando el proceso...")
    check_user_permissions()
    delete_local_branches()
    delete_remote_branches()
    create_and_push_branches()
    create_pull_requests()
    delete_files_and_commit()
    delete_remote_branches_after_pr()
