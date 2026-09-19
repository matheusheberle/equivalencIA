"""Testes da interface com persistência simulada, sem acessar PostgreSQL."""

from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class FluxoTest(unittest.TestCase):
    def setUp(self):
        self.analises = {
            1: (1, "Ana", "123", "2026/2", "Regular", "Externa", None, 10, 100),
            2: (2, "Bruno", "456", "2026/1", "Regular", "Interna", None, 20, 200),
        }
        self.cursos = [(10, "ADS", "Sistemas"), (20, "ENG", "Engenharia")]
        self.matrizes = {10: [(100, 10, "2024"), (101, 10, "2025")], 20: [(200, 20, "2026")]}
        funcoes = {
            "obter_analise": lambda ident: self.analises.get(ident),
            "listar_analises": lambda: [a[:7] for a in self.analises.values()],
            "criar_analise": self.criar,
            "atualizar_analise": self.atualizar,
            "listar_cursos": lambda: self.cursos,
            "listar_matrizes_por_curso": lambda ident: self.matrizes[ident],
            "salvar_curso_e_matriz": self.salvar_matriz,
        }
        for nome, funcao in funcoes.items():
            mock = patch(f"database.{nome}", side_effect=funcao)
            mock.start()
            self.addCleanup(mock.stop)
        mock = patch("navegacao.obter_analise", side_effect=funcoes["obter_analise"])
        mock.start()
        self.addCleanup(mock.stop)
        self.app = AppTest.from_file(str(ROOT / "app.py")).run()

    def criar(self, *valores):
        ident = max(self.analises) + 1
        self.analises[ident] = (ident, *valores, None, None, None)
        return ident

    def atualizar(self, ident, *valores):
        self.analises[ident] = (ident, *valores, *self.analises[ident][6:])

    def salvar_matriz(self, ident, curso, matriz):
        self.analises[ident] = (*self.analises[ident][:7], curso, matriz)

    def clicar(self, label):
        next(b for b in self.app.button if b.label == label).click().run()
        self.assertFalse(self.app.exception)
        # AppTest executa st.switch_page, mas não retém seu destino para
        # a próxima interação; sincronize com a página realmente renderizada.
        from navegacao import ETAPAS
        for titulo, pagina in ETAPAS:
            if self.app.title and self.app.title[0].value == titulo:
                self.app.switch_page(pagina)
                break

    def etapa(self, numero, analise_id):
        self.assertEqual(self.app.session_state["etapa_atual"], numero)
        self.assertEqual(self.app.session_state["analise_id"], analise_id)
        self.assertEqual(self.app.caption[0].value, f"Etapa {numero + 1} de 4")

    def ativar(self, ident=1):
        self.clicar("Iniciar análise")
        self.app.selectbox[0].select(self.analises[ident][:7])
        self.clicar("Ativar análise selecionada")

    def test_criar_avancar_voltar_e_retomar(self):
        self.clicar("Iniciar análise")
        self.clicar("Avançar")
        self.assertTrue(self.app.error)
        self.assertEqual(len(self.analises), 2)
        self.app.text_input[0].input("Carla")
        self.app.text_input[4].input("Outra instituição")
        self.clicar("Avançar")
        self.etapa(1, 3)
        self.clicar("Avançar")
        self.etapa(2, 3)
        self.clicar("Avançar")
        self.assertTrue(self.app.error)
        self.app.selectbox[1].select(self.matrizes[10][1])
        self.clicar("Avançar")
        self.etapa(3, 3)
        self.assertEqual(self.analises[3][7:], (10, 101))
        self.assertTrue(next(b for b in self.app.button if b.label == "Avançar").disabled)
        self.clicar("Voltar")
        self.assertEqual(self.app.selectbox[1].value[0], 101)
        self.app.switch_page("app.py").run()
        self.clicar("Continuar análise ativa")
        self.etapa(2, 3)
        self.clicar("Voltar")
        self.clicar("Voltar")
        self.etapa(0, 3)
        self.assertEqual(self.app.text_input[0].value, "Carla")
        self.assertEqual(self.app.text_input[4].value, "Outra instituição")
        self.clicar("Avançar")
        self.assertEqual(len(self.analises), 3)

    def test_trocar_analise_e_editar_sem_misturar_dados(self):
        self.ativar()
        self.app.text_input[0].input("Ana editada")
        self.clicar("Salvar alterações")
        self.assertEqual(self.analises[1][1], "Ana editada")
        self.app.selectbox[0].select(self.analises[2][:7])
        self.clicar("Ativar análise selecionada")
        self.etapa(0, 2)
        self.assertEqual(self.app.text_input[0].value, "Bruno")
        self.clicar("Avançar")
        self.clicar("Avançar")
        self.assertEqual(self.app.selectbox[0].value[0], 20)
        self.assertEqual(self.app.selectbox[1].value[0], 200)
        self.app.selectbox[0].select(self.cursos[0]).run()
        self.assertIsNone(self.app.selectbox[1].value)
        self.app.selectbox[1].select(self.matrizes[10][0])
        self.clicar("Avançar")
        self.assertEqual(self.analises[2][7:], (10, 100))
        self.assertEqual(self.analises[1][7:], (10, 100))
        self.clicar("Voltar")
        self.clicar("Voltar")
        self.clicar("Voltar")
        self.clicar("Cadastrar outra análise")
        self.assertIsNone(self.app.session_state["analise_id"])
        self.assertEqual(self.app.text_input[0].value, "")

    def test_acesso_direto_sem_analise_e_analise_removida(self):
        for pagina in ("3_Selecionar_Curso_e_Matriz", "4_Origem_do_Aproveitamento", "5_Proxima_Etapa"):
            self.app.switch_page(f"pages/{pagina}.py").run()
            self.assertFalse(self.app.exception)
            self.assertTrue(self.app.warning)
            self.clicar("Ir para Nova Análise")
        self.app.session_state["analise_id"] = 999
        self.app.switch_page("pages/3_Selecionar_Curso_e_Matriz.py").run()
        self.assertIsNone(self.app.session_state["analise_id"])
        self.assertFalse(self.app.exception)

    def test_sem_cursos_ou_matrizes_permite_voltar(self):
        self.ativar()
        self.clicar("Avançar")
        self.cursos = []
        self.clicar("Avançar")
        self.assertTrue(self.app.warning)
        self.assertTrue(next(b for b in self.app.button if b.label == "Avançar").disabled)
        self.clicar("Voltar")
        self.cursos = [(10, "ADS", "Sistemas")]
        self.matrizes[10] = []
        self.clicar("Avançar")
        self.assertTrue(self.app.warning)
        self.assertTrue(next(b for b in self.app.button if b.label == "Avançar").disabled)
        self.clicar("Voltar")
        self.etapa(1, 1)


if __name__ == "__main__":
    unittest.main()
