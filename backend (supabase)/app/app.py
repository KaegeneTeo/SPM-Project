from flask import Flask
from flask_supabase import Supabase
from dotenv import load_dotenv
import os
from flask import request, jsonify
app = Flask(__name__)
app.config['SUPABASE_URL'] = os.getenv("SUPABASE_URL")
app.config['SUPABASE_KEY'] = os.getenv("SUPABASE_KEY")

supabase = Supabase(app)

@app.route("/employees", methods=['GET'])
def get_employees():
    response = supabase.client.from_('Employee').select("*").execute()
    return response.data

@app.route("/employees", methods=['PUT'])
def update_employee():
    form_data = request.form

@app.route("/login", methods=['POST'])
def login():
    form_data = request.form
    try: 
        response = supabase.client.auth.sign_in_with_password({
            "email": form_data['email'],
            "password": form_data['password']
        })
        json = {
            "email": response.user.email,
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }   

        return json, 200
    except Exception as e:
        json = {
            "message": e.message,
        }
        return json, e.status

@app.route("/check_auth", methods=['POST'])
def check_auth():
    response = supabase.client.auth.get_user(request.form['access_token'])
    status_code = None
    if response != None:
        json = {
            "email": response.user.email,
            "role": response.user.role,
            "access_token": request.form['access_token'],
            "refresh_token": request.form['refresh_token'],
        }
        status_code = 200
    else:
        json = {}
        status_code = 404
    return json, status_code

