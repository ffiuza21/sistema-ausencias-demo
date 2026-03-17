import streamlit as st
import layout as ly
import validators as val
import database as db
import permissions as perm
import pandas as pd
import sqlite3
import time
from datetime import date, datetime

# ---------- LAYOUT ----------
ly.config_pg()
ly.apply_layout()

# ---------- PROTEÇÃO DA PÁGINA ----------
perm.require_page_access("Secretaria")

# ---------- FORMULÁRIOS / MODAIS ----------
@st.dialog(":material/new_window: Nova Ausência")
def modal_nova_ausencia():
    turmas = db.get_turmas()

    # Tipo de doc
    tipo_doc = st.radio("Documento", ["DECLARACAO", "ATESTADO MEDICO"], horizontal=True)

    # cpf
    cpf_input = st.text_input("CPF", max_chars=14)
    cpf_normalizado = val.normalize_cpf(cpf_input)
    cpf_valido = val.validate_cpf(cpf_normalizado)
    if cpf_input and not cpf_valido:
        st.error("CPF Invalido")

    # nome
    nome_input = st.text_input("Nome do aluno")
    nome_normalizado = val.normalize_nome(nome_input)

    # Turmas e Professores
    col1, col2 = st.columns(2)
    with col1:
        turma_1 = st.selectbox("Nº da Turma 1", options=[""] + turmas, key="turma1")

    with col2:
        professor_1 = db.get_professor_da_turma(turma_1) if turma_1 else ""
        st.text_input("Professor Turma 1", value=professor_1, disabled=True)

    col3, col4 = st.columns(2)
    with col3:
        turma_2 = st.selectbox("Nº da Turma 2 (opcional)", options=[""] + turmas, key="turma2")

    with col4:
        professor_2 = db.get_professor_da_turma(turma_2) if turma_2 else ""
        st.text_input("Professor Turma 2", value=professor_2, disabled=True)

    # Datas
    col5, col6 = st.columns(2)
    with col5:
        inicio = st.date_input("Início da ausência", format="DD/MM/YYYY")
    with col6:
        fim = st.date_input("Fim da ausência", format="DD/MM/YYYY")

    # ---------- CONFIRMAÇÃO FORM ----------
    with st.form("form_nova_ausencia"):
        submitted = st.form_submit_button(":material/save: Salvar", use_container_width=True)

        if submitted:
            # -------- VALIDAÇÕES --------
            if not cpf_valido:
                st.error("CPF inválido. Corrija antes de salvar.")
                st.stop()

            if not nome_normalizado:
                st.error("Nome do aluno é obrigatório.")
                st.stop()

            if not turma_1:
                st.error("A Turma 1 é obrigatória.")
                st.stop()

            if turma_1 and turma_2 and turma_1 == turma_2:
                st.error("Turma 1 e Turma 2 não podem ser iguais.")
                st.stop()

            if fim < inicio:
                st.error("Data final não pode ser anterior à data inicial.")
                st.stop()

            # -------- INSERT NO BANCO --------
            sucesso = db.insert_ausencia(
                tipo_doc,
                cpf_normalizado,
                nome_normalizado,
                turma_1,
                turma_2,
                inicio.isoformat(),
                fim.isoformat()
            )

            if sucesso:
                st.success("Ausência registrada com sucesso")
                time.sleep(1)
                st.rerun()
            else:
                st.warning("Esta ausência já está cadastrada")

