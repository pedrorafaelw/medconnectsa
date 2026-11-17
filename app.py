"""MedConnect System - aplicação principal de terminal."""
import sqlite3
from getpass import getpass

import banco
from modelos.consulta import Consulta
from modelos.financeiro import Financeiro
from modelos.medico import Medico
from modelos.paciente import Paciente
from utils import formatacoes, validacoes
from utils.entradas import (
    cabecalho, confirmar, exibir_lista, ler_inteiro, ler_opcao,
    ler_texto, ler_validado, ler_valor, pausar,
)

USUARIO = 'admin'
SENHA = 'admin123'
MAX_TENTATIVAS = 3

MSG_CPF = 'CPF inválido. Informe 11 dígitos numéricos.'
MSG_CRM = 'CRM inválido. Informe de 4 a 6 dígitos numéricos.'
MSG_TELEFONE = 'Telefone inválido. Informe DDD + número (10 ou 11 dígitos).'
MSG_EMAIL = 'Email inválido. Exemplo: nome@dominio.com'


# ======================================================================
# Utilitários de navegação
# ======================================================================

def executar_menu(titulo, opcoes):
    """Exibe um submenu em loop. `opcoes` mapeia a tecla -> (descrição, função)."""
    while True:
        cabecalho(titulo)
        for chave, (descricao, _) in opcoes.items():
            print(f'{chave} - {descricao}')
        print('0 - Voltar ao menu principal')
        escolha = ler_opcao('\nEscolha uma opção: ', list(opcoes) + ['0'])
        if escolha == '0':
            return
        descricao, acao = opcoes[escolha]
        cabecalho(descricao.upper())
        try:
            acao()
        except sqlite3.Error as erro:
            print(f'\nErro no banco de dados: {erro}')
            print('A operação não foi concluída.')
        pausar()


def ler_cpf(mensagem='CPF: ', obrigatorio=True):
    return ler_validado(mensagem, Paciente.validar_cpf, MSG_CPF, obrigatorio, limpar=True)


def ler_crm(mensagem='CRM: '):
    return ler_validado(mensagem, Medico.validar_crm, MSG_CRM)


def ler_telefone(mensagem='Telefone com DDD: ', obrigatorio=True):
    return ler_validado(mensagem, validacoes.validar_telefone, MSG_TELEFONE, obrigatorio, limpar=True)


def ler_tipo_consulta():
    escolha = ler_opcao('Tipo (1 - Presencial / 2 - Online): ', ['1', '2'])
    return 'online' if escolha == '2' else 'presencial'


def selecionar_paciente():
    paciente = Paciente.buscar_por_cpf(ler_cpf('CPF do paciente: '))
    if paciente is None:
        print('Paciente não encontrado.')
    return paciente


def selecionar_medico():
    medico = Medico.buscar_por_crm(ler_crm('CRM do médico: '))
    if medico is None:
        print('Médico não encontrado.')
    return medico


def selecionar_consulta():
    consulta = Consulta.buscar_por_id(ler_inteiro('Número da consulta: '))
    if consulta is None:
        print('Consulta não encontrada.')
    return consulta


def selecionar_lancamento():
    consulta = selecionar_consulta()
    if consulta is None:
        return None
    registro = Financeiro.buscar_por_consulta(consulta)
    if registro is None:
        print('Esta consulta não possui lançamento financeiro.')
    return registro


def tem_consulta_agendada(consultas):
    return any(consulta.status == 'agendada' for consulta in consultas)


# ======================================================================
# Gestão de Pacientes
# ======================================================================

def cadastrar_paciente():
    nome = ler_texto('Nome: ')
    cpf = ler_cpf('CPF (11 dígitos): ')
    if Paciente.buscar_por_cpf(cpf):
        print('Já existe um paciente cadastrado com este CPF.')
        return
    nascimento = ler_validado(
        'Data de nascimento (DD/MM/AAAA): ', validacoes.validar_data_nascimento,
        'Data inválida. Use DD/MM/AAAA, não futura e a partir de 1900.',
    )
    telefone = ler_telefone()
    email = ler_validado('Email (ENTER para pular): ', validacoes.validar_email, MSG_EMAIL, obrigatorio=False)
    try:
        paciente = Paciente(nome, cpf, nascimento, telefone, email or None)
    except ValueError as erro:
        print(f'Erro ao cadastrar: {erro}')
        return
    print('\nPaciente cadastrado com sucesso!\n')
    print(paciente)


