import streamlit as st

from database import testar_conexao


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

st.subheader("Status do sistema")

if st.button("Testar conexão com o banco"):
    sucesso, mensagem = testar_conexao()

    if sucesso:
        st.success(mensagem)
    else:
        st.error(mensagem)