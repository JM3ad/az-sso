import os
import requests
from flask import Flask, redirect, request
from flask_login import LoginManager, login_required, login_user
from src.user import User

app = Flask(__name__)
app.secret_key = 'secret'
login_manager = LoginManager()


@login_manager.user_loader
def load_user(id):
    return User(id)

@login_manager.unauthorized_handler
def unauthorized():
    url = f'https://login.microsoftonline.com/{os.getenv("AZ_TENANT_ID")}/oauth2/v2.0/authorize?'\
        + f'client_id={os.getenv("AZ_CLIENT_ID")}' \
        + '&scope=api://4af1a0b3-0554-4192-b159-0b2500864d47/user_impersonation' \
        + '&response_type=code'
    return redirect(url)

login_manager.init_app(app)

@app.route('/redirect')
def authed():
    code = request.args.get('code')
    
    token = get_token_from_code(code)

    user_id = get_user_id(token)
    login_user(User(user_id))
    return f"You're in {user_id}"

@app.route('/')
@login_required
def index():
    return 'Hello'

def get_token_from_code(code):
    url = f'https://login.microsoftonline.com/{os.getenv("AZ_TENANT_ID")}/oauth2/v2.0/token'
    data = {
        'client_id': os.getenv('AZ_CLIENT_ID'),
        'client_secret': os.getenv('AZ_CLIENT_SECRET'),
        'scope': 'https://graph.microsoft.com/User.Read',
        'grant_type': 'authorization_code',
        'code': code
    }
    result = requests.post(url, data = data)
    result.raise_for_status()
    token = result.json()['access_token']
    return token

def get_user_id(token):
    user_url = 'https://graph.microsoft.com/v1.0/me/'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    result = requests.get(user_url, headers = headers)
    
    json_result = result.json()
    print(json_result)
    id = json_result['id']
    return id