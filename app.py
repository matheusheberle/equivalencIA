import streamlit as st

from database import testar_conexao
from navegacao import inicializar_fluxo, ir_para_etapa


st.set_page_config(
    page_title="equivalencIA",
    page_icon="🎓"
)

st.title("equivalencIA")

st.write(
    "Sistema de apoio à análise de equivalência "
    "e aproveitamento de disciplinas."
)

st.divider()

inicializar_fluxo()
if st.session_state.analise_id is not None:
    if st.button("Continuar análise ativa", type="primary"):
        ir_para_etapa(st.session_state.etapa_atual)
else:
    if st.button("Iniciar análise", type="primary"):
        ir_para_etapa(0)

st.subheader("Status do sistema")

if st.button("Testar conexão com o banco"):
    sucesso, mensagem = testar_conexao()

    if sucesso:
        st.success(mensagem)
    else:
        st.error(mensagem)