def cadastrar_paciente_particular():
    print('Cadastro rápido: sem email e com a data de hoje como data de nascimento.\n')
    nome = ler_texto('Nome: ')
    cpf = ler_cpf('CPF (11 dígitos): ')
    telefone = ler_telefone()
    try:
        paciente = Paciente.cadastrar_particular(nome, cpf, telefone)
    except ValueError as erro:
        print(f'Erro ao cadastrar: {erro}')
        return
    print('\nPaciente cadastrado com sucesso!\n')
    print(paciente)


def listar_pacientes():
    exibir_lista(Paciente.pacientes, 'Nenhum paciente cadastrado.')


def listar_pacientes_ativos():
    exibir_lista(Paciente.listar_ativos(), 'Nenhum paciente ativo.')


def buscar_paciente():
    paciente = selecionar_paciente()
    if paciente:
        print(paciente)


def editar_paciente():
    paciente = selecionar_paciente()
    if paciente is None:
        return
    print(paciente)
    print('\nDeixe em branco (ENTER) para manter o valor atual.\n')
    nome = ler_texto('Novo nome: ', obrigatorio=False)
    telefone = ler_telefone('Novo telefone: ', obrigatorio=False)
    email = ler_validado('Novo email: ', validacoes.validar_email, MSG_EMAIL, obrigatorio=False)
    try:
        paciente.atualizar(nome=nome or None, telefone=telefone or None, email=email or None)
    except ValueError as erro:
        print(f'Erro ao atualizar: {erro}')
        return
    print('\nPaciente atualizado com sucesso!\n')
    print(paciente)


def alternar_status_paciente():
    paciente = selecionar_paciente()
    if paciente is None:
        return
    print(paciente)
    if confirmar(f'\nDeseja alterar o status de {paciente.nome_formatado}?'):
        paciente.alternar_status()
        print(f'Status alterado para: {paciente.status}')


def excluir_paciente():
    paciente = selecionar_paciente()
    if paciente is None:
        return
    if tem_consulta_agendada(Consulta.por_paciente(paciente)):
        print('Não é possível excluir: o paciente possui consulta agendada.')
        return
    print(paciente)
    if confirmar('\nConfirma a exclusão deste paciente?'):
        try:
            paciente.excluir()
        except ValueError as erro:
            print(f'Erro ao excluir: {erro}')
            return
        print('Paciente excluído com sucesso.')


def gestao_pacientes():
    executar_menu('GESTÃO DE PACIENTES', {
        '1': ('Cadastrar paciente', cadastrar_paciente),
        '2': ('Cadastro particular (rápido)', cadastrar_paciente_particular),
        '3': ('Listar pacientes', listar_pacientes),
        '4': ('Listar pacientes ativos', listar_pacientes_ativos),
        '5': ('Buscar paciente por CPF', buscar_paciente),
        '6': ('Editar paciente', editar_paciente),
        '7': ('Ativar/Desativar paciente', alternar_status_paciente),
        '8': ('Excluir paciente', excluir_paciente),
    })


# ======================================================================
# Gestão de Médicos
# ======================================================================

def cadastrar_medico():
    nome = ler_texto('Nome: ')
    crm = ler_crm('CRM (4 a 6 dígitos): ')
    if Medico.buscar_por_crm(crm):
        print('Já existe um médico cadastrado com este CRM.')
        return
    especialidade = ler_texto('Especialidade: ')
    telefone = ler_telefone()
    try:
        medico = Medico(nome, crm, especialidade, telefone)
    except ValueError as erro:
        print(f'Erro ao cadastrar: {erro}')
        return
    print('\nMédico cadastrado com sucesso!\n')
    print(medico)


def listar_medicos():
    exibir_lista(Medico.medicos, 'Nenhum médico cadastrado.')


def listar_por_especialidade():
    especialidades = Medico.especialidades()
    if not especialidades:
        print('Nenhum médico cadastrado.')
        return
    print('Especialidades cadastradas: ' + ', '.join(especialidades) + '\n')
    especialidade = ler_texto('Especialidade: ')
    exibir_lista(Medico.por_especialidade(especialidade), 'Nenhum médico encontrado nesta especialidade.')


def buscar_medico():
    medico = selecionar_medico()
    if medico:
        print(medico)


