"""Camada de persistência do MedConnect (SQLite)."""
from banco.conexao import CAMINHO_PADRAO, conectar, fechar


def inicializar(caminho=CAMINHO_PADRAO):
    """Conecta ao banco, cria as tabelas se preciso e carrega os dados nos modelos."""
    conectar(caminho)

    # Import aqui dentro para evitar import circular (os modelos importam o banco).
    from modelos.consulta import Consulta
    from modelos.financeiro import Financeiro
    from modelos.medico import Medico
    from modelos.paciente import Paciente

    # A ordem importa: consultas dependem de pacientes/médicos, e o financeiro de consultas.
    Paciente.carregar()
    Medico.carregar()
    Consulta.carregar()
    Financeiro.carregar()


__all__ = ['CAMINHO_PADRAO', 'conectar', 'fechar', 'inicializar']