@st.dialog(":material/edit: Editar Ausência")
def modal_editar_ausencia(registro):
    turmas = db.get_turmas()
   
   # Tipo doc
    doc_edit = st.radio("Documento", ["DECLARACAO", "ATESTADO MEDICO"], horizontal=True, index=0 if registro["Tipo Doc"] == "DECLARACAO" else 1)

    cpf_input_edit = st.text_input("CPF", max_chars=11, placeholder="Digite apenas números", value=registro["CPF"])
    cpf_normalizado_edit = val.normalize_cpf(cpf_input_edit)
    cpf_valido_edit = val.validate_cpf(cpf_normalizado_edit)
    if cpf_input_edit and not cpf_valido_edit:
        st.error("CPF Invalido")

    # Nome
    nome_input_edit = st.text_input("Nome do aluno", value=registro["Aluno"])
    nome_normalizado_edit = val.normalize_nome(nome_input_edit)

    # Turmas e Professores
    lista_turmas = [""] + turmas
    turma1_salva = registro["Turma 1"]
    turma2_salva = registro["Turma 2"] or ""

    col1, col2 = st.columns(2)
    with col1:
        # Busca índice da turma1, com fallback para 0 se não encontrar
        index_turma1 = lista_turmas.index(turma1_salva) if turma1_salva in lista_turmas else 0
        turma1_edit = st.selectbox("Nº da Turma 1", options=lista_turmas, index=index_turma1, key="turma1_edit")
    with col2:
        professor_1 = db.get_professor_da_turma(turma1_edit) if turma1_edit else ""
        st.text_input("Professor Turma 1", value=professor_1, disabled=True)

    col3, col4 = st.columns(2)
    with col3:
        # Busca índice da turma2, com fallback para 0 se não encontrar
        index_turma2 = lista_turmas.index(turma2_salva) if turma2_salva in lista_turmas else 0
        turma2_edit = st.selectbox("Nº da Turma 2", options=lista_turmas, index=index_turma2, key="turma2_edit")
    with col4:
        professor_2 = db.get_professor_da_turma(turma2_edit) if turma2_edit else ""
        st.text_input("Professor Turma 2", value=professor_2, disabled=True)

    # Data
    inicio_edit = datetime.strptime(registro["Início"], "%d/%m/%Y").date()
    fim_edit = datetime.strptime(registro["Fim"], "%d/%m/%Y").date()

    col5, col6 = st.columns(2)
    with col5:
        inicio_edit = st.date_input("Início da ausência", value=inicio_edit, format="DD/MM/YYYY")
    with col6:
        fim_edit = st.date_input("Fim da ausência", value=fim_edit, format="DD/MM/YYYY")

    # Salvar Alterações
    st.divider()
    
    col7, col8 = st.columns(2)
    with col7:
        if st.button(":material/save: Salvar Alterações", type="secondary", use_container_width=True):

            # ---------- VALIDAÇÕES ----------
            if not cpf_valido_edit:
                st.error("CPF inválido.")
                st.stop()

            if not nome_normalizado_edit:
                st.error("Nome do aluno é obrigatório.")
                st.stop()

            if not turma1_edit:
                st.error("A Turma 1 é obrigatória.")
                st.stop()

            if turma1_edit and turma2_edit and turma1_edit == turma2_edit:
                st.error("Turma 1 e Turma 2 não podem ser iguais.")
                st.stop()

            if fim_edit < inicio_edit:
                st.error("Data final não pode ser anterior à data inicial.")
                st.stop()

            # ---------- UPDATE NO BANCO ----------
            try:
                id_registro = int(registro["ID"])

                db.update_ausencia(
                    id=id_registro,
                    tipo_doc=doc_edit,
                    cpf=cpf_normalizado_edit,
                    nome_aluno=nome_normalizado_edit,
                    turma_1=turma1_edit,
                    turma_2=turma2_edit or None,
                    ausencia_inicio=inicio_edit.isoformat(),
                    ausencia_fim=fim_edit.isoformat()
                )
                st.success("Registro atualizado com sucesso!")
                remover_keys = ["tb_recentes_secretaria", "resetar_editor", "registro_em_edicao", "abrir_modal_edicao"]
                for key in remover_keys:
                    if key in st.session_state:
                        del st.session_state[key]

                time.sleep(1)
                st.rerun()

            except sqlite3.IntegrityError:
                st.error("Esta ausência já está cadastrada")

    with col8:
        if st.button(":material/delete: Excluir Ausência", type="primary", use_container_width=True):
            st.session_state["confirmar_exclusao"] = True

    # Excluir Ausência
    if st.session_state.get("confirmar_exclusao"):
        st.divider()
        st.warning("⚠️ Tem certeza que deseja excluir esta ausência ?")
        
        col9, col10 = st.columns(2)
        with col9:
            if st.button("✅ Excluir", type="primary", use_container_width=True):
                try:
                    id_registro = int(registro["ID"])
                    db.delete_ausencia(id_registro)
                    st.success("Ausência excluída com sucesso!")
                    
                    remover_keys = ["tb_recentes_secretaria", "resetar_editor", "registro_em_edicao", "abrir_modal_edicao", "confirmar_exclusao"]
                    for key in remover_keys:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    time.sleep(1)
                    st.rerun()
                    
                except Exception:
                    st.error(f"Erro ao excluir: {Exception}")
        
        with col10:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state["confirmar_exclusao"] = False
                st.rerun()

