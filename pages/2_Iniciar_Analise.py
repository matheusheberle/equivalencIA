import psycopg
import streamlit as st

from database import (
    atualizar_aluno,
    atualizar_analise,
    buscar_alunos_por_nome,
    criar_aluno,
    criar_analise,
    listar_analises,
    obter_aluno,
    normalizar_semestre_ano_ingresso,
)
from navegacao import (
    apresentar_etapa,
    ativar_analise,
    confirmar_salvamento,
    ir_para_etapa,
)


def _chamar_banco(funcao, mensagem, *args):
    """Executa uma operação e apresenta erros PostgreSQL sem perder o fluxo."""
    try:
        return True, funcao(*args)
    except psycopg.Error:
        st.error(mensagem)
        return False, None


@st.dialog("Cadastrar Novo Estudante")
def modal_cadastrar_aluno():
    with st.form("form_modal_aluno"):
        nome = st.text_input("Nome do estudante *", max_chars=150)
        ra = st.text_input("RA (opcional)", max_chars=30)
        cancelar, salvar = st.columns(2)
        cancelou = cancelar.form_submit_button("Cancelar", use_container_width=True)
        salvou = salvar.form_submit_button(
            "Salvar e selecionar", type="primary", use_container_width=True
        )

    if cancelou:
        st.rerun()
    if salvou:
        nome = nome.strip()
        if not nome:
            st.error("O nome do estudante é obrigatório.")
            return
        ok, aluno_id = _chamar_banco(
            criar_aluno,
            "Não foi possível confirmar o cadastro do estudante. Consulte a busca antes de tentar novamente.",
            nome,
            ra.strip() or None,
        )
        if ok:
            st.session_state.aluno_id = aluno_id
            st.session_state.aluno_cadastrado = True
            st.rerun()


@st.dialog("Editar estudante")
def modal_editar_aluno(aluno):
    ident, nome_atual, ra_atual = aluno
    with st.form(f"form_editar_aluno_{ident}"):
        nome = st.text_input("Nome do estudante *", value=nome_atual, max_chars=150)
        ra = st.text_input("RA (opcional)", value=ra_atual or "", max_chars=30)
        cancelar, salvar = st.columns(2)
        cancelou = cancelar.form_submit_button("Cancelar", use_container_width=True)
        salvou = salvar.form_submit_button(
            "Salvar alterações", type="primary", use_container_width=True
        )
    if cancelou:
        st.rerun()
    if salvou:
        nome = nome.strip()
        if not nome:
            st.error("O nome do estudante é obrigatório.")
            return
        ok, atualizado = _chamar_banco(
            atualizar_aluno,
            "Não foi possível confirmar as alterações do estudante. Tente novamente.",
            ident,
            nome,
            ra.strip() or None,
        )
        if ok and atualizado:
            st.session_state.aluno_id = ident
            st.session_state.aluno_atualizado = True
            st.rerun()
        if ok and not atualizado:
            st.error("O estudante não foi encontrado. Atualize a busca e tente novamente.")


def _texto(valor):
    return valor if valor not in (None, "") else "—"


def _submeter_busca_aluno():
    st.session_state.busca_aluno_enviada = st.session_state.get("busca_aluno", "").strip()


dados = apresentar_etapa(0)
st.caption(
    "Salve antes de voltar, trocar de análise ou navegar para outra página. "
    "Alterações não salvas podem ser descartadas."
)

tab_nova, tab_historico = st.tabs(["📝 Nova Análise", "📂 Histórico de Análises"])

