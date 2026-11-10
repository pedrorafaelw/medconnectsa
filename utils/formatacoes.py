"""Funções de formatação de dados para exibição."""
from datetime import datetime

FORMATO_DATA = '%d/%m/%Y'

MESES = (
    'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
    'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro',
)


def somente_digitos(texto):
    """Remove tudo que não for dígito de um texto."""
    return ''.join(caractere for caractere in str(texto) if caractere.isdigit())


def formatar_cpf(cpf):
    """'12345678900' -> '123.456.789-00'."""
    digitos = somente_digitos(cpf)
    if len(digitos) != 11:
        return str(cpf)
    return f'{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}'


def formatar_telefone(telefone):
    """'41999998888' -> '(41) 99999-8888' | '4133334444' -> '(41) 3333-4444'."""
    digitos = somente_digitos(telefone)
    if len(digitos) == 11:
        return f'({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}'
    if len(digitos) == 10:
        return f'({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}'
    return str(telefone)


def formatar_data_por_extenso(data):
    """'25/05/2026' -> '25 de maio de 2026'."""
    try:
        convertida = datetime.strptime(str(data).strip(), FORMATO_DATA)
    except ValueError:
        return 'Data inválida'
    return f'{convertida.day} de {MESES[convertida.month - 1]} de {convertida.year}'


def formatar_moeda(valor):
    """350 -> 'R$350,00' | 1350.5 -> 'R$1.350,50'."""
    texto = f'{valor:,.2f}'
    return 'R$' + texto.replace(',', '_').replace('.', ',').replace('_', '.')


def texto_para_data(data):
    """Converte 'DD/MM/AAAA' em um objeto date (lança ValueError se inválida)."""
    return datetime.strptime(str(data).strip(), FORMATO_DATA).date()
