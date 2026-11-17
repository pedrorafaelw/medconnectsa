"""Conexão com o banco SQLite e criação das tabelas."""
import sqlite3
from pathlib import Path

CAMINHO_PADRAO = Path(__file__).resolve().parent.parent / 'medconnect.db'

ESQUEMA = """
CREATE TABLE IF NOT EXISTS pacientes (
    cpf             TEXT PRIMARY KEY,
    nome            TEXT NOT NULL,
    data_nascimento TEXT NOT NULL,
    telefone        TEXT NOT NULL,
    email           TEXT,
    ativo           INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
);

CREATE TABLE IF NOT EXISTS medicos (
    crm           TEXT PRIMARY KEY,
    nome          TEXT NOT NULL,
    especialidade TEXT NOT NULL,
    telefone      TEXT NOT NULL,
    disponivel    INTEGER NOT NULL DEFAULT 1 CHECK (disponivel IN (0, 1))
);

CREATE TABLE IF NOT EXISTS consultas (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_cpf TEXT NOT NULL REFERENCES pacientes (cpf),
    medico_crm   TEXT NOT NULL REFERENCES medicos (crm),
    data         TEXT NOT NULL,
    hora         TEXT NOT NULL,
    tipo         TEXT NOT NULL CHECK (tipo IN ('presencial', 'online')),
    status       TEXT NOT NULL DEFAULT 'agendada'
                 CHECK (status IN ('agendada', 'realizada', 'cancelada'))
);

CREATE TABLE IF NOT EXISTS financeiro (
    consulta_id INTEGER PRIMARY KEY REFERENCES consultas (id),
    valor       REAL NOT NULL CHECK (valor > 0),
    pago        INTEGER NOT NULL DEFAULT 0 CHECK (pago IN (0, 1))
);
"""

_conexao = None


def conectar(caminho=CAMINHO_PADRAO):
    """Abre (ou cria) o banco em `caminho` e garante que as tabelas existam.

    Use ':memory:' para um banco temporário, apagado ao fechar (útil em testes).
    """
    global _conexao
    fechar()
    _conexao = sqlite3.connect(caminho)
    _conexao.row_factory = sqlite3.Row
    _conexao.execute('PRAGMA foreign_keys = ON')
    _conexao.executescript(ESQUEMA)
    return _conexao


def obter_conexao():
    if _conexao is None:
        raise RuntimeError('Banco de dados não inicializado. Chame banco.inicializar() antes.')
    return _conexao


def executar(sql, parametros=()):
    """Executa um comando de escrita (INSERT/UPDATE/DELETE) e confirma a transação."""
    conexao = obter_conexao()
    with conexao:  # commit em caso de sucesso, rollback em caso de erro
        return conexao.execute(sql, parametros)


def consultar(sql, parametros=()):
    """Executa um SELECT e retorna todas as linhas."""
    return obter_conexao().execute(sql, parametros).fetchall()


def fechar():
    global _conexao
    if _conexao is not None:
        _conexao.close()
        _conexao = None
