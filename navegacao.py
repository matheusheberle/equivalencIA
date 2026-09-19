import streamlit as st

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
    st.session_state.analise_id = analise_id
    st.session_state.etapa_atual = 0


def ir_para_etapa(etapa):
    st.session_state.etapa_atual = etapa
    st.switch_page(ETAPAS[etapa][1])


def apresentar_etapa(etapa):
    inicializar_fluxo()
    st.session_state.etapa_atual = etapa
    dados = None
    if st.session_state.analise_id is not None:
        dados = obter_analise(st.session_state.analise_id)
        if dados is None:
            ativar_analise(None)
            st.warning("A análise ativa não foi encontrada. Crie ou selecione outra análise.")

    if dados:
        st.session_state.aluno_id = dados[9]
        st.write(f"Análise ativa: {dados[1]} — nº {dados[0]}")
    st.caption(f"Etapa {etapa + 1} de {len(ETAPAS)}")
    st.title(ETAPAS[etapa][0])
    st.caption(" → ".join(nome for nome, _ in ETAPAS))

    if etapa > 0 and dados is None:
        st.warning("Crie ou selecione uma análise para continuar.")
        if st.button("Ir para Nova Análise"):
            ir_para_etapa(0)
        st.stop()
    return dados
