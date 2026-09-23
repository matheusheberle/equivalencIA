"""Testes da interface com persistência simulada, sem acessar PostgreSQL."""

from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class FluxoTest(unittest.TestCase):
    def setUp(self):
        self.alunos = {1: (1, "Ana", "123"), 2: (2, "Bruno", "456")}
        self.analises = {
            1: (1, "Ana", "123", "2026/2", "Concluído", "Externa", None, 10, 100, 1, "Engenharia"),
            2: (2, "Bruno", "456", "2026/1", "Incompleto", "Interna", None, 20, 200, 2, "Sistemas"),
        }
        self.cursos = [(10, "ADS", "Sistemas"), (20, "ENG", "Engenharia")]
        self.matrizes = {10: [(100, 10, "2024"), (101, 10, "2025")], 20: [(200, 20, "2026")]}
        funcoes = {
            "obter_analise": lambda ident: self.analises.get(ident),
            "listar_analises": lambda: list(self.analises.values()),
            "listar_alunos": lambda: self.fail("A tela não deve carregar todos os alunos"),
            "obter_aluno": lambda ident: self.alunos.get(ident),
            "buscar_alunos_por_nome": lambda termo: [
                aluno for aluno in self.alunos.values() if termo.lower() in aluno[1].lower()
            ],
            "criar_aluno": self.criar_aluno,
            "criar_analise": self.criar,
            "atualizar_analise": self.atualizar,
            "salvar_origem_aproveitamento": self.salvar_origem,
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

    def criar_aluno(self, nome, ra):
        ident = max(self.alunos) + 1
        self.alunos[ident] = (ident, nome.strip(), (ra or "").strip() or None)
        return ident

    def criar(self, aluno_id, *valores):
        ident = max(self.analises) + 1
        self.analises[ident] = (ident, *self.alunos[aluno_id][1:], *valores, None, None, None, None, None, aluno_id, None)
        return ident

    def atualizar(self, ident, *valores):
        self.analises[ident] = (*self.analises[ident][:3], *valores, *self.analises[ident][4:])

    def salvar_origem(self, ident, curso_origem, situacao, procedencia):
        dados = list(self.analises[ident])
        dados[4:6] = (situacao, procedencia)
        dados[10] = curso_origem
        self.analises[ident] = tuple(dados)

    def salvar_matriz(self, ident, curso, matriz):
        self.analises[ident] = (*self.analises[ident][:7], curso, matriz, *self.analises[ident][9:])

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
        self.app.selectbox[0].select(self.analises[ident])
        self.clicar("Ativar análise selecionada")

    def test_criar_avancar_voltar_e_retomar(self):
        self.clicar("Iniciar análise")
        self.clicar("Avançar")
        self.assertTrue(self.app.error)
        self.assertEqual(len(self.analises), 2)
        self.app.text_input[0].input("Carla")
        self.clicar("Salvar aluno")
        self.assertEqual(len(self.analises), 2)
        self.assertEqual(self.alunos[3], (3, "Carla", None))
        self.clicar("Avançar")
        self.etapa(1, 3)
        self.app.text_input(key="curso_origem_3").input("Engenharia")
        self.app.selectbox(key="situacao_origem_3").select("Incompleto")
        self.app.text_input(key="procedencia_3").input("Outra instituição")
        self.clicar("Avançar")
        self.etapa(2, 3)
        self.clicar("Avançar")
        self.assertTrue(self.app.error)
        self.app.selectbox[1].select(self.matrizes[10][1])
        self.clicar("Avançar")
        self.etapa(3, 3)
        self.assertEqual(self.analises[3][7:], (10, 101, 3, "Engenharia"))
        self.assertTrue(next(b for b in self.app.button if b.label == "Avançar").disabled)
        self.clicar("Voltar")
        self.assertEqual(self.app.selectbox[1].value[0], 101)
        self.app.switch_page("app.py").run()
        self.clicar("Continuar análise ativa")
        self.etapa(2, 3)
        self.clicar("Voltar")
        self.clicar("Voltar")
        self.etapa(0, 3)
        self.assertEqual(self.analises[3][5], "Outra instituição")
        self.assertEqual(self.analises[3][10], "Engenharia")
        self.assertTrue(any("Carla" in m.value for m in self.app.markdown))
        self.clicar("Avançar")
        self.assertEqual(len(self.analises), 3)

    def test_trocar_analise_e_editar_sem_misturar_dados(self):
        self.ativar()
        self.app.text_input[0].input("2027/1")
        self.clicar("Salvar alterações")
        self.assertEqual(self.analises[1][3], "2027/1")
        self.assertEqual(self.alunos[1], (1, "Ana", "123"))
        self.app.selectbox[0].select(self.analises[2])
        self.clicar("Ativar análise selecionada")
        self.etapa(0, 2)
        self.assertEqual(self.app.text_input[0].value, "2026/1")
        self.assertTrue(any("Bruno" in m.value for m in self.app.markdown))
        self.clicar("Avançar")
        self.clicar("Avançar")
        self.assertEqual(self.app.selectbox[0].value[0], 20)
        self.assertEqual(self.app.selectbox[1].value[0], 200)
        self.app.selectbox[0].select(self.cursos[0]).run()
        self.assertIsNone(self.app.selectbox[1].value)
        self.app.selectbox[1].select(self.matrizes[10][0])
        self.clicar("Avançar")
        self.assertEqual(self.analises[2][7:], (10, 100, 2, "Sistemas"))
        self.assertEqual(self.analises[1][7:], (10, 100, 1, "Engenharia"))
        self.clicar("Voltar")
        self.clicar("Voltar")
        self.clicar("Voltar")
        self.clicar("Cadastrar outra análise")
        self.assertIsNone(self.app.session_state["analise_id"])
        self.assertEqual(self.app.text_input[0].value, "")

    def test_cadastro_com_ra_nome_obrigatorio_e_duas_analises(self):
        self.clicar("Iniciar análise")
        self.app.text_input[0].input("   ")
        self.clicar("Salvar aluno")
        self.assertTrue(self.app.error)
        self.assertEqual(len(self.alunos), 2)
        self.app.text_input[0].input("Daniela")
        self.app.text_input[1].input("789")
        self.clicar("Salvar aluno")
        self.assertEqual(self.alunos[3], (3, "Daniela", "789"))
        self.assertEqual(len(self.analises), 2)
        self.clicar("Salvar análise")
        self.etapa(0, 3)
        self.clicar("Cadastrar outra análise")
        self.assertEqual(self.app.session_state["aluno_id"], 3)
        self.clicar("Avançar")
        self.etapa(1, 4)
        self.assertEqual(self.analises[3][9], self.analises[4][9])
        self.assertEqual(len(self.alunos), 3)

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

    def test_busca_seleciona_homonimo_por_id_e_preserva_contexto(self):
        self.alunos[3] = (3, "Matheus Freitas", None)
        self.alunos[4] = (4, "Matheus Freitas", "987")
        self.clicar("Iniciar análise")
        self.assertFalse([b for b in self.app.button if b.label == "Selecionar"])
        self.app.text_input(key="busca_aluno").input("mAtHeUs").run()
        self.assertEqual(len([b for b in self.app.button if b.label == "Selecionar"]), 2)
        self.assertTrue(any(m.value == "RA não informado" for m in self.app.markdown))
        self.assertTrue(any(m.value == "RA: 987" for m in self.app.markdown))
        self.app.button(key="selecionar_aluno_4").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.session_state["aluno_id"], 4)
        self.app.text_input(key="busca_aluno").input("Inexistente").run()
        self.assertTrue(any(i.value == "Nenhum aluno encontrado." for i in self.app.info))
        self.assertFalse([b for b in self.app.button if b.label == "Selecionar"])
        self.assertEqual(self.app.session_state["aluno_id"], 4)
        self.app.switch_page("app.py").run()
        self.clicar("Iniciar análise")
        self.assertEqual(self.app.session_state["aluno_id"], 4)
        self.clicar("Avançar")
        self.etapa(1, 3)
        self.assertEqual(self.analises[3][9], 4)
        self.clicar("Voltar")
        self.assertEqual(self.app.session_state["aluno_id"], 4)
        self.clicar("Cadastrar outra análise")
        self.clicar("Limpar seleção")
        self.assertIsNone(self.app.session_state["aluno_id"])
        self.clicar("Avançar")
        self.assertTrue(self.app.error)

    def test_busca_sem_resultado_e_aluno_removido(self):
        self.clicar("Iniciar análise")
        self.app.text_input(key="busca_aluno").input("Ninguém").run()
        self.assertTrue(any(i.value == "Nenhum aluno encontrado." for i in self.app.info))
        self.app.text_input(key="busca_aluno").input("Ana").run()
        self.app.button(key="selecionar_aluno_1").click().run()
        del self.alunos[1]
        self.app.run()
        self.assertFalse(self.app.exception)
        self.assertTrue(self.app.warning)
        self.assertIsNone(self.app.session_state["aluno_id"])

    def test_selecionar_aluno_existente_cria_apenas_analises(self):
        alunos_antes = self.alunos.copy()
        with patch("database.criar_aluno") as criar_aluno:
            self.clicar("Iniciar análise")
            self.app.text_input(key="busca_aluno").input("Bruno").run()
            self.app.button(key="selecionar_aluno_2").click().run()
            self.assertEqual(self.app.session_state["aluno_id"], 2)
            self.clicar("Salvar análise")
            self.etapa(0, 3)
            self.assertEqual(self.analises[3][9], 2)
            self.assertEqual(self.alunos, alunos_antes)
            tabela = self.app.dataframe[0].value
            linha = tabela[tabela["ID da análise"] == 3].iloc[0]
            self.assertEqual(linha["ID do aluno"], 2)
            self.clicar("Cadastrar outra análise")
            self.clicar("Avançar")
            self.etapa(1, 4)
            self.assertEqual(self.analises[4][9], 2)
            self.assertEqual(self.alunos, alunos_antes)
            criar_aluno.assert_not_called()

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
