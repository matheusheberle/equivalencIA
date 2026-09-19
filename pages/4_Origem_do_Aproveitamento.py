import streamlit as st

from navegacao import apresentar_etapa, ir_para_etapa


apresentar_etapa(1)
st.info("Etapa de Origem do Aproveitamento ainda não implementada.")
st.write("Os campos atuais de Situação e Procedência continuam em Nova Análise.")

voltar, avancar = st.columns(2)
if voltar.button("Voltar"):
    ir_para_etapa(0)
if avancar.button("Avançar", type="primary"):
    ir_para_etapa(2)
