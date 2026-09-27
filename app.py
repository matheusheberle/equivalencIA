import streamlit as st

from database import testar_conexao
from navegacao import inicializar_fluxo, ir_para_etapa


st.set_page_config(
    page_title="equivalencIA",
    page_icon="🎓"
)


def pagina_inicio():
    st.title("equivalencIA")

    st.write(
        "Sistema de apoio à análise curricular e ao aproveitamento de disciplinas."
    )

    st.divider()

    inicializar_fluxo()

    if st.session_state.analise_id is not None:
        if st.button("Continuar análise ativa", type="primary"):
            ir_para_etapa(st.session_state.etapa_atual)
    else:
        if st.button("Iniciar análise", type="primary"):
            ir_para_etapa(0)

    st.subheader("Status da conexão")

    if st.button("Verificar conexão"):
        sucesso, mensagem = testar_conexao()

        if sucesso:
            st.success(mensagem)
        else:
            st.error(mensagem)


paginas = [
    st.Page(pagina_inicio, title="Início", icon="🏠", default=True),
    st.Page(
        "pages/2_Iniciar_Analise.py",
        title="Iniciar Análise",
        icon="📝"
    ),
    st.Page(
        "pages/4_Origem_do_Aproveitamento.py",
        title="Origem do Aproveitamento",
        icon="🏫"
    ),
    st.Page(
        "pages/3_Curso_e_Matriz.py",
        title="Curso e Matriz",
        icon="🎓"
    ),
    st.Page(
        "pages/5_Continuacao_da_Analise.py",
        title="Continuação da Análise",
        icon="➡️"
    ),
    st.Page(
        "pages/1_Cursos_e_Matrizes.py",
        title="Cursos e Matrizes",
        icon="📚"
    ),
]

navegacao = st.navigation(paginas)
navegacao.run()