import streamlit as st
import psycopg

from database import obter_analise


ETAPAS = (
    ("Nova Análise", "pages/2_Nova_Analise.py"),
    ("Origem do Aproveitamento", "pages/4_Origem_do_Aproveitamento.py"),
    ("Curso e Matriz", "pages/3_Selecionar_Curso_e_Matriz.py"),
    ("Próxima etapa", "pages/5_Proxima_Etapa.py"),
)


def inicializar_fluxo():
    st.session_state.setdefault("aluno_id", None)
    st.session_state.setdefault("analise_id", None)
    st.session_state.setdefault("etapa_atual", 0)


def ativar_analise(analise_id):
    st.session_state.pop("confirmacao_salvamento", None)
    st.session_state.analise_id = analise_id
    st.session_state.etapa_atual = 0


def ir_para_etapa(etapa):
    st.session_state.etapa_atual = etapa
    st.switch_page(ETAPAS[etapa][1])


def confirmar_salvamento(mensagem, etapa):
    st.session_state.confirmacao_salvamento = (
        st.session_state.analise_id, etapa, mensagem
    )


def apresentar_etapa(etapa):
    inicializar_fluxo()
    # Consumida uma única vez, inclusive se a leitura seguinte falhar.
    confirmacao = st.session_state.pop("confirmacao_salvamento", None)
    st.session_state.etapa_atual = etapa
    dados = None
    if st.session_state.analise_id is not None:
        try:
            dados = obter_analise(st.session_state.analise_id)
        except psycopg.Error:
            # Widgets não renderizados por st.stop seriam removidos da sessão.
            for chave in list(st.session_state):
                if chave.startswith(("analise_", "curso_", "matriz_", "situacao_origem_", "procedencia_")):
                    st.session_state[chave] = st.session_state[chave]
            st.error("Não foi possível carregar a análise ativa. Tente novamente.")
            if st.button("Tentar novamente"):
                st.rerun()
            st.stop()
        if dados is None:
            ativar_analise(None)
            st.warning("A análise ativa não foi encontrada. Crie ou selecione outra análise.")

    if dados:
        st.session_state.aluno_id = dados[9]
        st.write(f"Análise ativa: {dados[1]} — nº {dados[0]}")
    st.caption(f"Etapa {etapa + 1} de {len(ETAPAS)}")
    st.title(ETAPAS[etapa][0])
    st.caption(" → ".join(nome for nome, _ in ETAPAS))
    if dados and confirmacao and confirmacao[:2] == (dados[0], etapa):
        st.success(confirmacao[2])

    if etapa > 0 and dados is None:
        st.warning("Crie ou selecione uma análise para continuar.")
        if st.button("Ir para Nova Análise"):
            ir_para_etapa(0)
        st.stop()
    return dados
