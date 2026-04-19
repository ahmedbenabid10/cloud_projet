from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import json, base64, jwt, datetime

# Generate RSA key pair
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# Save private key
with open("private_key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()
    ))

# Save public key
with open("public_key.pem", "wb") as f:
    f.write(public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    ))

# Generate a valid JWT token
token = jwt.encode(
    {
        "sub": "test-user-algeria",
        "email": "test@cloud.dz",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)
    },
    private_key,
    algorithm="RS256"
)

print("=" * 60)
print("YOUR BEARER TOKEN (copy this into Swagger):")
print("=" * 60)
print(f"Bearer {token}")
print("=" * 60)
