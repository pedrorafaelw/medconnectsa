"""Funções de validação de dados de entrada.

Todas as funções retornam True ou False e nunca lançam exceções,
podendo ser usadas com segurança em qualquer ponto do sistema.
"""
import re
from datetime import date, datetime

FORMATO_DATA = '%d/%m/%Y'
ANO_MINIMO = 1900


def validar_email(email):
    """Valida um email no formato usuario@dominio.ext."""
    padrao = r'[\w.+-]+@[\w-]+(\.[\w-]+)+'
    return isinstance(email, str) and re.fullmatch(padrao, email.strip()) is not None


def validar_data(data):
    """Valida uma data no formato DD/MM/AAAA e se ela existe no calendário."""
    if not isinstance(data, str) or not re.fullmatch(r'\d{2}/\d{2}/\d{4}', data.strip()):
        return False
    try:
        datetime.strptime(data.strip(), FORMATO_DATA)
    except ValueError:
        return False
    return True


def validar_data_nascimento(data):
    """Valida uma data de nascimento: formato correto, não futura e a partir de 1900."""
    if not validar_data(data):
        return False
    nascimento = datetime.strptime(data.strip(), FORMATO_DATA).date()
    return ANO_MINIMO <= nascimento.year and nascimento <= date.today()


def validar_data_agendamento(data):
    """Valida uma data de agendamento: formato correto e não anterior a hoje."""
    if not validar_data(data):
        return False
    return datetime.strptime(data.strip(), FORMATO_DATA).date() >= date.today()


def validar_hora(hora):
    """Valida um horário no formato HH:MM (00:00 a 23:59)."""
    if not isinstance(hora, str) or not re.fullmatch(r'\d{2}:\d{2}', hora.strip()):
        return False
    horas, minutos = map(int, hora.strip().split(':'))
    return 0 <= horas <= 23 and 0 <= minutos <= 59


def validar_telefone(telefone):
    """Valida um telefone com DDD: fixo (10 dígitos) ou celular (11 dígitos, iniciando em 9)."""
    if not isinstance(telefone, str) or not telefone.isdigit():
        return False
    if len(telefone) not in (10, 11) or telefone[0] == '0' or telefone[1] == '0':
        return False
    if len(telefone) == 11 and telefone[2] != '9':
        return False
    return True


def validar_cpf(cpf):
    """Valida se o CPF possui exatamente 11 dígitos numéricos."""
    return isinstance(cpf, str) and cpf.isdigit() and len(cpf) == 11
