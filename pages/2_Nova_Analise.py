import streamlit as st

from database import (
    atualizar_analise, buscar_alunos_por_nome, criar_aluno, criar_analise,
    listar_analises, obter_aluno,
)
from navegacao import apresentar_etapa, ativar_analise, ir_para_etapa


dados = apresentar_etapa(0)

if dados and st.button("Cadastrar outra análise"):
    ativar_analise(None)
    st.rerun()

aluno_id = dados[9] if dados else None
if dados:
    st.write(f"Aluno: {dados[1]} — cadastro nº {aluno_id}")
    st.write(f"RA: {dados[2] or 'Não informado'}")
else:
    with st.expander("Cadastrar aluno"):
        with st.form("form_aluno", clear_on_submit=True):
            nome = st.text_input("Nome do aluno *", max_chars=150)
            ra = st.text_input("RA (opcional)", max_chars=30)
            cadastrar = st.form_submit_button("Salvar aluno")
        if cadastrar:
            nome = nome.strip()
            ra = ra.strip() or None
            if not nome:
                st.error("O nome do aluno é obrigatório.")
            else:
                st.session_state.aluno_id = criar_aluno(nome, ra)
                st.success("Aluno cadastrado. Você já pode iniciar uma análise para ele.")

    st.subheader("Buscar aluno")
    termo = st.text_input("Nome ou parte do nome", key="busca_aluno").strip()
    if termo:
        resultados = buscar_alunos_por_nome(termo)
        st.subheader("Resultados")
        if not resultados:
            st.info("Nenhum aluno encontrado.")
        for ident, nome, ra in resultados:
            with st.container(border=True):
                st.write(nome)
                st.write(f"RA: {ra}" if ra else "RA não informado")
                st.caption(f"Cadastro nº {ident}")
                if st.button("Selecionar", key=f"selecionar_aluno_{ident}"):
                    st.session_state.aluno_id = ident
                    st.rerun()
    else:
        st.info("Digite o nome ou parte do nome para buscar um aluno.")

    aluno_id = st.session_state.aluno_id
    aluno = obter_aluno(aluno_id) if aluno_id is not None else None
    if aluno:
        st.write(f"Aluno selecionado: {aluno[1]} — cadastro nº {aluno[0]}")
        st.write(f"RA: {aluno[2]}" if aluno[2] else "RA não informado")
        if st.button("Limpar seleção"):
            st.session_state.aluno_id = None
            st.rerun()
    elif aluno_id is not None:
        st.session_state.aluno_id = aluno_id = None
        st.warning("O aluno selecionado não foi encontrado. Selecione outro aluno.")

st.subheader("Dados da análise ativa" if dados else "Iniciar análise para o aluno selecionado")
st.caption("Avançar salva os dados deste formulário antes de continuar.")

with st.form(f"form_analise_{dados[0] if dados else 'nova'}"):
    semestre_ano = st.text_input(
        "Semestre/Ano",
        value=(dados[3] or "") if dados else "",
        key=f"analise_{dados[0] if dados else 'nova'}_semestre_ano",
    )
    voltar, salvar, avancar = st.columns(3)
    voltar.form_submit_button("Voltar", disabled=True)
    salvar_apenas = salvar.form_submit_button("Salvar alterações" if dados else "Salvar análise")
    continuar = avancar.form_submit_button("Avançar", type="primary")

if salvar_apenas or continuar:
    if aluno_id is None:
        st.error("Cadastre ou selecione um aluno para iniciar a análise.")
    else:
        if dados:
            atualizar_analise(dados[0], semestre_ano.strip())
        else:
            ativar_analise(criar_analise(aluno_id, semestre_ano.strip()))
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
            [
                {
                    "ID da análise": analise[0],
                    "ID do aluno": analise[9],
                    "Aluno": analise[1],
                    "RA": analise[2],
                    "Semestre/Ano": analise[3],
                    "Curso de origem": analise[10],
                    "Situação": analise[4],
                    "Procedência": analise[5],
                    "Criada em": analise[6],
                }
                for analise in analises
            ],
            hide_index=True,
            width="stretch",
        )
        selecionada = st.selectbox(
            "Selecione uma análise",
            analises,
            format_func=lambda analise: (
                f"Análise #{analise[0]} — {analise[1]} — Aluno #{analise[9]}"
            ),
        )
        if st.button("Ativar análise selecionada"):
            ativar_analise(selecionada[0])
            st.rerun()
