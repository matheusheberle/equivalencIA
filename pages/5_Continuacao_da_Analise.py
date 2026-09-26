import streamlit as st

from navegacao import apresentar_etapa, ir_para_etapa


apresentar_etapa(3)
st.info("Próxima etapa ainda não implementada.")

voltar, avancar = st.columns(2)
if voltar.button("Voltar"):
    ir_para_etapa(2)
avancar.button("Avançar", disabled=True)