def editar_medico():
    medico = selecionar_medico()
    if medico is None:
        return
    print(medico)
    print('\nDeixe em branco (ENTER) para manter o valor atual.\n')
    nome = ler_texto('Novo nome: ', obrigatorio=False)
    especialidade = ler_texto('Nova especialidade: ', obrigatorio=False)
    telefone = ler_telefone('Novo telefone: ', obrigatorio=False)
    try:
        medico.atualizar(nome=nome or None, especialidade=especialidade or None, telefone=telefone or None)
    except ValueError as erro:
        print(f'Erro ao atualizar: {erro}')
        return
    print('\nMédico atualizado com sucesso!\n')
    print(medico)


def alternar_disponibilidade_medico():
    medico = selecionar_medico()
    if medico is None:
        return
    if tem_consulta_agendada(Consulta.por_medico(medico)):
        print('Não é possível alterar: o médico possui consulta agendada.')
        print('Realize ou cancele a consulta para liberá-lo.')
        return
    print(medico)
    if confirmar(f'\nDeseja alterar a disponibilidade de {medico.nome_formatado}?'):
        medico.alternar_disponibilidade()
        print(f'Disponibilidade alterada para: {medico.status}')


def excluir_medico():
    medico = selecionar_medico()
    if medico is None:
        return
    if tem_consulta_agendada(Consulta.por_medico(medico)):
        print('Não é possível excluir: o médico possui consulta agendada.')
        return
    print(medico)
    if confirmar('\nConfirma a exclusão deste médico?'):
        try:
            medico.excluir()
        except ValueError as erro:
            print(f'Erro ao excluir: {erro}')
            return
        print('Médico excluído com sucesso.')


def gestao_medicos():
    executar_menu('GESTÃO DE MÉDICOS', {
        '1': ('Cadastrar médico', cadastrar_medico),
        '2': ('Listar médicos', listar_medicos),
        '3': ('Listar por especialidade', listar_por_especialidade),
        '4': ('Buscar médico por CRM', buscar_medico),
        '5': ('Editar médico', editar_medico),
        '6': ('Alterar disponibilidade', alternar_disponibilidade_medico),
        '7': ('Excluir médico', excluir_medico),
    })


# ======================================================================
# Gestão de Consultas
# ======================================================================

def agendar_consulta():
    paciente = selecionar_paciente()
    if paciente is None:
        return
    if not paciente.ativo:
        print('Não é possível agendar: o paciente está inativo.')
        return

    disponiveis = Medico.listar_disponiveis()
    if not disponiveis:
        print('Nenhum médico disponível no momento.')
        return
    print('\nMédicos disponíveis:')
    for medico in disponiveis:
        print(f'  CRM {medico.crm} - {medico.nome_formatado} ({medico.especialidade.title()})')
    print()

    medico = selecionar_medico()
    if medico is None:
        return
    data = ler_validado(
        'Data (DD/MM/AAAA): ', validacoes.validar_data_agendamento,
        'Data inválida ou no passado. Use DD/MM/AAAA.',
    )
    hora = ler_validado('Hora (HH:MM): ', validacoes.validar_hora, 'Hora inválida. Use HH:MM.')
    tipo = ler_tipo_consulta()
    try:
        consulta = Consulta.agendar(paciente, medico, data, hora, tipo)
    except ValueError as erro:
        print(f'Erro ao agendar: {erro}')
        return
    print('\nConsulta agendada com sucesso!\n')
    print(consulta)


def listar_consultas():
    exibir_lista([c.resumo for c in Consulta.consultas], 'Nenhuma consulta registrada.')


def consultas_do_dia():
    data = ler_validado('Data (DD/MM/AAAA): ', validacoes.validar_data, 'Data inválida. Use DD/MM/AAAA.')
    print(f'\nConsultas em {formatacoes.formatar_data_por_extenso(data)}:\n')
    exibir_lista(Consulta.consultas_do_dia(data), 'Nenhuma consulta nesta data.')


def buscar_consulta():
    consulta = selecionar_consulta()
    if consulta:
        print(consulta)


