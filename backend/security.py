import os
import hashlib
from getpass import getpass

SENHA_FILE = '.senha'

def carregar_senha():
    try:
        with open(SENHA_FILE, 'rb') as f:
            salt, senha_hash = f.read().split(b',')
            return salt, senha_hash
    except FileNotFoundError:
        return None, None

def criar_senha():
    print("\nCrie uma senha para proteger seu diário:")
    while True:
        senha = getpass("Nova senha (mínimo 8 caracteres): ")
        if len(senha) < 8:
            print("Senha muito curta! Tente novamente.")
            continue

        confirmacao = getpass("Confirme a senha: ")
        if senha != confirmacao:
            print("As senhas não coincidem!")
        else:
            salt = os.urandom(32)
            senha_hash = hashlib.pbkdf2_hmac('sha256', senha.encode(), salt, 100000)
            with open(SENHA_FILE, 'wb') as f:
                f.write(salt + b',' + senha_hash)
            print("\n✓ Senha definida com sucesso!\n")
            break

def autenticar():
    salt, senha_hash = carregar_senha()
    if not salt:
        criar_senha()
        return True

    tentativas = 3
    while tentativas > 0:
        senha = getpass("\nDigite sua senha: ")
        novo_hash = hashlib.pbkdf2_hmac('sha256', senha.encode(), salt, 100000)
        if novo_hash == senha_hash:
            return True
        tentativas -= 1
        print(f"Senha incorreta! Tentativas restantes: {tentativas}")

    print("\n⚠ Acesso bloqueado! Saindo...")
    return False