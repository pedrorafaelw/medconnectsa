"""Testes automáticos dos módulos do MedConnect (somente biblioteca padrão).

Execute com:  python -m unittest test -v
"""
import unittest
from datetime import date, timedelta

from modelos.consulta import Consulta
from modelos.financeiro import Financeiro
from modelos.medico import Medico
from modelos.paciente import Paciente
from utils import formatacoes, validacoes

AMANHA = (date.today() + timedelta(days=1)).strftime('%d/%m/%Y')


class BaseTeste(unittest.TestCase):
    def setUp(self):
        Paciente.pacientes.clear()
        Medico.medicos.clear()
        Consulta.consultas.clear()
        Financeiro.registros.clear()
        self.paciente = Paciente('ana souza', '12345678900', '10/03/1990', '41999998888', 'ana@email.com')
        self.medico = Medico('carlos lima', '123456', 'Cardiologia', '4133334444')


class TestUtils(unittest.TestCase):
    def test_validacoes(self):
        self.assertTrue(validacoes.validar_email('a@b.com'))
        self.assertFalse(validacoes.validar_email('a@b'))
        self.assertTrue(validacoes.validar_data('25/05/2026'))
        self.assertFalse(validacoes.validar_data('31/02/2026'))
        self.assertFalse(validacoes.validar_data('abc'))
        self.assertTrue(validacoes.validar_hora('23:59'))
        self.assertFalse(validacoes.validar_hora('24:00'))
        self.assertTrue(validacoes.validar_telefone('41999998888'))
        self.assertFalse(validacoes.validar_telefone('4199999888a'))
        self.assertFalse(validacoes.validar_cpf('1234567890a'))

    def test_formatacoes(self):
        self.assertEqual(formatacoes.formatar_cpf('12345678900'), '123.456.789-00')
        self.assertEqual(formatacoes.formatar_telefone('41999998888'), '(41) 99999-8888')
        self.assertEqual(formatacoes.formatar_data_por_extenso('25/05/2026'), '25 de maio de 2026')
        self.assertEqual(formatacoes.formatar_moeda(350), 'R$350,00')
        self.assertEqual(formatacoes.formatar_moeda(1350.5), 'R$1.350,50')


class TestPaciente(BaseTeste):
    def test_propriedades(self):
        self.assertEqual(self.paciente.nome_formatado, 'Ana Souza')
        self.assertEqual(self.paciente.status, 'Ativo')
        self.assertIsInstance(self.paciente.idade, int)
        self.paciente.alternar_status()
        self.assertEqual(self.paciente.status, 'Inativo')
        self.assertIn('Ana Souza', str(self.paciente))

    def test_particular_e_duplicado(self):
        particular = Paciente.cadastrar_particular('joao', '98765432100', '11988887777')
        self.assertIsNone(particular.email)
        self.assertEqual(particular.idade, 0)
        with self.assertRaises(ValueError):
            Paciente('outro', '12345678900', '01/01/2000', '41999998888')


class TestMedico(BaseTeste):
    def test_medico(self):
        self.assertEqual(self.medico.crm_formatado, 'CRM-SP 123456')
        self.assertEqual(self.medico.status, 'Disponível')
        self.assertEqual(Medico.por_especialidade('cardiologia'), [self.medico])
        self.assertFalse(Medico.validar_crm('123'))
        self.medico.alternar_disponibilidade()
        self.assertEqual(self.medico.status, 'Indisponível')
        self.assertIn('Carlos Lima', str(self.medico))


class TestConsultaEFinanceiro(BaseTeste):
    def test_fluxo_completo(self):
        consulta = Consulta.agendar(self.paciente, self.medico, AMANHA, '14:30', 'online')
        self.assertFalse(self.medico.disponivel)
        self.assertEqual(consulta.status_formatado, 'AGENDADA')
        self.assertTrue(consulta.resumo.startswith(f'#{consulta.id} |'))
        self.assertEqual(Consulta.consultas_do_dia(AMANHA), [consulta])
        self.assertIn('Ana Souza', str(consulta))

        with self.assertRaises(ValueError):
            Consulta.agendar(self.paciente, self.medico, AMANHA, '15:00')

        with self.assertRaises(ValueError):
            Financeiro(consulta, 350)

        consulta.realizar()
        self.assertTrue(self.medico.disponivel)
        registro = Financeiro(consulta, 350)
        self.assertEqual(registro.valor_formatado, 'R$350,00')
        self.assertEqual(Financeiro.total_pendente(), 350)
        self.assertTrue(registro.registrar_pagamento())
        self.assertFalse(registro.registrar_pagamento())
        self.assertEqual(Financeiro.total_recebido(), 350)
        self.assertIn('Total recebido', Financeiro.relatorio_financeiro())

    def test_cancelar_libera_medico(self):
        consulta = Consulta.agendar(self.paciente, self.medico, AMANHA, '09:00')
        consulta.cancelar()
        self.assertTrue(self.medico.disponivel)
        with self.assertRaises(ValueError):
            consulta.realizar()

    def test_validacoes_consulta(self):
        self.assertFalse(Consulta.validar_tipo('domiciliar'))
        with self.assertRaises(ValueError):
            Consulta.agendar(self.paciente, self.medico, '01/01/2000', '09:00')
        self.paciente.alternar_status()
        with self.assertRaises(ValueError):
            Consulta.agendar(self.paciente, self.medico, AMANHA, '09:00')


if __name__ == '__main__':
    unittest.main()
