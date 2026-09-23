import streamlit as st
import psycopg

from database import salvar_origem_aproveitamento
from navegacao import apresentar_etapa, confirmar_salvamento, ir_para_etapa


situacoes = ("Concluído", "Incompleto", "Trancado")
dados = apresentar_etapa(1)
st.caption("Informe a formação anterior do aluno. Não informe aqui o período de encaixe na UNIPAR.")

with st.form(f"form_origem_{dados[0]}"):
    with st.container(border=True):
        st.subheader("Origem do Aproveitamento")
        curso_origem = st.text_input(
            "Curso de origem",
            value=dados[10] or "",
            max_chars=150,
            key=f"curso_origem_{dados[0]}",
        )
        situacao_atual = dados[4]
        indice_situacao = situacoes.index(situacao_atual) if situacao_atual in situacoes else None
        situacao_origem = st.selectbox(
            "Situação do curso de origem",
            situacoes,
            index=indice_situacao,
            placeholder="Selecione uma situação",
            key=f"situacao_origem_{dados[0]}",
        )
        procedencia = st.text_input(
            "Instituição/faculdade de procedência",
            value=dados[5] or "",
            max_chars=150,
            key=f"procedencia_{dados[0]}",
        )

    voltar, salvar, avancar = st.columns(3)
    voltar_clicked = voltar.form_submit_button("Voltar")
    salvar_apenas = salvar.form_submit_button("Salvar alterações")
    continuar = avancar.form_submit_button("Avançar", type="primary")

if voltar_clicked:
    ir_para_etapa(0)

if salvar_apenas or continuar:
    if situacao_origem not in situacoes:
        st.error("Selecione a situação do curso de origem.")
    else:
        try:
            salvar_origem_aproveitamento(
                dados[0],
                curso_origem,
                situacao_origem,
                procedencia,
            )
        except psycopg.Error:
            st.error("Não foi possível confirmar o salvamento da origem do aproveitamento. Tente salvar novamente.")
        else:
            confirmar_salvamento("Origem do aproveitamento salva com sucesso.", 2 if continuar else 1)
            if continuar:
                ir_para_etapa(2)
            st.rerun()
