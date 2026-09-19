import streamlit as st

from database import atualizar_analise, criar_analise, listar_analises
from navegacao import apresentar_etapa, ativar_analise, ir_para_etapa


dados = apresentar_etapa(0)

if dados and st.button("Cadastrar outra análise"):
    ativar_analise(None)
    st.rerun()

st.subheader("Editar análise ativa" if dados else "Cadastrar nova análise")
st.caption("Avançar salva os dados deste formulário antes de continuar.")

with st.form(f"form_analise_{dados[0] if dados else 'nova'}"):
    campos = ("Nome do aluno *", "RA", "Semestre/Ano", "Situação", "Procedência")
    valores = [
        st.text_input(
            campo,
            value=(dados[indice + 1] or "") if dados else "",
            key=f"analise_{dados[0] if dados else 'nova'}_{indice}",
        )
        for indice, campo in enumerate(campos)
    ]
    voltar, salvar, avancar = st.columns(3)
    voltar.form_submit_button("Voltar", disabled=True)
    salvar_apenas = salvar.form_submit_button("Salvar alterações" if dados else "Salvar análise")
    continuar = avancar.form_submit_button("Avançar", type="primary")

if salvar_apenas or continuar:
    if not valores[0].strip():
        st.error("O nome do aluno é obrigatório.")
    else:
        if dados:
            atualizar_analise(dados[0], *valores)
        else:
            ativar_analise(criar_analise(*valores))
        if continuar:
            ir_para_etapa(1)
        st.rerun()

st.divider()
with st.expander("Selecionar uma análise cadastrada", expanded=dados is None):
    analises = listar_analises()
    if not analises:
        st.info("Nenhuma análise cadastrada.")
    else:
        st.dataframe(
            [dict(zip(("ID", "Aluno", "RA", "Semestre/Ano", "Situação", "Procedência", "Criada em"), analise))
             for analise in analises],
            hide_index=True,
            width="stretch",
        )
        selecionada = st.selectbox(
            "Selecione uma análise",
            analises,
            format_func=lambda analise: f"#{analise[0]} — {analise[1]}",
        )
        if st.button("Ativar análise selecionada"):
            ativar_analise(selecionada[0])
            st.rerun()
