"""Módulo Médico: cadastro e controle de disponibilidade dos médicos."""
from banco import repositorios
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
        repositorios.inserir_medico(
            self.crm, self.nome, self.especialidade, self.telefone, self._disponivel,
        )
        Medico.medicos.append(self)

    @classmethod
    def _de_registro(cls, linha):
        """Monta um médico a partir de uma linha do banco (sem validar nem gravar de novo)."""
        medico = cls.__new__(cls)
        medico.nome = linha['nome']
        medico.crm = linha['crm']
        medico.especialidade = linha['especialidade']
        medico.telefone = linha['telefone']
        medico._disponivel = bool(linha['disponivel'])
        return medico

    @classmethod
    def carregar(cls):
        """Substitui a lista em memória pelos médicos gravados no banco."""
        cls.medicos[:] = [cls._de_registro(linha) for linha in repositorios.listar_medicos()]

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

    def _definir_disponibilidade(self, disponivel):
        repositorios.definir_disponibilidade_medico(self.crm, disponivel)
        self._disponivel = disponivel

    def alternar_disponibilidade(self):
        self._definir_disponibilidade(not self._disponivel)

    def ocupar(self):
        self._definir_disponibilidade(False)

    def liberar(self):
        self._definir_disponibilidade(True)

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

        novo_nome = self.nome if nome is None else nome
        nova_especialidade = self.especialidade if especialidade is None else especialidade
        novo_telefone = self.telefone if telefone is None else telefone
        repositorios.atualizar_medico(self.crm, novo_nome, nova_especialidade, novo_telefone)
        self.nome, self.especialidade, self.telefone = novo_nome, nova_especialidade, novo_telefone

    def excluir(self):
        """Exclui o médico. Quem já tem consultas no histórico não pode ser excluído."""
        if repositorios.medico_tem_consultas(self.crm):
            raise ValueError(
                'O médico possui consultas no histórico e não pode ser excluído. '
                'Marque-o como indisponível em vez disso.'
            )
        repositorios.excluir_medico(self.crm)
        if self in Medico.medicos:
            Medico.medicos.remove(self)