def remarcar_consulta():
    consulta = selecionar_consulta()
    if consulta is None:
        return
    if consulta.status != 'agendada':
        print(f'Não é possível remarcar: a consulta está {consulta.status}.')
        return
    print(consulta)
    data = ler_validado(
        'Nova data (DD/MM/AAAA): ', validacoes.validar_data_agendamento,
        'Data inválida ou no passado. Use DD/MM/AAAA.',
    )
    hora = ler_validado('Nova hora (HH:MM): ', validacoes.validar_hora, 'Hora inválida. Use HH:MM.')
    try:
        consulta.remarcar(data, hora)
    except ValueError as erro:
        print(f'Erro ao remarcar: {erro}')
        return
    print('\nConsulta remarcada com sucesso!\n')
    print(consulta)


def realizar_consulta():
    consulta = selecionar_consulta()
    if consulta is None:
        return
    if consulta.status != 'agendada':
        print(f'Não é possível realizar: a consulta está {consulta.status}.')
        return
    print(consulta)
    valor = ler_valor('\nValor da consulta (R$): ')
    try:
        consulta.realizar()
        registro = Financeiro(consulta, valor)
    except ValueError as erro:
        print(f'Erro ao realizar consulta: {erro}')
        return
    print('\nConsulta realizada! O médico está disponível novamente.')
    print(f'Cobrança de {registro.valor_formatado} lançada como {registro.status_pagamento}.')


def cancelar_consulta():
    consulta = selecionar_consulta()
    if consulta is None:
        return
    if consulta.status != 'agendada':
        print(f'Não é possível cancelar: a consulta está {consulta.status}.')
        return
    print(consulta)
    if confirmar('\nConfirma o cancelamento?'):
        consulta.cancelar()
        print('Consulta cancelada. O médico está disponível novamente.')


def gestao_consultas():
    executar_menu('GESTÃO DE CONSULTAS', {
        '1': ('Agendar consulta', agendar_consulta),
        '2': ('Listar consultas', listar_consultas),
        '3': ('Consultas do dia', consultas_do_dia),
        '4': ('Buscar consulta por número', buscar_consulta),
        '5': ('Remarcar consulta', remarcar_consulta),
        '6': ('Realizar consulta', realizar_consulta),
        '7': ('Cancelar consulta', cancelar_consulta),
    })


# ======================================================================
# Financeiro
# ======================================================================

def lancar_cobranca():
    sem_cobranca = [
        c for c in Consulta.por_status('realizada') if Financeiro.buscar_por_consulta(c) is None
    ]
    if not sem_cobranca:
        print('Não há consultas realizadas sem cobrança.')
        return
    print('Consultas realizadas sem cobrança:')
    for consulta in sem_cobranca:
        print(f'  {consulta.resumo}')
    print()
    consulta = selecionar_consulta()
    if consulta is None:
        return
    valor = ler_valor('Valor (R$): ')
    try:
        registro = Financeiro(consulta, valor)
    except ValueError as erro:
        print(f'Erro ao lançar cobrança: {erro}')
        return
    print(f'\nCobrança de {registro.valor_formatado} lançada com sucesso.')


def listar_lancamentos():
    exibir_lista(Financeiro.registros, 'Nenhum lançamento registrado.')


def listar_pendentes():
    exibir_lista(Financeiro.listar_pendentes(), 'Nenhum pagamento pendente.')


def registrar_pagamento():
    registro = selecionar_lancamento()
    if registro is None:
        return
    print(registro)
    if registro.registrar_pagamento():
        print('\nPagamento registrado com sucesso.')
    else:
        print('\nEste pagamento já havia sido registrado.')


def alterar_valor_lancamento():
    registro = selecionar_lancamento()
    if registro is None:
        return
    if registro.pago:
        print('Não é possível alterar o valor de um lançamento já pago.')
        return
    print(registro)
    novo_valor = ler_valor('\nNovo valor (R$): ')
    try:
        registro.alterar_valor(novo_valor)
    except ValueError as erro:
        print(f'Erro ao alterar valor: {erro}')
        return
    print(f'Valor alterado para {registro.valor_formatado}.')


def excluir_lancamento():
    registro = selecionar_lancamento()
    if registro is None:
        return
    if registro.pago:
        print('Não é possível excluir um lançamento já pago.')
        return
    print(registro)
    if confirmar('\nConfirma a exclusão deste lançamento?'):
        try:
            registro.excluir()
        except ValueError as erro:
            print(f'Erro ao excluir: {erro}')
            return
        print('Lançamento excluído com sucesso.')


def relatorio_financeiro():
    print(Financeiro.relatorio_financeiro())


