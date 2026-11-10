"""Módulo Médico: cadastro e controle de disponibilidade dos médicos."""
from utils import formatacoes, validacoes


class Medico:
    """Representa um médico da MedConnect."""

    medicos = []

    def __init__(self, nome, crm, especialidade, telefone):
        nome = str(nome).strip()
        especialidade = str(especialidade).strip()
        if not nome:
            raise ValueError('O nome não pode ficar vazio.')
        if not Medico.validar_crm(crm):
            raise ValueError('CRM inválido. Deve conter apenas números, entre 4 e 6 dígitos.')
        if Medico.buscar_por_crm(crm):
            raise ValueError('Já existe um médico cadastrado com este CRM.')
        if not especialidade:
            raise ValueError('A especialidade não pode ficar vazia.')
        if not validacoes.validar_telefone(telefone):
            raise ValueError('Telefone inválido. Informe DDD + número.')

        self.nome = nome
        self.crm = crm
        self.especialidade = especialidade
        self.telefone = telefone
        self._disponivel = True
        Medico.medicos.append(self)

    def __str__(self):
        linha = '=' * 30
        return (
            f'{linha}\n'
            f'Médico: {self.nome_formatado}\n'
            f'CRM: {self.crm_formatado}\n'
            f'Especialidade: {self.especialidade.title()}\n'
            f'Telefone: {formatacoes.formatar_telefone(self.telefone)}\n'
            f'Status: {self.status}\n'
            f'{linha}'
        )

    @property
    def nome_formatado(self):
        return f'Dr(a). {self.nome.title()}'

    @property
    def disponivel(self):
        return self._disponivel

    @property
    def status(self):
        return 'Disponível' if self._disponivel else 'Indisponível'

    @property
    def crm_formatado(self):
        return f'CRM-SP {self.crm}'

    @classmethod
    def por_especialidade(cls, especialidade):
        alvo = especialidade.strip().lower()
        return [medico for medico in cls.medicos if medico.especialidade.lower() == alvo]

    @classmethod
    def buscar_por_crm(cls, crm):
        for medico in cls.medicos:
            if medico.crm == crm:
                return medico
        return None

    @classmethod
    def listar_disponiveis(cls):
        return [medico for medico in cls.medicos if medico.disponivel]

    @classmethod
    def especialidades(cls):
        return sorted({medico.especialidade.title() for medico in cls.medicos})

    @staticmethod
    def validar_crm(crm):
        return isinstance(crm, str) and crm.isdigit() and 4 <= len(crm) <= 6

    def alternar_disponibilidade(self):
        self._disponivel = not self._disponivel

    def ocupar(self):
        self._disponivel = False

    def liberar(self):
        self._disponivel = True

    def atualizar(self, nome=None, especialidade=None, telefone=None):
        """Atualiza os campos informados (None mantém o valor atual)."""
        if nome is not None:
            nome = nome.strip()
            if not nome:
                raise ValueError('O nome não pode ficar vazio.')
        if especialidade is not None:
            especialidade = especialidade.strip()
            if not especialidade:
                raise ValueError('A especialidade não pode ficar vazia.')
        if telefone is not None and not validacoes.validar_telefone(telefone):
            raise ValueError('Telefone inválido. Informe DDD + número.')

        if nome is not None:
            self.nome = nome
        if especialidade is not None:
            self.especialidade = especialidade
        if telefone is not None:
            self.telefone = telefone

    def excluir(self):
        if self in Medico.medicos:
            Medico.medicos.remove(self)
