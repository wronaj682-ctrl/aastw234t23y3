import os
from flask import Flask, request, jsonify
from supabase import create_client

app = Flask(__name__)

# These come from your Render Environment Variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
ADMIN_SECRET = os.environ.get("ADMIN_SECRET")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def index():
    action = request.args.get('action')
    secret = request.args.get('secret')

    if action == 'verify':
        key_input = request.args.get('key')
        hwid_input = request.args.get('hwid')
        res = supabase.table("keys").select("*").eq("key_content", key_input).execute()
        if not res.data: return jsonify({"valid": False, "message": "Invalid Key"})
        data = res.data[0]
        if data.get('status') == 'banned': return jsonify({"valid": False, "message": "Banned"})
        if not data.get('hwid'):
            supabase.table("keys").update({"hwid": hwid_input}).eq("key_content", key_input).execute()
            return jsonify({"valid": True})
        return jsonify({"valid": data['hwid'] == hwid_input})

    if action == 'generate' and secret == ADMIN_SECRET:
        import secrets
        new_key = "KEY_" + secrets.token_hex(6).upper()
        supabase.table("keys").insert({"key_content": new_key, "status": "active"}).execute()
        return jsonify({"status": "success", "key": new_key})

    if action == 'reset' and secret == ADMIN_SECRET:
        key_to_reset = request.args.get('key')
        supabase.table("keys").update({"hwid": None}).eq("key_content", key_to_reset).execute()
        return jsonify({"status": "success"})

    return jsonify({"message": "API is online"})

if __name__ == "__main__":
    app.run()
