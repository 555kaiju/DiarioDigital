from security import autenticar
from fileoperations import (
    verificacao, nova_anotacao, historico,
    limpar, buscar, editar_excluir
)
from interface import mostrar_menu, obter_entrada, mostrar_mensagem

def main():
    if not autenticar():
        return

    while True:
        mostrar_menu()
        escolha = obter_entrada('Selecione a opção desejada: ')

        if escolha == '6':
            mostrar_mensagem("✓ Sessão encerrada. Até logo!")
            break
        elif escolha == '1':
            verificacao()
            nova_anotacao()
        elif escolha == '2':
            historico()
        elif escolha == '3':
            buscar()
        elif escolha == '4':
            historico()
            editar_excluir()
        elif escolha == '5':
            limpar()
        else:
            mostrar_mensagem("Opção inválida!")

if __name__ == "__main__":
    main()