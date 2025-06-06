import os
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

SENHA_FILE = '.senha'

def carregar_senha():
    try:
        with open(SENHA_FILE, 'rb') as f:
            dados = f.read()
            salt, senha_hash = dados.split(b',', 1)
            return salt, senha_hash
    except FileNotFoundError:
        return None, None
    except Exception as e:
        print(f"Erro ao ler arquivo de senha: {str(e)}")
        return None, None

def criar_senha(senha: str):
    salt = os.urandom(32)
    senha_hash = hashlib.pbkdf2_hmac('sha256', senha.encode(), salt, 100000)
    with open(SENHA_FILE, 'wb') as f:
        f.write(salt + b',' + senha_hash)
    return hashlib.pbkdf2_hmac('sha256', senha.encode(), salt, 100000, dklen=32)

def autenticar(senha_digitada: str):
    salt, senha_hash = carregar_senha()
    if not salt:
        return None
    
    novo_hash = hashlib.pbkdf2_hmac('sha256', senha_digitada.encode(), salt, 100000)
    if novo_hash == senha_hash:
        return hashlib.pbkdf2_hmac('sha256', senha_digitada.encode(), salt, 100000, dklen=32)
    return None

def criptografar(texto: str, chave: bytes) -> bytes:
    try:
        iv = os.urandom(16)
        cipher = AES.new(chave, AES.MODE_CBC, iv)
        texto_bytes = pad(texto.encode('utf-8'), AES.block_size)
        return iv + cipher.encrypt(texto_bytes)
    except Exception as e:
        print(f"\033[31mErro na criptografia: {str(e)}\033[0m")
        raise

def descriptografar(dados: bytes, chave: bytes) -> str:
    try:
        iv = dados[:16]
        cipher = AES.new(chave, AES.MODE_CBC, iv)
        texto_bytes = unpad(cipher.decrypt(dados[16:]), AES.block_size)
        return texto_bytes.decode('utf-8')
    except Exception as e:
        print(f"\033[31mErro na descriptografia: {str(e)}\033[0m")
        raise