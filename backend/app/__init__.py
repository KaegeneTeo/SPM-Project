from flask import Flask
from supabase import Client, create_client

def create_app():
    app = Flask(__name__)
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    return