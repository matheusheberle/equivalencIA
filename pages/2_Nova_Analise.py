import streamlit as st

from database import (
    atualizar_analise,
    criar_analise,
    listar_analises,
    obter_analise,
)


st.title("Nova análise curricular")

st.subheader("Cadastrar nova análise")

with st.form("form_nova_analise"):
    nome_aluno = st.text_input("Nome do aluno *")
    ra = st.text_input("RA")
    semestre_ano = st.text_input("Semestre/Ano")
    situacao = st.text_input("Situação")
    procedencia = st.text_input("Procedência")

    salvar = st.form_submit_button("Salvar e continuar")

if salvar:
    if not nome_aluno.strip():
        st.error("O nome do aluno é obrigatório.")
    else:
        analise_id = criar_analise(
            nome_aluno,
            ra,
            semestre_ano,
            situacao,
            procedencia
        )
        st.success(f"Análise nº {analise_id} criada com sucesso.")


st.divider()
st.subheader("Análises cadastradas")

analises = listar_analises()

if not analises:
    st.info("Nenhuma análise cadastrada.")
else:
    st.dataframe(
        [
            {
                "ID": analise[0],
                "Aluno": analise[1],
                "RA": analise[2],
                "Semestre/Ano": analise[3],
                "Situação": analise[4],
                "Procedência": analise[5],
                "Criada em": analise[6]
            }
            for analise in analises
        ],
        hide_index=True,
        use_container_width=True
    )

    analise_selecionada = st.selectbox(
        "Selecione uma análise para editar",
        analises,
        format_func=lambda analise: f"#{analise[0]} — {analise[1]}"
    )

    dados = obter_analise(analise_selecionada[0])

    st.subheader("Editar análise")

    with st.form("form_editar_analise"):
        nome_editado = st.text_input(
            "Nome do aluno *",
            value=dados[1],
            key=f"nome_{dados[0]}"
        )
        ra_editado = st.text_input(
            "RA",
            value=dados[2] or "",
            key=f"ra_{dados[0]}"
        )
        semestre_editado = st.text_input(
            "Semestre/Ano",
            value=dados[3] or "",
            key=f"semestre_{dados[0]}"
        )
        situacao_editada = st.text_input(
            "Situação",
            value=dados[4] or "",
            key=f"situacao_{dados[0]}"
        )
        procedencia_editada = st.text_input(
            "Procedência",
            value=dados[5] or "",
            key=f"procedencia_{dados[0]}"
        )

        atualizar = st.form_submit_button("Salvar alterações")

    if atualizar:
        if not nome_editado.strip():
            st.error("O nome do aluno é obrigatório.")
        else:
            atualizar_analise(
                dados[0],
                nome_editado,
                ra_editado,
                semestre_editado,
                situacao_editada,
                procedencia_editada
            )
            st.success("Análise atualizada com sucesso.")