def financeiro():
    executar_menu('FINANCEIRO', {
        '1': ('Lançar cobrança', lancar_cobranca),
        '2': ('Listar lançamentos', listar_lancamentos),
        '3': ('Listar pendentes', listar_pendentes),
        '4': ('Registrar pagamento', registrar_pagamento),
        '5': ('Alterar valor', alterar_valor_lancamento),
        '6': ('Excluir lançamento', excluir_lancamento),
        '7': ('Relatório financeiro', relatorio_financeiro),
    })


# ======================================================================
# Relatórios
# ======================================================================

def resumo_geral():
    ativos = len(Paciente.listar_ativos())
    disponiveis = len(Medico.listar_disponiveis())
    print(f'Pacientes:  {len(Paciente.pacientes)} ({ativos} ativos)')
    print(f'Médicos:    {len(Medico.medicos)} ({disponiveis} disponíveis)')
    print(f'Consultas:  {len(Consulta.consultas)}')
    for status in ('agendada', 'realizada', 'cancelada'):
        print(f'  - {status.capitalize()}s: {len(Consulta.por_status(status))}')
    print(f'Recebido:   {formatacoes.formatar_moeda(Financeiro.total_recebido())}')
    print(f'Pendente:   {formatacoes.formatar_moeda(Financeiro.total_pendente())}')


def relatorio_consultas_por_status():
    escolha = ler_opcao('Status (1 - Agendada / 2 - Realizada / 3 - Cancelada): ', ['1', '2', '3'])
    status = {'1': 'agendada', '2': 'realizada', '3': 'cancelada'}[escolha]
    print()
    exibir_lista([c.resumo for c in Consulta.por_status(status)], f'Nenhuma consulta {status}.')


def relatorio_consultas_por_medico():
    medico = selecionar_medico()
    if medico:
        print(f'\nConsultas de {medico.nome_formatado}:\n')
        exibir_lista([c.resumo for c in Consulta.por_medico(medico)], 'Nenhuma consulta para este médico.')


def relatorio_historico_paciente():
    paciente = selecionar_paciente()
    if paciente:
        print(f'\nHistórico de {paciente.nome_formatado}:\n')
        exibir_lista([c.resumo for c in Consulta.por_paciente(paciente)], 'Nenhuma consulta para este paciente.')


def relatorios():
    executar_menu('RELATÓRIOS', {
        '1': ('Resumo geral', resumo_geral),
        '2': ('Consultas por status', relatorio_consultas_por_status),
        '3': ('Consultas por médico', relatorio_consultas_por_medico),
        '4': ('Histórico do paciente', relatorio_historico_paciente),
        '5': ('Relatório financeiro', relatorio_financeiro),
    })


# ======================================================================
# Login e menu principal
# ======================================================================

def login():
    """Pede usuário e senha. Retorna True se o acesso for liberado."""
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        cabecalho('MEDCONNECT - LOGIN')
        usuario = input('Usuário: ').strip()
        senha = input('Senha: ')
        if usuario == USUARIO and senha == SENHA:
            return True
        restantes = MAX_TENTATIVAS - tentativa
        if restantes:
            print(f'\nUsuário ou senha incorretos. Tentativas restantes: {restantes}')
            pausar()
    return False


def menu_principal():
    acoes = {
        '1': gestao_pacientes,
        '2': gestao_medicos,
        '3': gestao_consultas,
        '4': financeiro,
        '5': relatorios,
    }
    while True:
        cabecalho('MEDCONNECT SYSTEM')
        print('1 - Gestão de Pacientes')
        print('2 - Gestão de Médicos')
        print('3 - Gestão de Consultas')
        print('4 - Financeiro')
        print('5 - Relatórios')
        print('6 - Sair')
        escolha = ler_opcao('\nEscolha uma opção: ', ['1', '2', '3', '4', '5', '6'])
        if escolha == '6':
            print('\nSaindo do sistema. Até logo!')
            return
        acoes[escolha]()


def main():
    try:
        banco.inicializar()
    except sqlite3.Error as erro:
        print(f'Não foi possível abrir o banco de dados ({banco.CAMINHO_PADRAO}): {erro}')
        return
    try:
        if not login():
            print('\nNúmero máximo de tentativas atingido. Acesso bloqueado.')
            return
        menu_principal()
    except (KeyboardInterrupt, EOFError):
        print('\n\nSistema encerrado pelo usuário.')
    finally:
        banco.fechar()


if __name__ == '__main__':
    main()
