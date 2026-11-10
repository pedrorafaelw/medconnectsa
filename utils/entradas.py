"""Funções auxiliares de interface no terminal: exibição e leitura de dados.

Cada função de leitura repete a pergunta até receber um valor válido,
garantindo que o restante do sistema só receba dados corretos.
"""
import math
import os

LARGURA = 30
CARACTERES_IGNORADOS = ' .-()/'


def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


def cabecalho(texto):
    limpar_tela()
    print('=' * LARGURA)
    print(texto.center(LARGURA))
    print('=' * LARGURA)


def pausar():
    input('\nPressione ENTER para continuar...')


def exibir_lista(itens, mensagem_vazia):
    """Imprime cada item da lista ou uma mensagem caso ela esteja vazia."""
    if not itens:
        print(mensagem_vazia)
        return
    for item in itens:
        print(item)


def ler_texto(mensagem, obrigatorio=True):
    while True:
        valor = input(mensagem).strip()
        if valor or not obrigatorio:
            return valor
        print('Este campo não pode ficar vazio.')


def ler_opcao(mensagem, opcoes_validas):
    while True:
        valor = input(mensagem).strip()
        if valor in opcoes_validas:
            return valor
        print(f'Opção inválida. Escolha entre: {", ".join(opcoes_validas)}.')


def ler_validado(mensagem, validador, mensagem_erro, obrigatorio=True, limpar=False):
    """Lê um texto até que `validador(texto)` retorne True.

    obrigatorio=False permite ENTER vazio (retorna '').
    limpar=True remove espaços, pontos, traços e parênteses (útil para CPF e telefone).
    """
    while True:
        valor = input(mensagem).strip()
        if limpar:
            valor = ''.join(c for c in valor if c not in CARACTERES_IGNORADOS)
        if not valor and not obrigatorio:
            return ''
        if validador(valor):
            return valor
        print(mensagem_erro)


def ler_inteiro(mensagem):
    while True:
        valor = input(mensagem).strip()
        if valor.isdigit():
            return int(valor)
        print('Digite um número inteiro válido.')


def ler_valor(mensagem):
    """Lê um valor monetário positivo. Aceita '350', '350.50', '350,50' ou '1.350,50'."""
    while True:
        texto = input(mensagem).replace('R$', '').strip()
        if ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        try:
            valor = float(texto)
        except ValueError:
            print('Valor inválido. Exemplo: 350,00')
            continue
        if not math.isfinite(valor) or valor <= 0:
            print('O valor deve ser um número maior que zero.')
            continue
        return round(valor, 2)


def confirmar(mensagem):
    return ler_opcao(f'{mensagem} (s/n): ', ['s', 'n', 'S', 'N']).lower() == 's'
