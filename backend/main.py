from security import autenticar
from fileoperations import *
from interface import *
import os

def main():
    cabecalho("Bem-vindo ao Diário Digital")
    
    chave = autenticar()
    if not chave:
        mostrar_erro("Autenticação falhou!")
        return

    if os.path.exists('diario.txt') and not os.path.exists('backup_diario'):
        try:
            with open('diario.txt', 'r', encoding='utf-8') as f:
                conteudo = f.read()
            escrever_arquivo_cifrado(conteudo, chave)
            os.rename('diario.txt', 'backup_diario')
            mostrar_sucesso("Dados migrados com sucesso!")
        except Exception as e:
            mostrar_erro(f"Erro na migração: {str(e)}")

    while True:
        mostrar_menu()
        escolha = input("\033[33m► Escolha uma opção: \033[0m").strip()

        if escolha == '6':
            cabecalho("Até logo!")
            break

        try:
            if escolha == '1':
                nova_anotacao(chave)
            elif escolha == '2':
                historico(chave)
            elif escolha == '3':
                buscar(chave)
            elif escolha == '4':
                editar_excluir(chave)
            elif escolha == '5':
                limpar(chave)
            else:
                mostrar_erro("Opção inválida!")
        except Exception as e:
            mostrar_erro(f"Erro inesperado: {str(e)}")

if __name__ == "__main__":
    main()