"""Módulo Consulta: agendamento e ciclo de vida das consultas."""
from banco import repositorios
from modelos.medico import Medico
from modelos.paciente import Paciente
from utils import formatacoes, validacoes


class Consulta:
    """Representa uma consulta entre um paciente e um médico."""

    consultas = []

    def __init__(self, paciente, medico, data, hora, tipo='presencial'):
        if not isinstance(paciente, Paciente):
            raise ValueError('Paciente inválido.')
        if not isinstance(medico, Medico):
            raise ValueError('Médico inválido.')
        if not validacoes.validar_data(data):
            raise ValueError('Data inválida. Use DD/MM/AAAA.')
        if not validacoes.validar_hora(hora):
            raise ValueError('Hora inválida. Use HH:MM.')
        if not Consulta.validar_tipo(tipo):
            raise ValueError('Tipo de consulta inválido. Deve ser "presencial" ou "online".')

        self.paciente = paciente
        self.medico = medico
        self.data = data
        self.hora = hora
        self.tipo = tipo.strip().lower()
        self._status = 'agendada'
        # O número da consulta é gerado pelo banco (AUTOINCREMENT).
        self.id = repositorios.inserir_consulta(
            paciente.cpf, medico.crm, self.data, self.hora, self.tipo, self._status,
        )
        Consulta.consultas.append(self)

    @classmethod
    def _de_registro(cls, linha, pacientes, medicos):
        """Monta uma consulta a partir de uma linha do banco, ligando-a aos objetos já carregados."""
        consulta = cls.__new__(cls)
        consulta.id = linha['id']
        consulta.paciente = pacientes[linha['paciente_cpf']]
        consulta.medico = medicos[linha['medico_crm']]
        consulta.data = linha['data']
        consulta.hora = linha['hora']
        consulta.tipo = linha['tipo']
        consulta._status = linha['status']
        return consulta

    @classmethod
    def carregar(cls):
        """Substitui a lista em memória pelas consultas do banco. Carregue pacientes e médicos antes."""
        pacientes = {paciente.cpf: paciente for paciente in Paciente.pacientes}
        medicos = {medico.crm: medico for medico in Medico.medicos}
        cls.consultas[:] = [
            cls._de_registro(linha, pacientes, medicos) for linha in repositorios.listar_consultas()
        ]

    def __str__(self):
        linha = '=' * 30
        return (
            f'{linha}\n'
            f'Consulta nº {self.id}\n'
            f'Paciente: {self.paciente.nome_formatado}'
            f' (CPF {formatacoes.formatar_cpf(self.paciente.cpf)})\n'
            f'Médico: {self.medico.nome_formatado} - {self.medico.especialidade.title()}\n'
            f'Data: {formatacoes.formatar_data_por_extenso(self.data)} às {self.hora}\n'
            f'Tipo: {self.tipo.capitalize()}\n'
            f'Status: {self.status_formatado}\n'
            f'{linha}'
        )

    @property
    def status(self):
        return self._status

    @property
    def status_formatado(self):
        return self._status.upper()

    @property
    def resumo(self):
        return (
            f'#{self.id} | {self.data} {self.hora} | {self.paciente.nome_formatado} '
            f'com {self.medico.nome_formatado} | {self.tipo} | {self.status_formatado}'
        )

    def _exigir_agendada(self):
        if self._status != 'agendada':
            raise ValueError(f'Operação não permitida: a consulta está {self._status}.')

    def _definir_status(self, status):
        repositorios.definir_status_consulta(self.id, status)
        self._status = status

    def realizar(self):
        """Marca a consulta como realizada e libera o médico."""
        self._exigir_agendada()
        self._definir_status('realizada')
        self.medico.liberar()

    def cancelar(self):
        """Marca a consulta como cancelada e libera o médico."""
        self._exigir_agendada()
        self._definir_status('cancelada')
        self.medico.liberar()

    def remarcar(self, data, hora):
        self._exigir_agendada()
        if not validacoes.validar_data_agendamento(data):
            raise ValueError('Data inválida ou no passado. Use DD/MM/AAAA.')
        if not validacoes.validar_hora(hora):
            raise ValueError('Hora inválida. Use HH:MM.')
        repositorios.remarcar_consulta(self.id, data, hora)
        self.data = data
        self.hora = hora

    @classmethod
    def agendar(cls, paciente, medico, data, hora, tipo='presencial'):
        """Agenda uma consulta se o médico estiver disponível e o marca como indisponível."""
        if not isinstance(paciente, Paciente) or not isinstance(medico, Medico):
            raise ValueError('Paciente ou médico inválido.')
        if not paciente.ativo:
            raise ValueError('Não é possível agendar: o paciente está inativo.')
        if not medico.disponivel:
            raise ValueError(f'{medico.nome_formatado} está indisponível no momento.')
        if not validacoes.validar_data_agendamento(data):
            raise ValueError('Data inválida ou no passado. Use DD/MM/AAAA.')

        consulta = cls(paciente, medico, data, hora, tipo)
        medico.ocupar()
        return consulta

    @classmethod
    def consultas_do_dia(cls, data):
        return [consulta for consulta in cls.consultas if consulta.data == data]

    @classmethod
    def buscar_por_id(cls, id_consulta):
        for consulta in cls.consultas:
            if consulta.id == id_consulta:
                return consulta
        return None

    @classmethod
    def por_status(cls, status):
        return [consulta for consulta in cls.consultas if consulta.status == status]

    @classmethod
    def por_medico(cls, medico):
        return [consulta for consulta in cls.consultas if consulta.medico is medico]

    @classmethod
    def por_paciente(cls, paciente):
        return [consulta for consulta in cls.consultas if consulta.paciente is paciente]

    @staticmethod
    def validar_tipo(tipo):
        return isinstance(tipo, str) and tipo.strip().lower() in ('presencial', 'online')
