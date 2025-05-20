from jose import jwt
import datetime

class JWTokensGenerator:
    def generate_jwt(user_data):
        payload = {
            'user_id': user_data['id'],
            'username': user_data.get('name', ''),
            'roles': user_data.get('userCredentials', {}).get('userRoles', []),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(payload, 'your-secret-key', algorithm='HS256')
        return token