import secrets

# สร้าง JWT_SECRET_KEY
jwt_secret_key = secrets.token_hex(32)
print(jwt_secret_key)