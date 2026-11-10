# MedConnect System

Sistema de gestão interna da **MedConnect S.A.**: uma aplicação de terminal em Python para gerenciar pacientes, médicos, consultas e o financeiro da clínica.

Projeto Integrador: Desenvolvimento Back-end com Python.

## Requisitos

- Python **3.10 ou superior** (testado no 3.12)
- Nenhuma biblioteca externa: apenas módulos nativos do Python

## Como executar

```bash
python app.py
```

Login padrão:

| Usuário | Senha      |
|---------|------------|
| admin   | admin123   |

Após 3 tentativas incorretas o acesso é bloqueado. Para sair a qualquer momento, use a opção **6 - Sair** do menu principal (ou `Ctrl+C`).

> Os dados ficam apenas em memória e são perdidos ao encerrar o programa.

## Como rodar os testes

```bash
python -m unittest test -v
```

## Estrutura

```
medconnect/
├── modelos/
│   ├── __init__.py
│   ├── paciente.py
│   ├── medico.py
│   ├── consulta.py
│   └── financeiro.py
├── utils/
│   ├── __init__.py
│   ├── validacoes.py
│   ├── formatacoes.py
│   └── entradas.py
├── app.py
├── test.py
└── README.md
```

## Módulos

### `modelos/paciente.py` (classe `Paciente`)
- Atributos: `nome`, `cpf`, `data_nascimento` (DD/MM/AAAA), `telefone`, `email`, `_ativo` e a lista de classe `pacientes`.
- Propriedades: `nome_formatado`, `status` ('Ativo'/'Inativo'), `idade`.
- `cadastrar_particular(nome, cpf, telefone)`: cadastro sem email, usando a data atual.
- `validar_cpf(cpf)`: verifica se o CPF tem 11 dígitos numéricos.
- `alternar_status()`, `atualizar(...)`, `excluir()`, `buscar_por_cpf(cpf)`, `listar_ativos()`.
- Não permite CPF duplicado.

### `modelos/medico.py` (classe `Medico`)
- Atributos: `nome`, `crm`, `especialidade`, `telefone`, `_disponivel` e a lista de classe `medicos`.
- Propriedades: `status` ('Disponível'/'Indisponível'), `crm_formatado` ('CRM-SP 123456').
- `por_especialidade(especialidade)`: retorna os médicos da especialidade.
- `validar_crm(crm)`: verifica se o CRM tem de 4 a 6 dígitos.
- `alternar_disponibilidade()`, `atualizar(...)`, `excluir()`, `buscar_por_crm(crm)`.

### `modelos/consulta.py` (classe `Consulta`)
- Atributos: `paciente`, `medico`, `data`, `hora`, `tipo` (presencial/online), `_status` e a lista de classe `consultas`. Cada consulta recebe um número (`id`) automático.
- Propriedades: `status_formatado` (maiúsculo), `resumo` (uma linha).
- `agendar(paciente, medico, data, hora, tipo='presencial')`: só agenda se o paciente estiver ativo e o médico disponível, e então marca o médico como **indisponível**.
- `realizar()` e `cancelar()`: mudam o status e **liberam o médico**.
- `remarcar(data, hora)`, `consultas_do_dia(data)`, `validar_tipo(tipo)`.

### `modelos/financeiro.py` (classe `Financeiro`)
- Atributos: `consulta`, `valor`, `_pago` e a lista de classe `registros`.
- Propriedades: `status_pagamento` ('Pago'/'Pendente'), `valor_formatado` ('R$350,00').
- `registrar_pagamento()`, `alterar_valor(valor)`, `excluir()` (somente pendentes).
- `total_recebido()`, `total_pendente()`, `relatorio_financeiro()`.
- Só aceita cobrança de consultas **realizadas**, com no máximo um lançamento por consulta.

### `utils/validacoes.py`
Validação de email, data DD/MM/AAAA (incluindo datas inexistentes, como 31/02), hora HH:MM, telefone com DDD e CPF.

### `utils/formatacoes.py`
- CPF: `'12345678900'` → `'123.456.789-00'`
- Telefone: `'41999998888'` → `'(41) 99999-8888'`
- Data por extenso: `'25/05/2026'` → `'25 de maio de 2026'`
- Moeda: `350` → `'R$350,00'`

### `utils/entradas.py`
Funções de interface do terminal (limpar tela, cabeçalho, leitura validada de dados). Cada leitura repete a pergunta até receber um valor válido.

### `app.py`
Login e menu principal com navegação entre os módulos. Cada submenu tem CRUD completo:

1. **Gestão de Pacientes**: cadastrar, cadastro particular, listar, listar ativos, buscar por CPF, editar, ativar/desativar, excluir
2. **Gestão de Médicos**: cadastrar, listar, listar por especialidade, buscar por CRM, editar, alterar disponibilidade, excluir
3. **Gestão de Consultas**: agendar, listar, consultas do dia, buscar, remarcar, realizar (gera a cobrança), cancelar
4. **Financeiro**: lançar cobrança, listar, pendentes, registrar pagamento, alterar valor, excluir, relatório
5. **Relatórios**: resumo geral, consultas por status, por médico, histórico do paciente, relatório financeiro

## Fluxo de uma consulta

```
agendar  ──►  médico fica INDISPONÍVEL
   │
   ├── realizar  ──►  médico DISPONÍVEL + cobrança lançada como Pendente
   │                     └── registrar pagamento ──► Pago
   └── cancelar  ──►  médico DISPONÍVEL
```
