import streamlit as st

from database import (
    listar_analises,
    listar_cursos,
    listar_matrizes_por_curso,
    obter_analise,
    salvar_curso_e_matriz,
)


st.title("Selecionar curso e matriz")

analises = listar_analises()

if not analises:
    st.warning("Crie uma análise antes de selecionar curso e matriz.")
    st.stop()

analise_selecionada = st.selectbox(
    "Selecione a análise",
    analises,
    format_func=lambda analise: f"#{analise[0]} — {analise[1]}"
)

dados_analise = obter_analise(analise_selecionada[0])
cursos = listar_cursos()

curso_atual_id = dados_analise[7]
matriz_atual_id = dados_analise[8]

indice_curso = next(
    (
        indice
        for indice, curso in enumerate(cursos)
        if curso[0] == curso_atual_id
    ),
    0
)

curso_selecionado = st.selectbox(
    "Curso",
    cursos,
    index=indice_curso,
    format_func=lambda curso: f"{curso[1]} — {curso[2]}",
    key=f"curso_{dados_analise[0]}"
)

matrizes = listar_matrizes_por_curso(curso_selecionado[0])

indice_matriz = next(
    (
        indice
        for indice, matriz in enumerate(matrizes)
        if matriz[0] == matriz_atual_id
        and curso_selecionado[0] == curso_atual_id
    ),
    None
)

matriz_selecionada = st.selectbox(
    "Matriz curricular",
    matrizes,
    index=indice_matriz,
    placeholder="Selecione uma matriz",
    format_func=lambda matriz: matriz[2],
    key=f"matriz_{dados_analise[0]}_{curso_selecionado[0]}"
)

if st.button("Salvar seleção e continuar", type="primary"):
    if matriz_selecionada is None:
        st.error("A matriz curricular é obrigatória para continuar.")
    else:
        salvar_curso_e_matriz(
            dados_analise[0],
            curso_selecionado[0],
            matriz_selecionada[0]
        )
        st.success("Curso e matriz curricular salvos com sucesso.")