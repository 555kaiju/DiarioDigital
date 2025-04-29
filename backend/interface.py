def mostrar_menu():
    print("\n\033[1;35m" + "═" * 30)
    print(" DIÁRIO DIGITAL ".center(30, '★'))
    print("═" * 30 + "\033[0m")
    print("\033[36m1. Nova Anotação")
    print("2. Histórico")
    print("3. Buscar")
    print("4. Editar/Excluir")
    print("5. Limpar Tudo")
    print("6. Sair\033[0m\n")

def cabecalho(titulo):
    print("\n\033[1;35m" + "═" * 60)
    print(f" {titulo} ".center(60, '★'))
    print("═" * 60 + "\033[0m")

def mostrar_erro(mensagem):
    print(f"\n\033[1;31m⚠ {mensagem.center(58)} ⚠\033[0m\n")

def mostrar_sucesso(mensagem):
    print(f"\n\033[1;32m✓ {mensagem.center(58)} ✓\033[0m\n")