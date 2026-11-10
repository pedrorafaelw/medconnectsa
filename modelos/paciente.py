"""Módulo Paciente: cadastro e controle de pacientes."""
from datetime import date

from utils import formatacoes, validacoes


class Paciente:
    """Representa um paciente da MedConnect."""

    pacientes = []

    def __init__(self, nome, cpf, data_nascimento, telefone, email=None):
        nome = str(nome).strip()
        if not nome:
            raise ValueError('O nome não pode ficar vazio.')
        if not Paciente.validar_cpf(cpf):
            raise ValueError('CPF inválido. Deve conter 11 dígitos numéricos.')
        if Paciente.buscar_por_cpf(cpf):
            raise ValueError('Já existe um paciente cadastrado com este CPF.')
        if not validacoes.validar_data_nascimento(data_nascimento):
            raise ValueError('Data de nascimento inválida. Use DD/MM/AAAA (não pode ser futura).')
        if not validacoes.validar_telefone(telefone):
            raise ValueError('Telefone inválido. Informe DDD + número.')
        if email and not validacoes.validar_email(email):
            raise ValueError('Email inválido.')

        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento
        self.telefone = telefone
        self.email = email or None
        self._ativo = True
        Paciente.pacientes.append(self)

    def __str__(self):
        linha = '=' * 30
        return (
            f'{linha}\n'
            f'Nome: {self.nome_formatado}\n'
            f'CPF: {formatacoes.formatar_cpf(self.cpf)}\n'
            f'Nascimento: {formatacoes.formatar_data_por_extenso(self.data_nascimento)}'
            f' ({self.idade} anos)\n'
            f'Telefone: {formatacoes.formatar_telefone(self.telefone)}\n'
            f'Email: {self.email or "Não informado"}\n'
            f'Status: {self.status}\n'
            f'{linha}'
        )

    @property
    def nome_formatado(self):
        return self.nome.title()

    @property
    def ativo(self):
        return self._ativo

    @property
    def status(self):
        return 'Ativo' if self._ativo else 'Inativo'

    @property
    def idade(self):
        nascimento = formatacoes.texto_para_data(self.data_nascimento)
        hoje = date.today()
        fez_aniversario = (hoje.month, hoje.day) >= (nascimento.month, nascimento.day)
        return hoje.year - nascimento.year - (0 if fez_aniversario else 1)

    @classmethod
    def cadastrar_particular(cls, nome, cpf, telefone):
        """Cadastro rápido: sem email e com a data atual como data de nascimento."""
        hoje = date.today().strftime(validacoes.FORMATO_DATA)
        return cls(nome, cpf, hoje, telefone, None)

    @classmethod
    def buscar_por_cpf(cls, cpf):
        for paciente in cls.pacientes:
            if paciente.cpf == cpf:
                return paciente
        return None

    @classmethod
    def listar_ativos(cls):
        return [paciente for paciente in cls.pacientes if paciente.ativo]

    @staticmethod
    def validar_cpf(cpf):
        return validacoes.validar_cpf(cpf)

    def alternar_status(self):
        self._ativo = not self._ativo

    def atualizar(self, nome=None, telefone=None, email=None):
        """Atualiza os campos informados (None mantém o valor atual)."""
        if nome is not None:
            nome = nome.strip()
            if not nome:
                raise ValueError('O nome não pode ficar vazio.')
        if telefone is not None and not validacoes.validar_telefone(telefone):
            raise ValueError('Telefone inválido. Informe DDD + número.')
        if email is not None and not validacoes.validar_email(email):
            raise ValueError('Email inválido.')

        if nome is not None:
            self.nome = nome
        if telefone is not None:
            self.telefone = telefone
        if email is not None:
            self.email = email

    def excluir(self):
        if self in Paciente.pacientes:
            Paciente.pacientes.remove(self)
