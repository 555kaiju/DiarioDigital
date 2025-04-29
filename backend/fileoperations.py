import os
from datetime import datetime
import pytz
from security import criptografar, descriptografar

DIARIO = 'diario.txt'
SEPARADOR = "\n\n══════════════════════════\n\n"
FORMATO_DATA = "%d/%m/%Y %H:%M:%S"
FUSO = pytz.timezone('America/Manaus')

def ler_arquivo_cifrado(chave: bytes) -> str:
    try:
        if not os.path.exists(DIARIO):
            return ''
            
        with open(DIARIO, 'rb') as f:
            dados = f.read()
            return descriptografar(dados, chave) if dados else ''
    except Exception as e:
        print(f"\033[31mErro na leitura: {str(e)}\033[0m")
        return ''

def escrever_arquivo_cifrado(conteudo: str, chave: bytes):
    try:
        dados = criptografar(conteudo, chave)
        with open(DIARIO, 'wb') as f:
            f.write(dados)
    except Exception as e:
        print(f"\033[31mErro na escrita: {str(e)}\033[0m")
        raise

def nova_anotacao(chave: bytes):
    try:
        data_hora = datetime.now(FUSO).strftime(FORMATO_DATA)
        print("\n\033[1;36m" + "═" * 60)
        print(f" Nova Anotação - {data_hora} ".center(60, ' '))
        print("═" * 60 + "\033[0m\n")
        
        texto = []
        print("\033[33mDigite sua anotação (linha vazia para finalizar):\033[0m")
        while True:
            linha = input()
            if not linha.strip():
                break
            texto.append(linha)

        if not texto:
            print("\033[33mNenhum conteúdo fornecido. Operação cancelada.\033[0m")
            return

        conteudo_existente = ler_arquivo_cifrado(chave)
        novo_conteudo = f"[{data_hora}]\n" + "\n".join(texto) + SEPARADOR
        escrever_arquivo_cifrado(conteudo_existente + novo_conteudo, chave)
        print("\n\033[32m✓ Anotação salva com sucesso!\033[0m\n")

    except KeyboardInterrupt:
        print("\n\033[33mOperação cancelada pelo usuário.\033[0m")

def historico(chave: bytes):
    try:
        conteudo = ler_arquivo_cifrado(chave)
        if not conteudo:
            print("\n\033[33mNenhuma anotação encontrada.\033[0m")
            return

        entradas = [e.strip() for e in conteudo.split(SEPARADOR) if e.strip()]
        print("\n\033[1;36m" + "═" * 60)
        print(" Histórico de Anotações ".center(60, ' '))
        print("═" * 60 + "\033[0m")

        for idx, entrada in enumerate(reversed(entradas), 1):
            partes = entrada.split("\n", 1)
            if len(partes) < 2:
                continue

            data_hora, texto = partes[0][1:-1], partes[1].strip()
            print(f"\n\033[1;34mEntrada #{idx}\033[0m")
            print(f"\033[35mData/Hora: {data_hora}\033[0m")
            print("\033[37m" + texto + "\033[0m")
            print("-" * 60)

    except Exception as e:
        print(f"\033[31mErro ao carregar histórico: {str(e)}\033[0m")

def limpar(chave: bytes):
    try:
        print("\n\033[1;31m" + "!" * 60)
        print(" ATENÇÃO: Esta ação é IRREVERSÍVEL! ".center(60, ' '))
        print("!" * 60 + "\033[0m")
        
        confirmacao = input("\n\033[33mDigite 'APAGAR TUDO' para confirmar: \033[0m").strip().upper()
        if confirmacao != "APAGAR TUDO":
            print("\033[33mOperação cancelada.\033[0m")
            return

        escrever_arquivo_cifrado("", chave)
        print("\n\033[32m✓ Diário totalmente limpo com sucesso!\033[0m\n")

    except Exception as e:
        print(f"\033[31mErro ao limpar: {str(e)}\033[0m")

def buscar(chave: bytes):
    try:
        conteudo = ler_arquivo_cifrado(chave)
        if not conteudo:
            print("\n\033[33mNenhuma anotação para buscar.\033[0m")
            return

        termo = input("\n\033[33mDigite o termo de busca: \033[0m").lower()
        entradas = [e for e in conteudo.split(SEPARADOR) if termo in e.lower()]
        
        print("\n\033[1;36m" + "═" * 60)
        print(f" Resultados ({len(entradas)} encontrados) ".center(60, ' '))
        print("═" * 60 + "\033[0m")
        
        for idx, entrada in enumerate(reversed(entradas), 1):
            partes = entrada.split("\n", 1)
            if len(partes) < 2:
                continue
                
            data_hora, texto = partes[0][1:-1], partes[1].strip()
            print(f"\n\033[1;34mResultado #{idx}\033[0m")
            print(f"\033[35mData/Hora: {data_hora}\033[0m")
            print("\033[37m" + texto + "\033[0m")
            print("-" * 60)

    except Exception as e:
        print(f"\033[31mErro na busca: {str(e)}\033[0m")

def editar_excluir(chave: bytes):
    try:
        conteudo = ler_arquivo_cifrado(chave)
        entradas = [e.strip() for e in conteudo.split(SEPARADOR) if e.strip()]
        
        if not entradas:
            print("\n\033[33mNenhuma entrada para editar.\033[0m")
            return

        print("\n\033[1;36m" + "═" * 60)
        print(" Entradas Disponíveis ".center(60, ' '))
        print("═" * 60 + "\033[0m")
        for idx, entrada in enumerate(reversed(entradas)), 1:
            data = entrada.split("\n", 1)[0][1:-1]
            print(f"{idx}. {data}")

        num = input("\n\033[33mNúmero da entrada: \033[0m")
        if not num.isdigit() or not (1 <= int(num) <= len(entradas)):
            print("\033[31mNúmero inválido!\033[0m")
            return

        idx = len(entradas) - int(num)
        entrada = entradas[idx]
        cabecalho, texto = entrada.split("\n", 1)
        
        print("\n\033[1;36m" + "═" * 60)
        print(" Edição de Entrada ".center(60, ' '))
        print("═" * 60 + "\033[0m")
        print(f"\033[35mData original: {cabecalho[1:-1]}\033[0m")
        print("\033[37m" + texto.strip() + "\033[0m\n")
        
        acao = input("\033[33m[E]ditar/[X]cluir/[C]ancelar: \033[0m").upper()
        
        if acao == 'E':
            novo_texto = []
            print("\n\033[33mNovo conteúdo (linha vazia para finalizar):\033[0m")
            while True:
                linha = input()
                if not linha.strip():
                    break
                novo_texto.append(linha)

            if novo_texto:
                entradas[idx] = f"{cabecalho}\n" + "\n".join(novo_texto)
                escrever_arquivo_cifrado(SEPARADOR.join(entradas), chave)
                print("\n\033[32m✓ Entrada atualizada!\033[0m")
            else:
                print("\033[33mEdição cancelada.\033[0m")

        elif acao == 'X':
            confirmacao = input("\033[33mConfirmar exclusão? (S/N): \033[0m").upper()
            if confirmacao == 'S':
                del entradas[idx]
                escrever_arquivo_cifrado(SEPARADOR.join(entradas), chave)
                print("\n\033[32m✓ Entrada excluída!\033[0m")
            else:
                print("\033[33mExclusão cancelada.\033[0m")
        else:
            print("\033[33mOperação cancelada.\033[0m")

    except Exception as e:
        print(f"\033[31mErro na edição: {str(e)}\033[0m")