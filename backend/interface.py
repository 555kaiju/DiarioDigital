def mostrar_menu():
    print('\n' + '=' * 30)
    print('1 - NOVA NOTA')
    print('2 - HISTORICO')
    print('3 - BUSCAR NOTA')
    print('4 - EDITAR OU EXCLUIR ENTRADA')
    print('5 - LIMPAR HISTÓRICO')
    print('6 - SAIR')

def obter_entrada(mensagem):
    return input(mensagem).strip()

def mostrar_mensagem(mensagem):
    print(f"\n{mensagem.center(80)}")

def formatar_datahora(data_hora):
    return data_hora.strftime("%d/%m/%Y %H:%M:%S")

def cabecalho(titulo):
    print("\n" + "=" * 80)
    print(titulo.center(80))
    print("=" * 80 + "\n")