@st.dialog(":material/search: Pesquisar Ausência", width="large")
def modal_pesquisa():

    # Campos Busca
    col1, col2, col3 = st.columns(3)
    with col1:
        cpf_input = st.text_input("CPF", max_chars=14)
        cpf_normalizado = val.normalize_cpf(cpf_input) if cpf_input else None
    with col2:
        nome_input = st.text_input("Nome do aluno")
        nome_normalizado = val.normalize_nome(nome_input) if nome_input else None
    with col3:
        turma = st.selectbox("Turma", ["Todas"] + db.get_turmas())
        turma_filtro = None if turma == "Todas" else turma
    
    col4, col5, col6 = st.columns(3)
    with col4:
        professor = st.selectbox("Professor", ["Todos"] + db.get_professores())
        professor_filtro = None if professor == "Todos" else professor 
    with col5:
        data_inicio = st.date_input("Período Ausência de:", format="DD/MM/YYYY")
    with col6:
        data_fim = st.date_input("Até:", format="DD/MM/YYYY")

    st.divider()

    # Botão Pesquisar
    if st.button(":material/person_search: Buscar", use_container_width=True):

        # -------- VALIDAÇÃO DO PERÍODO --------
        if data_fim < data_inicio:
            st.error("A data final não pode ser anterior à data inicial.")
            st.stop()

        # -------- BUSCA NO BANCO --------
        resultados = db.search_ausencias(
            data_inicio=data_inicio.isoformat(),
            data_fim=data_fim.isoformat(),
            cpf=cpf_normalizado,
            nome=nome_normalizado,
            turma=turma_filtro,
            professor=professor_filtro
        )

        if not resultados:
            st.info("Nenhuma ausência encontrada para os critérios informados.")
            st.stop()

        # ---------- DATAFRAME ----------
        df = pd.DataFrame(resultados, columns=[
            "ID",
            "Tipo Doc",
            "Data Registro",
            "CPF",
            "Aluno",
            "Turma 1",
            "Professor 1",
            "Turma 2",
            "Professor 2",
            "Início",
            "Fim"
        ])

        df = df.fillna("")
        # ---------- FORMATAÇÃO DE DATAS ----------
        df["Início"] = df["Início"].apply(val.format_data_dma)
        df["Fim"] = df["Fim"].apply(val.format_data_dma)
        
        st.session_state["resultados_pesquisa_df"] = df

    # ========== EXIBE RESULTADOS SE EXISTIREM ==========
    if "resultados_pesquisa_df" in st.session_state:
        df = st.session_state["resultados_pesquisa_df"]
        
        # ---------- TABELA PESQUISA ----------
        # Só mostra coluna "Editar" se usuário pode editar
        if perm.can_perform_action("editar_ausencia"):
            df["Editar"] = False
        
        st.divider()
        st.write(f":material/search: Resultados da Pesquisa ({len(df)} ausências encontradas)")

        colunas_ocultas = {"ID": None, "Tipo Doc": None, "Data Registro": None}
        colunas_desabilitadas = [coluna for coluna in df.columns if coluna != "Editar"]
        
        if perm.can_perform_action("editar_ausencia"):
            colunas_ocultas["Editar"] = st.column_config.CheckboxColumn("Editar", default=False)
        
        st.data_editor(
            df, 
            column_config=colunas_ocultas,
            hide_index=True, 
            disabled=colunas_desabilitadas,
            key="tb_resultados_pesquisa", 
            use_container_width=True
        )

        # Detecção do checkbox (só se pode editar)
        if perm.can_perform_action("editar_ausencia"):
            if st.session_state.tb_resultados_pesquisa.get("edited_rows"):
                edicoes = st.session_state.tb_resultados_pesquisa["edited_rows"]

                for indice_linha, status in edicoes.items():
                    if status.get("Editar") is True:
                        registro = df.iloc[int(indice_linha)]
                        
                        st.session_state["registro_para_editar"] = registro.to_dict()
                        st.session_state["abrir_modal_edicao_pesquisa"] = True
                        
                        del st.session_state["tb_resultados_pesquisa"]
                        del st.session_state["resultados_pesquisa_df"]
                        
                        st.rerun()
                        break

