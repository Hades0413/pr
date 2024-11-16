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
        print("Salida estándar:", result.stdout)
    if result.stderr:
        print("Error estándar:", result.stderr)
    return result.stdout, result.stderr

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

# 1. Eliminar ramas locales que siguen el patrón
def delete_local_branches():
    print("Eliminando ramas locales que siguen el patrón 'feature-branch-2023-05-'...")
    command = "git branch | Where-Object { $_ -match 'feature-branch-2023-05-' } | ForEach-Object { git branch -D $_.Trim() }"
    stdout, stderr = run_command(f"powershell -Command \"{command}\"")
    if stderr:
        print("Error al eliminar ramas locales:", stderr)
    else:
        print("Ramas locales eliminadas exitosamente.")

# 2. Eliminar ramas remotas que siguen el patrón (verificación antes de eliminar)
def delete_remote_branches():
    print("Verificando y eliminando ramas remotas que siguen el patrón 'feature-branch-2023-05-'...")
    command = "git branch -r | Where-Object { $_ -match 'origin/feature-branch-2023-05-' }"
    stdout, stderr = run_command(f"powershell -Command \"{command}\"")
    
    if stdout:
        branches = stdout.splitlines()
        for branch in branches:
            branch_name = branch.replace('origin/', '').strip()
            print(f"Eliminando la rama remota {branch_name}...")
            run_command(f"git push origin --delete {branch_name}")
            time.sleep(2)  # Esperar un poco para evitar sobrecargar el servidor
    else:
        print("No se encontraron ramas remotas para eliminar.")

# 3. Crear y empujar las nuevas ramas de características
def create_and_push_branches():
    print("Creando y empujando nuevas ramas de características...")
    for i in range(1, 3):
        branch_name = f"feature-branch-{YEAR}-{MONTH}-{i}"
        file_name = f"file-{i}.txt"
        
        # Crear la nueva rama desde la rama base (main)
        run_command(f"git checkout {BASE_BRANCH}")
        run_command(f"git pull origin {BASE_BRANCH}")
        run_command(f"git checkout -b {branch_name}")
        
        # Crear un archivo específico para el commit
        with open(file_name, 'w') as f:
            f.write(f"Este es un commit dummy para la rama {branch_name}")
        
        # Agregar y hacer commit
        run_command(f"git add {file_name}")
        
        # Aquí corregimos el formato del commit para asegurar que no haya problemas con espacios
        commit_message = f"Commit dummy para la rama {branch_name}"
        run_command(f"git commit -m \"{commit_message}\"")
        
        # Empujar la rama
        run_command(f"git push origin {branch_name}")
        
        # Regresar a la rama principal
        run_command(f"git checkout {BASE_BRANCH}")

# 4. Crear múltiples pull requests a través de la API de GitHub
def create_pull_requests():
    print("Creando los Pull Requests...")
    merged_prs = []  # Lista para almacenar los PRs fusionados exitosamente
    for i in range(1, 3):  # Cambia 3 a la cantidad deseada de PRs
        feature_branch = f'feature-branch-{YEAR}-{MONTH}-{i}'
        print(f"Intentando crear PR para la rama {feature_branch}...")

        # Configura los datos del pull request
        pr_title = PR_TITLE_TEMPLATE.format(f'{YEAR}-{MONTH}-{i}')
        pr_body = PR_BODY_TEMPLATE.format(f'{YEAR}-{MONTH}-{i}')
        
        data = {
            'title': pr_title,
            'body': pr_body,
            'head': feature_branch,
            'base': BASE_BRANCH
        }
        
        # Realiza la solicitud POST a la API de GitHub
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            
            # Imprime el resultado de la solicitud
            print(f"Respuesta de la API para PR {i}: {response.status_code}")
            if response.status_code == 201:
                print(f'Pull request {i} creado exitosamente.')
                pr_url = response.json()['html_url']
                print(f'URL del PR: {pr_url}')
                
                # Merged automáticamente el PR
                merge_url = response.json()['url'] + '/merge'
                merge_data = {'commit_title': f'Merge Pull Request {i}', 'commit_message': f'Merging PR {i} automatically.'}
                merge_response = requests.put(merge_url, headers=headers, data=json.dumps(merge_data))
                if merge_response.status_code == 200:
                    print(f'Pull request {i} fusionado exitosamente.')
                    merged_prs.append(i)  # Agregar el PR a la lista de fusionados
                else:
                    print(f'Error al fusionar PR {i}: {merge_response.status_code}')
            else:
                print(f'Error al crear el pull request {i}.')
                print('Código de estado:', response.status_code)
                print('Respuesta:', response.json())
        except requests.exceptions.RequestException as e:
            print(f"Error al realizar la solicitud para PR {i}: {e}")
        
        # Espera 2 segundos entre cada solicitud
        time.sleep(2)
    
    return merged_prs

# 5. Eliminar archivos y realizar un commit de eliminación antes de eliminar las ramas remotas
def delete_files_and_commit(merged_prs):
    print("Eliminando archivos y realizando commit para su eliminación...")
    for i in merged_prs:  # Solo para PRs fusionados
        file_name = f"file-{i}.txt"
        
        # Eliminar el archivo localmente
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Archivo {file_name} eliminado.")
        
        # Agregar el cambio (eliminación del archivo)
        run_command(f"git add -A")
        
        # Commit para eliminar los archivos
        commit_message = f"Eliminar archivo {file_name}"
        run_command(f"git commit -m \"{commit_message}\"")
        
        # Empujar el commit
        run_command("git push origin main")

# 6. Eliminar archivos uno por uno en la rama main
def delete_txt_files_from_main():
    print("Eliminando archivos .txt de la rama principal...")
    files = [f for f in os.listdir('.') if f.endswith('.txt')]
    for file in files:
        os.remove(file)
        print(f"Archivo {file} eliminado.")
        run_command(f"git add {file}")
        run_command(f"git commit -m \"Eliminar archivo {file}\"")
    run_command("git push origin main")

# 7. Eliminar ramas locales y remotas que siguen el patrón
def delete_branches():
    delete_local_branches()
    delete_remote_branches()

def main():
    check_user_permissions()
    delete_branches()
    create_and_push_branches()
    merged_prs = create_pull_requests()
    delete_files_and_commit(merged_prs)
    delete_txt_files_from_main()

if __name__ == '__main__':
    main()
