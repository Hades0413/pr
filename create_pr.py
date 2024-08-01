import requests
import json
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configura tus variables
TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = 'Hades0413'
REPO_NAME = 'pr'
BASE_BRANCH = 'main'
FEATURE_BRANCH = 'feature-branch'
PR_TITLE = 'Título del Pull Request'
PR_BODY = 'Descripción del Pull Request'

# URL de la API de GitHub para crear un pull request
url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls'

# Encabezados para la autenticación y formato
headers = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'Content-Type': 'application/json'
}

# Datos del pull request
data = {
    'title': PR_TITLE,
    'body': PR_BODY,
    'head': FEATURE_BRANCH,
    'base': BASE_BRANCH
}

# Realiza la solicitud POST a la API de GitHub
response = requests.post(url, headers=headers, data=json.dumps(data))

# Imprime el resultado
if response.status_code == 201:
    print('Pull request creado exitosamente.')
    print('URL:', response.json()['html_url'])
else:
    print('Error al crear el pull request.')
    print('Código de estado:', response.status_code)
    print('Respuesta:', response.json())