if st.session_state.get("abrir_modal_edicao_pesquisa"):
    registro_dict = st.session_state["registro_para_editar"]
    registro = pd.Series(registro_dict)
    
    del st.session_state["abrir_modal_edicao_pesquisa"]
    del st.session_state["registro_para_editar"]
    
    modal_editar_ausencia(registro)

# ---------- INTERFACE ----------
st.title(":material/view_cozy: Secretaria")

# ========== BOTÕES (CONDICIONAIS) ==========
# COORDENADOR não vê os botões de criar e pesquisar
if perm.can_perform_action("criar_ausencia"):
    # Admin, Secretaria, Diretor veem ambos os botões
    col1, col2 = st.columns(2)
    with col1:
        if st.button(":material/add_2: Adicionar Nova Ausência", use_container_width=True):
            modal_nova_ausencia()

    with col2:
        if st.button(":material/search: Pesquisar Ausências", use_container_width=True):
            modal_pesquisa()

# Tabela Recentes
st.write("##### :material/data_table: Últimas 100 Ausências Registradas")
ausencias_recentes = db.get_ausencias_recentes()
if not ausencias_recentes:
    st.info("Nenhuma ausência registrada até o momento.")
else:
    df = pd.DataFrame(ausencias_recentes, columns=[
            "ID",
            "Tipo Doc",
            "Data Registro",
            "CPF",
            "Aluno",
            "Turma 1",
            "Professor 1",
            "Turma 2",
            "Professor 2",
            "Início",
            "Fim"
        ]
    )

    df = df.fillna("")
    df["Início"] = df["Início"].apply(val.format_data_dma)
    df["Fim"] = df["Fim"].apply(val.format_data_dma)
    df["Data Registro"] = df["Data Registro"].apply(val.format_data_dm)

    # Só mostra coluna "Editar" se usuário pode editar
    if perm.can_perform_action("editar_ausencia"):
        df["Editar"] = False
        
        edicao = st.data_editor(
            df, 
            column_config={
                "ID": None, 
                "Editar": st.column_config.CheckboxColumn("Editar", default=False)
            }, 
            hide_index=True, 
            disabled=[coluna for coluna in df.columns if coluna != "Editar"], 
            key="tb_recentes_secretaria"
        )

        if st.session_state.tb_recentes_secretaria.get("edited_rows"):
            edicoes = st.session_state.tb_recentes_secretaria["edited_rows"]

            for indice_linha, status in edicoes.items():
                if status.get("Editar") is True:
                    registro = df.iloc[int(indice_linha)]
                    modal_editar_ausencia(registro)
                    st.stop()
    else:
        # Coordenador só pode visualizar (sem coluna Editar)
        st.dataframe(
            df,
            column_config={"ID": None},
            hide_index=True,
            use_container_width=True
        )