with tab_nova:
    aluno_valido = bool(dados)
    if dados:
        aluno_id = dados[9]
        with st.container(border=True):
            info, acao = st.columns(
                [3, 1.3], vertical_alignment="center"
            )
            info.subheader(f"Análise #{dados[0]} em andamento")
            info.markdown(f"**Estudante:** {dados[1]} — cadastro nº {aluno_id}")
            info.markdown(f"**RA:** {_texto(dados[2])}")
            if acao.button("Trocar análise", use_container_width=True):
                ativar_analise(None)
                st.session_state.aluno_id = None
                st.rerun()
    else:
        aluno_id = st.session_state.get("aluno_id")
        st.subheader("1. Identificação do estudante")
        if st.session_state.pop("aluno_cadastrado", False):
            st.success("Estudante cadastrado e selecionado.")
        if st.session_state.pop("aluno_atualizado", False):
            st.success("Cadastro do estudante atualizado.")

        if aluno_id is None:
            busca, acao_busca, novo = st.columns(
                [5, 1.3, 1.6], vertical_alignment="bottom"
            )
            busca.text_input(
                "Buscar estudante",
                placeholder="Nome ou parte do nome",
                key="busca_aluno",
                on_change=_submeter_busca_aluno,
            )
            if acao_busca.button(
                "🔍 Buscar", type="secondary", use_container_width=True
            ):
                _submeter_busca_aluno()
            if novo.button(
                "＋ Novo estudante", type="secondary", use_container_width=True
            ):
                modal_cadastrar_aluno()

        termo = st.session_state.get("busca_aluno_enviada", "")
        if aluno_id is None and termo:
            ok, resultados = _chamar_banco(
                buscar_alunos_por_nome,
                "Não foi possível carregar os resultados da busca. Tente novamente.",
                termo,
            )
            if ok and not resultados:
                st.info("Nenhum estudante encontrado.")
            elif ok:
                for ident, nome, ra in resultados:
                    with st.container(border=True):
                        info, escolher, editar = st.columns(
                            [4.5, 1.2, 1], vertical_alignment="center"
                        )
                        info.write(f"**{nome}**")
                        info.caption(f"RA: {_texto(ra)} · Cadastro nº {ident}")
                        if escolher.button(
                            "Selecionar",
                            key=f"selecionar_aluno_{ident}",
                            type="primary",
                            use_container_width=True,
                        ):
                            st.session_state.aluno_id = ident
                            st.session_state.pop("editando_aluno_id", None)
                            st.rerun()
                        if editar.button(
                            "Editar",
                            key=f"editar_aluno_{ident}",
                            use_container_width=True,
                        ):
                            ok_aluno, aluno_edicao = _chamar_banco(
                                obter_aluno,
                                "Não foi possível carregar o estudante para edição. Tente novamente.",
                                ident,
                            )
                            if ok_aluno and aluno_edicao:
                                modal_editar_aluno(aluno_edicao)
                            elif ok_aluno:
                                st.warning("O estudante não foi encontrado. Atualize a busca e tente novamente.")
        elif aluno_id is None and not termo:
            st.info("Digite o nome ou parte do nome para buscar um estudante.")

        aluno = None
        if aluno_id is not None:
            ok, aluno = _chamar_banco(
                obter_aluno,
                "Não foi possível carregar o estudante selecionado. Tente novamente.",
                aluno_id,
            )
            if ok and aluno is None:
                st.session_state.aluno_id = None
                aluno_id = None
                st.warning("O estudante selecionado não foi encontrado. Selecione outro estudante.")
            elif ok:
                aluno_valido = True
                with st.container(border=True):
                    info, remover = st.columns(
                        [3.5, 1.2], vertical_alignment="center"
                    )
                    info.success(f"Estudante selecionado: **{aluno[1]}**")
                    info.caption(f"RA: {_texto(aluno[2])} · Cadastro nº {aluno[0]}")
                    if remover.button(
                        "Trocar estudante",
                        use_container_width=True,
                    ):
                        st.session_state.aluno_id = None
                        st.rerun()

    st.divider()
    st.subheader("2. Dados da análise")
    if not aluno_valido:
        if st.session_state.get("aluno_id") is None:
            st.info("Selecione ou cadastre um estudante para liberar os dados da análise.")
    else:
        st.caption("Avançar salva os dados antes de continuar.")
        analise_id = dados[0] if dados else "nova"
        with st.form(f"form_analise_{analise_id}"):
            semestre_ano = st.text_input(
                "Semestre/Ano de ingresso",
                value=(dados[3] or "") if dados else "",
                placeholder="1/2027 ou 2/2027",
                help="Informe o semestre e o ano previstos para ingresso no curso de destino.",
                key=f"analise_{analise_id}_semestre_ano",
            )
            salvar, avancar = st.columns(2)
            salvar_apenas = salvar.form_submit_button(
                "Salvar alterações" if dados else "Salvar análise",
                use_container_width=True,
            )
            continuar = avancar.form_submit_button(
                "Avançar", type="primary", use_container_width=True
            )

        if salvar_apenas or continuar:
            try:
                semestre_ano = normalizar_semestre_ano_ingresso(semestre_ano)
            except ValueError as erro:
                st.error(str(erro))
            else:
                if dados:
                    ok, salvo = _chamar_banco(
                        atualizar_analise,
                        "Não foi possível confirmar o salvamento da análise. Consulte o histórico antes de tentar novamente.",
                        dados[0],
                        semestre_ano,
                    )
                else:
                    ok, nova_analise_id = _chamar_banco(
                        criar_analise,
                        "Não foi possível confirmar o salvamento da análise. Consulte o histórico antes de tentar novamente.",
                        aluno_id,
                        semestre_ano,
                    )
                    salvo = ok
                if ok:
                    if not salvo:
                        st.error("As alterações não foram salvas porque a análise não foi encontrada. Selecione outra análise no histórico.")
                    else:
                        if not dados:
                            ativar_analise(nova_analise_id)
                        confirmar_salvamento(
                            "Dados da análise salvos com sucesso.", 1 if continuar else 0
                        )
                        if continuar:
                            ir_para_etapa(1)
                        st.rerun()

with tab_historico:
    st.subheader("Análises cadastradas")
    ok, analises = _chamar_banco(
        listar_analises,
        "Não foi possível carregar as análises cadastradas. Tente novamente.",
    )
    if ok and not analises:
        st.info("Nenhuma análise cadastrada.")
    elif ok:
        tabela_dados = [
            {
                "ID da análise": a[0],
                "ID do estudante": a[9],
                "Estudante": _texto(a[1]),
                "RA": _texto(a[2]),
                "Semestre/Ano": _texto(a[3]),
                "Curso de origem": _texto(a[10]),
                "Situação": _texto(a[4]),
                "Procedência": _texto(a[5]),
                "Criada em": str(a[6])[:10] if a[6] else "—",
            }
            for a in analises
        ]
        tabela = st.dataframe(
            tabela_dados,
            hide_index=True,
            width="stretch",
            on_select="rerun",
            selection_mode="single-row",
        )
        linhas = tabela.selection.rows
        selecionada = analises[linhas[0]] if linhas else None
        if selecionada:
            if st.button(
                f"Carregar análise #{selecionada[0]} — {selecionada[1]}",
                type="primary",
            ):
                ativar_analise(selecionada[0])
                st.rerun()
        else:
            st.button("Selecione uma linha para carregar a análise", disabled=True)
