import os
import subprocess
import requests
import time
import json
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Configura tus variables
TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = 'Hades0413'
REPO_NAME = 'pr'
BASE_BRANCH = 'main'
PR_TITLE_TEMPLATE = 'Título del Pull Request {}'
PR_BODY_TEMPLATE = 'Descripción del Pull Request {}'

# Define el año y mes
YEAR = '2023'
MONTH = '05'

# URL de la API de GitHub para crear un PR
url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls'

# Encabezados para la autenticación
headers = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'Content-Type': 'application/json'
}

# Función para verificar si la rama existe en el repositorio remoto
def branch_exists(branch_name):
    branches_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/branches/{branch_name}'
    try:
        response = requests.get(branches_url, headers=headers)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Error al verificar la rama {branch_name}: {e}")
        return False

# Función para verificar si la rama existe localmente
def branch_exists_locally(branch_name):
    try:
        subprocess.run(["git", "rev-parse", "--verify", branch_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True  # La rama existe localmente
    except subprocess.CalledProcessError:
        return False  # La rama no existe

# Función para crear una rama localmente y hacer un commit
def create_local_branch(branch_name):
    # Cambiar a la rama base (main) antes de crear una nueva rama
    subprocess.run(["git", "checkout", BASE_BRANCH], check=True)
    
    # Actualiza la rama base
    subprocess.run(["git", "pull", "origin", BASE_BRANCH], check=True)

    # Crear la nueva rama y hacer un commit inicial (ejemplo: crear un archivo vacío o de prueba)
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    
    # Crear o modificar un archivo (por ejemplo, creando un archivo vacío)
    with open(f"{branch_name}.txt", "w") as file:
        file.write(f"Este es el archivo de la rama {branch_name}")
    
    subprocess.run(["git", "add", f"{branch_name}.txt"], check=True)
    subprocess.run(["git", "commit", "-m", f"Agregado archivo para {branch_name}"], check=True)

# Función para hacer push de la rama al repositorio remoto
def push_branch_to_remote(branch_name):
    subprocess.run(["git", "push", "--set-upstream", "origin", branch_name], check=True)

# Función para crear un Pull Request
def create_pull_request(i):
    FEATURE_BRANCH = f'feature-branch-{YEAR}-{MONTH}-{i}'

    if not branch_exists_locally(FEATURE_BRANCH):
        print(f'La rama {FEATURE_BRANCH} no existe localmente, creándola...')
        create_local_branch(FEATURE_BRANCH)
        push_branch_to_remote(FEATURE_BRANCH)
        time.sleep(2)  # Espera a que el push se complete antes de continuar
    else:
        print(f'La rama {FEATURE_BRANCH} ya existe localmente. Haciendo checkout...')
        subprocess.run(["git", "checkout", FEATURE_BRANCH], check=True)
        # Asegurando que la rama esté empujada al remoto
        push_branch_to_remote(FEATURE_BRANCH)
        time.sleep(2)

    # Crear el pull request
    PR_TITLE = PR_TITLE_TEMPLATE.format(f'{YEAR}-{MONTH}-{i}')
    PR_BODY = PR_BODY_TEMPLATE.format(f'{YEAR}-{MONTH}-{i}')
    
    data = {
        'title': PR_TITLE,
        'body': PR_BODY,
        'head': FEATURE_BRANCH,  # La rama creada localmente y subida
        'base': BASE_BRANCH
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 201:
            pr_url = response.json().get('html_url', 'URL no disponible')
            print(f'Pull request {i} creado exitosamente.')
            print('URL:', pr_url)
            # Intentar hacer merge automáticamente si el PR está listo
            merge_pr(response.json().get('number'))
        else:
            print(f'Error al crear el pull request {i}.')
            print('Código de estado:', response.status_code)
            print('Respuesta:', response.json())
    except requests.RequestException as e:
        print(f"Error al crear el PR {i}: {e}")

# Función para hacer merge automático del PR
def merge_pr(pr_number):
    merge_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/merge'
    data = {
        'commit_title': 'Merge del Pull Request',
        'commit_message': 'Automáticamente fusionado después de la creación.',
        'merge_method': 'merge'  # Puedes usar 'merge', 'squash', o 'rebase'
    }

    try:
        response = requests.put(merge_url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            print(f'PR {pr_number} fusionado exitosamente.')
        else:
            print(f'Error al fusionar el PR {pr_number}.')
            print('Código de estado:', response.status_code)
            print('Respuesta:', response.json())
    except requests.RequestException as e:
        print(f"Error al fusionar el PR {pr_number}: {e}")

# Función para eliminar worktrees activos
def remove_worktrees():
    result = subprocess.run(["git", "worktree", "list"], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if line:
            # Extraer el path del worktree
            worktree_path = line.split()[0]
            # Asegurarse de que no sea el directorio principal
            if worktree_path != os.getcwd():
                print(f"Eliminando worktree en {worktree_path}...")
                subprocess.run(["git", "worktree", "remove", worktree_path], check=True)

# Función para eliminar las ramas locales creadas por el script
def delete_local_branches(start=1, end=50):
    # Primero, cambiar a la rama main para tener los permisos necesarios
    subprocess.run(["git", "checkout", BASE_BRANCH], check=True)
    remove_worktrees()  # Eliminar cualquier worktree antes de intentar eliminar las ramas
    for i in range(start, end + 1):
        branch_name = f'feature-branch-{YEAR}-{MONTH}-{i}'
        print(f'Eliminando la rama local {branch_name}...')
        subprocess.run(["git", "branch", "-D", branch_name], check=True)

# Función para eliminar las ramas remotas creadas por el script
def delete_remote_branches(start=1, end=50):
    # Primero, cambiar a la rama main para tener los permisos necesarios
    subprocess.run(["git", "checkout", BASE_BRANCH], check=True)
    for i in range(start, end + 1):
        branch_name = f'feature-branch-{YEAR}-{MONTH}-{i}'
        print(f'Eliminando la rama remota {branch_name}...')
        subprocess.run(["git", "push", "origin", "--delete", branch_name], check=True)

# Función para eliminar todos los archivos .txt del repositorio
def delete_txt_files():
    # Buscar todos los archivos .txt en el repositorio
    txt_files = subprocess.run(["find", ".", "-name", "*.txt"], capture_output=True, text=True).stdout.splitlines()
    if txt_files:
        # Eliminar los archivos .txt encontrados
        for file in txt_files:
            print(f"Eliminando el archivo {file}...")
            subprocess.run(["git", "rm", file], check=True)
        
        # Hacer commit de la eliminación
        subprocess.run(["git", "commit", "-m", "Cargando..."], check=True)

        # Hacer push al repositorio remoto
        subprocess.run(["git", "push"], check=True)

# Crear múltiples pull requests
def create_multiple_prs(num_prs=50):
    for i in range(1, num_prs + 1):  # Cambia 51 a la cantidad deseada de PRs
        create_pull_request(i)
        # Espera de forma controlada entre cada solicitud
        time.sleep(2)

    # Eliminar todas las ramas locales creadas al finalizar el proceso
    delete_local_branches(1, num_prs)
    # Eliminar las ramas remotas después de completar los PRs
    delete_remote_branches(1, num_prs)

    # Eliminar los archivos .txt y hacer commit con el mensaje "Cargando..."
    delete_txt_files()

# Ejecutar la creación de PRs
if __name__ == "__main__":
    create_multiple_prs(3)
