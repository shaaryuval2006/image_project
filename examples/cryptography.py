from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import os
import base64


class SymmetricEncryption:
    def __init__(self, password: str, salt: bytes = None):
        self.password = password.encode()
        self.salt = salt if salt else os.urandom(16)
        self.key = self.derive_key()

    def derive_key(self):
        # שימוש ב-PBKDF2HMAC או Scrypt כדי לגזור מפתח מהסיסמה
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(self.password)

    def encrypt(self, plaintext: str) -> str:
        iv = os.urandom(16)  # Initialisation Vector
        cipher = Cipher(algorithms.AES(self.key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(plaintext.encode()) + padder.finalize()

        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        return base64.b64encode(self.salt + iv + ciphertext).decode()

    def decrypt(self, ciphertext: str) -> str:
        data = base64.b64decode(ciphertext)
        salt = data[:16]
        iv = data[16:32]
        actual_ciphertext = data[32:]

        self.salt = salt
        self.key = self.derive_key()

        cipher = Cipher(algorithms.AES(self.key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        return plaintext.decode()


# דוגמה לשימוש בספרייה
if __name__ == "__main__":
    password = "my_secure_password"
    plaintext = "This is a secret message."

    encryptor = SymmetricEncryption(password)
    encrypted = encryptor.encrypt(plaintext)
    print(f"Encrypted: {encrypted}")

    decryptor = SymmetricEncryption(password)
    decrypted = decryptor.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
