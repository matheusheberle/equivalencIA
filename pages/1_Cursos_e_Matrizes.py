import streamlit as st

from database import listar_cursos, listar_matrizes_por_curso


st.title("Cursos e matrizes curriculares")

cursos = listar_cursos()

if not cursos:
    st.warning("Nenhum curso foi encontrado no banco de dados.")
else:
    curso_selecionado = st.selectbox(
        "Selecione um curso",
        cursos,
        format_func=lambda curso: f"{curso[1]} - {curso[2]}"
    )

    matrizes = listar_matrizes_por_curso(curso_selecionado[0])

    st.subheader(f"Matrizes de {curso_selecionado[2]}")

    if matrizes:
        st.dataframe(
            [{"Matriz curricular": matriz[2]} for matriz in matrizes],
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Não há matrizes cadastradas para este curso.")