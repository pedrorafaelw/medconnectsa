"""Comandos SQL de cada entidade. Os modelos usam estas funções em vez de escrever SQL."""
from banco.conexao import consultar, executar

# ======================================================================
# Pacientes
# ======================================================================


def listar_pacientes():
    return consultar('SELECT * FROM pacientes ORDER BY rowid')


def inserir_paciente(cpf, nome, data_nascimento, telefone, email, ativo):
    executar(
        'INSERT INTO pacientes (cpf, nome, data_nascimento, telefone, email, ativo) '
        'VALUES (?, ?, ?, ?, ?, ?)',
        (cpf, nome, data_nascimento, telefone, email, int(ativo)),
    )


def atualizar_paciente(cpf, nome, telefone, email):
    executar(
        'UPDATE pacientes SET nome = ?, telefone = ?, email = ? WHERE cpf = ?',
        (nome, telefone, email, cpf),
    )


def definir_ativo_paciente(cpf, ativo):
    executar('UPDATE pacientes SET ativo = ? WHERE cpf = ?', (int(ativo), cpf))


def paciente_tem_consultas(cpf):
    return bool(consultar('SELECT 1 FROM consultas WHERE paciente_cpf = ? LIMIT 1', (cpf,)))


def excluir_paciente(cpf):
    executar('DELETE FROM pacientes WHERE cpf = ?', (cpf,))


# ======================================================================
# Médicos
# ======================================================================


def listar_medicos():
    return consultar('SELECT * FROM medicos ORDER BY rowid')


def inserir_medico(crm, nome, especialidade, telefone, disponivel):
    executar(
        'INSERT INTO medicos (crm, nome, especialidade, telefone, disponivel) VALUES (?, ?, ?, ?, ?)',
        (crm, nome, especialidade, telefone, int(disponivel)),
    )


def atualizar_medico(crm, nome, especialidade, telefone):
    executar(
        'UPDATE medicos SET nome = ?, especialidade = ?, telefone = ? WHERE crm = ?',
        (nome, especialidade, telefone, crm),
    )


def definir_disponibilidade_medico(crm, disponivel):
    executar('UPDATE medicos SET disponivel = ? WHERE crm = ?', (int(disponivel), crm))


def medico_tem_consultas(crm):
    return bool(consultar('SELECT 1 FROM consultas WHERE medico_crm = ? LIMIT 1', (crm,)))


def excluir_medico(crm):
    executar('DELETE FROM medicos WHERE crm = ?', (crm,))


# ======================================================================
# Consultas
# ======================================================================


def listar_consultas():
    return consultar('SELECT * FROM consultas ORDER BY id')


def inserir_consulta(paciente_cpf, medico_crm, data, hora, tipo, status):
    """Insere a consulta e retorna o número (id) gerado pelo banco."""
    cursor = executar(
        'INSERT INTO consultas (paciente_cpf, medico_crm, data, hora, tipo, status) '
        'VALUES (?, ?, ?, ?, ?, ?)',
        (paciente_cpf, medico_crm, data, hora, tipo, status),
    )
    return cursor.lastrowid


def definir_status_consulta(id_consulta, status):
    executar('UPDATE consultas SET status = ? WHERE id = ?', (status, id_consulta))


def remarcar_consulta(id_consulta, data, hora):
    executar('UPDATE consultas SET data = ?, hora = ? WHERE id = ?', (data, hora, id_consulta))


# ======================================================================
# Financeiro
# ======================================================================


def listar_lancamentos():
    return consultar('SELECT * FROM financeiro ORDER BY rowid')


def inserir_lancamento(consulta_id, valor, pago):
    executar(
        'INSERT INTO financeiro (consulta_id, valor, pago) VALUES (?, ?, ?)',
        (consulta_id, valor, int(pago)),
    )


def definir_pago_lancamento(consulta_id, pago):
    executar('UPDATE financeiro SET pago = ? WHERE consulta_id = ?', (int(pago), consulta_id))


def atualizar_valor_lancamento(consulta_id, valor):
    executar('UPDATE financeiro SET valor = ? WHERE consulta_id = ?', (valor, consulta_id))


def excluir_lancamento(consulta_id):
    executar('DELETE FROM financeiro WHERE consulta_id = ?', (consulta_id,))
