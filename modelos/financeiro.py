"""Módulo Financeiro: cobranças e pagamentos das consultas."""
import math

from banco import repositorios
from modelos.consulta import Consulta
from utils import formatacoes


class Financeiro:
    """Representa a cobrança de uma consulta realizada."""

    registros = []

    def __init__(self, consulta, valor, pago=False):
        if not isinstance(consulta, Consulta):
            raise ValueError('Consulta inválida.')
        if consulta.status != 'realizada':
            raise ValueError('Só é possível lançar cobrança de uma consulta realizada.')
        if Financeiro.buscar_por_consulta(consulta):
            raise ValueError('Já existe um lançamento para esta consulta.')

        self.consulta = consulta
        self.valor = Financeiro._validar_valor(valor)
        self._pago = bool(pago)
        repositorios.inserir_lancamento(consulta.id, self.valor, self._pago)
        Financeiro.registros.append(self)

    @classmethod
    def _de_registro(cls, linha, consultas):
        """Monta um lançamento a partir de uma linha do banco, ligando-o à consulta já carregada."""
        registro = cls.__new__(cls)
        registro.consulta = consultas[linha['consulta_id']]
        registro.valor = linha['valor']
        registro._pago = bool(linha['pago'])
        return registro

    @classmethod
    def carregar(cls):
        """Substitui a lista em memória pelos lançamentos do banco. Carregue as consultas antes."""
        consultas = {consulta.id: consulta for consulta in Consulta.consultas}
        cls.registros[:] = [
            cls._de_registro(linha, consultas) for linha in repositorios.listar_lancamentos()
        ]

    def __str__(self):
        return (
            f'{self.consulta.resumo}\n'
            f'   Valor: {self.valor_formatado} | Pagamento: {self.status_pagamento}'
        )

    @property
    def pago(self):
        return self._pago

    @property
    def status_pagamento(self):
        return 'Pago' if self._pago else 'Pendente'

    @property
    def valor_formatado(self):
        return formatacoes.formatar_moeda(self.valor)

    def registrar_pagamento(self):
        """Marca o lançamento como pago. Retorna False se ele já estava pago."""
        if self._pago:
            return False
        repositorios.definir_pago_lancamento(self.consulta.id, True)
        self._pago = True
        return True

    def alterar_valor(self, novo_valor):
        if self._pago:
            raise ValueError('Não é possível alterar o valor de um lançamento já pago.')
        valor = Financeiro._validar_valor(novo_valor)
        repositorios.atualizar_valor_lancamento(self.consulta.id, valor)
        self.valor = valor

    def excluir(self):
        if self._pago:
            raise ValueError('Não é possível excluir um lançamento já pago.')
        repositorios.excluir_lancamento(self.consulta.id)
        Financeiro.registros.remove(self)

    @staticmethod
    def _validar_valor(valor):
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            raise ValueError('Valor inválido.') from None
        if not math.isfinite(valor) or valor <= 0:
            raise ValueError('O valor deve ser maior que zero.')
        return round(valor, 2)

    @classmethod
    def buscar_por_consulta(cls, consulta):
        for registro in cls.registros:
            if registro.consulta is consulta:
                return registro
        return None

    @classmethod
    def listar_pendentes(cls):
        return [registro for registro in cls.registros if not registro.pago]

    @classmethod
    def total_recebido(cls):
        return round(sum(r.valor for r in cls.registros if r.pago), 2)

    @classmethod
    def total_pendente(cls):
        return round(sum(r.valor for r in cls.registros if not r.pago), 2)

    @classmethod
    def relatorio_financeiro(cls):
        linhas = [
            f'Lançamentos:     {len(cls.registros)}',
            f'Total recebido:  {formatacoes.formatar_moeda(cls.total_recebido())}',
            f'Total pendente:  {formatacoes.formatar_moeda(cls.total_pendente())}',
            f'Total geral:     {formatacoes.formatar_moeda(cls.total_recebido() + cls.total_pendente())}',
            '-' * 30,
        ]
        if cls.registros:
            linhas.extend(str(registro) for registro in cls.registros)
        else:
            linhas.append('Nenhum lançamento registrado.')
        return '\n'.join(linhas)
