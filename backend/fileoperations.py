import os
from datetime import datetime

diario = 'diario.txt'

def verificacao():
    if not os.path.exists(diario):
        with open(diario, 'w') as arquivo:
            pass
        print(f"Arquivo '{diario}' criado com sucesso!")
    else:
        print("Iniciando diário...")

def nova_anotacao():
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    print("\n" + "=" * 80)
    print(f"Nova Anotação - {data_hora}")
    print("=" * 80 + "\n")

    print("Digite sua anotação (pressione Enter em uma linha vazia para finalizar):")
    texto = []
    while True:
        linha = input()
        if linha.strip() == '':
            break
        texto.append(linha)

    with open(diario, "a", encoding="utf-8") as arquivo:
        arquivo.write(f"[{data_hora}]\n")
        arquivo.write("\n".join(texto))
        arquivo.write("\n\n" + "-" * 30 + "\n\n")

    print("\n✓ Anotação salva com sucesso!\n")

def historico():
    try:
        with open(diario, "r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read()

            entradas = conteudo.split("\n\n------------------------------\n\n")
            entradas_validas = [e.strip() for e in entradas if e.strip() != '']

            if not entradas_validas:
                print("\nNenhuma anotação encontrada.\n")
                return

            print("\n" + "=" * 80)
            print("HISTÓRICO DE ANOTAÇÕES".center(80))
            print("=" * 80 + "\n")
            total_entradas = len(entradas_validas)
            for indice, entrada in enumerate(entradas_validas, 1):
                num_entry = total_entradas - indice + 1
                partes = entrada.split("\n", 1)
                if len(partes) >= 2:
                    data_hora = partes[0][1:-1]
                    texto = partes[1].strip()

                    print(f"[ENTRADA {num_entry}]".center(80, '-'))
                    print(f"Data/Hora: {data_hora}")
                    print("-" * 80)
                    print(texto)
                    print("\n" + "═" * 80 + "\n")

    except FileNotFoundError:
        print("\nNenhum diário encontrado. Crie sua primeira anotação!\n")

def limpar():
    print("\n" + "!" * 80)
    print("ATENÇÃO: Esta ação apagará permanentemente todo o conteúdo do diário!".center(80))
    print("!" * 80)

    confirmacao1 = input("\nPara confirmar, digite 'APAGAR TUDO': ").strip().upper()
    if confirmacao1 != "APAGAR TUDO":
        print("\nOperação cancelada (1ª confirmação falhou).\n")
        return

    confirmacao2 = input("Digite novamente 'APAGAR TUDO' para confirmar: ").strip().upper()
    if confirmacao2 != "APAGAR TUDO":
        print("\nOperação cancelada (2ª confirmação falhou).\n")
        return

    try:
        with open(diario, "w", encoding="utf-8") as arquivo:
            arquivo.write("")
        print("\n" + "✓" * 80)
        print("Diário totalmente limpo com sucesso!".center(80))
        print("✓" * 80 + "\n")

    except Exception as e:
        print(f"\nErro ao limpar o diário: {str(e)}\n")

def buscar():
    try:
        with open(diario, "r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read()
            entradas = [e.strip() for e in conteudo.split("\n\n------------------------------\n\n") if e.strip()]

            termo = input("\nDigite termo ou data (DD/MM/AAAA): ").lower()
            encontradas = []

            for entrada in entradas:
                partes = entrada.split("\n", 1)
                if len(partes) >= 2 and (termo in partes[0].lower() or termo in partes[1].lower()):
                    encontradas.append(entrada)

            print(f"\n║ {len(encontradas)} RESULTADOS ║".center(80, '═'))
            for idx, entrada in enumerate(reversed(encontradas), 1):
                partes = entrada.split("\n", 1)
                print(f"[RESULTADO {idx}]".center(80, '-'))
                print(f"Data: {partes[0][1:-1]}\nConteúdo:\n{partes[1]}")
                print("═" * 80 + "\n")

    except FileNotFoundError:
        print("\nDiário vazio. Crie uma anotação primeiro!\n")

def editar_excluir():
    try:
        with open(diario, "r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read()
            entradas = [e.strip() for e in conteudo.split("\n\n------------------------------\n\n") if e.strip()]

            if not entradas:
                print("\nNenhuma entrada para editar!\n")
                return

            print("\n" + "=" * 80)
            print("EDIÇÃO DE ENTRADA".center(80))
            print("=" * 80)
            num_entrada = input("\nDigite o número da entrada (como mostrado no histórico): ").strip()

            if not num_entrada.isdigit() or int(num_entrada) < 1 or int(num_entrada) > len(entradas):
                print("\n⚠ Número inválido! Use o número mostrado no histórico.\n")
                return

            idx = len(entradas) - int(num_entrada)
            entrada = entradas[idx]
            partes = entrada.split("\n", 1)

            # Prévia detalhada
            print("\n" + "═" * 80)
            print(f" PRÉVIA DA ENTRADA {num_entrada} ".center(80, '▣'))
            print("═" * 80)
            print(f"Data original: {partes[0][1:-1]}")
            print("Conteúdo atual:".center(80))
            print("-" * 80)
            print(partes[1])
            print("═" * 80 + "\n")

            acao = input("[E]ditar | [X]cluir | [C]ancelar: ").upper()

            if acao == "E":
                print("\n" + "=" * 80)
                print("MODO EDIÇÃO (digite novo texto, finalize com linha vazia)".center(80))
                print("=" * 80)
                novo_texto = []
                while True:
                    linha = input()
                    if linha.strip() == '':
                        break
                    novo_texto.append(linha)

                if not novo_texto:
                    print("\n⚠ Edição cancelada - texto vazio!\n")
                    return

                entradas[idx] = f"{partes[0]}\n" + "\n".join(novo_texto)

                with open(diario, "w", encoding="utf-8") as arquivo:
                    arquivo.write("\n\n------------------------------\n\n".join(entradas))

                print("\n" + "✓" * 80)
                print("ENTRADA ATUALIZADA COM SUCESSO!".center(80))
                print("✓" * 80 + "\n")

            elif acao == "X":
                print("\n" + "!" * 80)
                confirmacao = input("CONFIRMAR EXCLUSÃO? (S/N): ").upper()
                if confirmacao == "S":
                    del entradas[idx]
                    with open(diario, "w", encoding="utf-8") as arquivo:
                        arquivo.write("\n\n------------------------------\n\n".join(entradas))
                    print("\n" + "✓" * 80)
                    print("ENTRADA EXCLUÍDA PERMANENTEMENTE!".center(80))
                    print("✓" * 80 + "\n")
                else:
                    print("\nExclusão cancelada.\n")

            else:
                print("\nOperação cancelada.\n")

    except FileNotFoundError:
        print("\nDiário não encontrado! Crie uma anotação primeiro.\n")
    except Exception as e:
        print(f"\nErro inesperado: {str(e)}\n")