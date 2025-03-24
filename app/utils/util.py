from datetime import datetime, timedelta, timezone
from jose import jwt, ExpiredSignatureError, JWTError
from functools import wraps
from flask import request, jsonify
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or 'Azumarill is the best Water-type Pokemon'

def encode_token(user_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0,hours=1), # expiration date
        'iat': datetime.now(timezone.utc), # issued at
        'sub':  str(user_id) # subject
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]
            if not token:
                return jsonify({'message': 'Missing token'}), 400
            
            try:
                data = jwt.decode(token, SECRET_KEY, algorithms='HS256')
                print(data)
                customer_id = data['sub']
            except ExpiredSignatureError:
                return jsonify({'message': 'Token expired.'}), 400
            except JWTError:
                return jsonify({'message': 'Invalid token'}), 400
            
            return f(customer_id, *args, **kwargs)
        else:
            return jsonify({'message': 'You must be logged in to access this'}), 400
        
    return decorated