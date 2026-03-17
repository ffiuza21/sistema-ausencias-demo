import streamlit as st
import database as db
import validators as val
import layout as ly
import permissions as perm
import time
import pandas as pd

# ---------- LAYOUT ----------
ly.config_pg()
ly.apply_layout()

# ---------- PROTEÇÃO DA PÁGINA ----------
perm.require_page_access("Professores")

# ---------- FUNÇÃO CARD PROFESSOR ----------
def exibir_card_professor(professor, turmas, index):
    turmas_prof = db.get_turmas_por_professor(professor)

    with st.container(border=True):
        col1, col2 = st.columns([3,1])
        with col1:
            st.markdown(f"### :material/person: {professor}")
        with col2:
            st.markdown(f"**{len(turmas_prof)}** turmas")
        
        with st.expander(":material/edit: Editar", expanded=False):
            nome_edit = st.text_input("Renomear professor:", value=professor, key=f"edit_{professor}_{index}", label_visibility="collapsed")
            nome_edit_normalizado = val.normalize_nome(nome_edit)
            turmas_do_prof = db.get_turmas_por_professor(professor)
            
            st.write("**Turmas:**")
            turmas_selecionadas = st.multiselect(
                "Selecione ou digite turmas",
                options=list(set(turmas + turmas_do_prof)),
                default=turmas_do_prof,
                key=f"turmas_{professor}_{index}",
                label_visibility="collapsed"
            )
        
        # Botões
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button(":material/save: Salvar Alterações", key=f"save_{professor}_{index}", use_container_width=True, type="secondary"):
                if db.update_vinculo_professor(professor, nome_edit_normalizado, turmas_selecionadas):
                    st.success("✅ Salvo!")
                    # Limpa cache das listas
                    if "modal_professores" in st.session_state:
                        del st.session_state["modal_professores"]
                    if "modal_turmas" in st.session_state:
                        del st.session_state["modal_turmas"]
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Erro ao salvar")
        
        with col4:
            if st.button(":material/delete: Excluir Professor", key=f"del_{professor}_{index}", use_container_width=True, type="primary"):
                st.session_state[f"confirmar_exclusao_prof_{professor}"] = True
        
        # Confirmação de exclusão
        if st.session_state.get(f"confirmar_exclusao_prof_{professor}"):
            st.warning(f"⚠️ Tem certeza que deseja excluir {professor}")
            
            col5, col6 = st.columns(2)
            with col5:
                if st.button("✅ Excluir", key=f"conf_del_{professor}_{index}", use_container_width=True, type="primary"):
                    if db.update_vinculo_professor(professor, professor, []):
                        st.success("✅ Professor excluído!")
                        del st.session_state[f"confirmar_exclusao_prof_{professor}"]
                        # Limpa cache
                        if "modal_professores" in st.session_state:
                            del st.session_state["modal_professores"]
                        if "modal_turmas" in st.session_state:
                            del st.session_state["modal_turmas"]
                        time.sleep(0.5)
                        st.rerun()
            
            with col6:
                if st.button("❌ Cancelar", key=f"canc_del_{professor}_{index}", use_container_width=True):
                    del st.session_state[f"confirmar_exclusao_prof_{professor}"]
                    st.rerun()

# ---------- MODAL ----------
@st.dialog(":material/settings: Gerenciar Professores e Turmas", width="large")
def modal_gerenciar_professores():
    
    # CARREGA DADOS UMA VEZ e guarda em session_state
    if "modal_professores" not in st.session_state:
        st.session_state.modal_professores = db.get_professores()
    
    if "modal_turmas" not in st.session_state:
        st.session_state.modal_turmas = db.get_turmas()
    
    professores = st.session_state.modal_professores
    turmas = st.session_state.modal_turmas
    
    # Abas
    tab1, tab2 = st.tabs([":material/group: Editar Professores", ":material/add: Nova Turma"])
    
    # Aba 1 - editar professores
    with tab1:
        if not professores:
            st.info("📭 Nenhum professor cadastrado ainda.")
        else:
            # Busca e filtro
            st.write("### :material/person_search: Buscar Professor")
            busca_input = st.text_input("Digite o nome do professor:", placeholder="Nome do(a) professor(a)", label_visibility="collapsed")
            busca_normalizada = val.normalize_nome(busca_input)
            
            professores_filtrados = [prof for prof in professores if busca_normalizada in prof] if busca_normalizada else professores
            
            qnt = len(professores_filtrados)
            msg = f"{qnt} professores encontrados" if qnt > 1 else f"{qnt} professor(a) encontrado(a)"
            st.write(f"{msg}")
            
            # Grid professores em pares
            for i in range(0, len(professores_filtrados), 2):
                col1, col2 = st.columns(2)
                
                # Prof 1
                with col1:
                    if i < len(professores_filtrados):
                        exibir_card_professor(professores_filtrados[i], turmas, i)
                
                # Prof 2
                with col2:
                    if i + 1 < len(professores_filtrados):
                        exibir_card_professor(professores_filtrados[i + 1], turmas, i + 1)
    
    # Aba 2 - Nova Turma
    with tab2:
        st.write("### :material/new_label: Cadastrar Nova Turma")
        
        col3, col4 = st.columns(2)
        with col3:
            nova_turma = st.text_input("Número da Turma", placeholder="Ex: 0001", key="input_nova_turma", max_chars=4)
            if nova_turma and not nova_turma.isdigit():
                st.error("Digite apenas números")

        with col4:
            novo_prof = st.text_input("Nome do Professor(a)", placeholder="Ex: JOÃO SILVA", key="input_novo_prof")
            novo_prof_normalizado = val.normalize_nome(novo_prof)
        
        st.info(":material/notifications: Utilize os campos acima para criar novas turmas e professores ou atualizar turmas existentes")
        st.divider()
        
        col5, col6, col7 = st.columns([1, 2, 1])
        with col6:
            if st.button(":material/save: Cadastrar Nova Turma e Professor", use_container_width=True, type="secondary"):
                if not nova_turma or not novo_prof_normalizado:
                    st.error("⚠️ Preencha ambos os campos!")
                    st.stop()
                
                # Busca vínculos existentes
                vinc_existentes = db.get_turmas_por_professor(novo_prof_normalizado)
                
                if nova_turma in vinc_existentes:
                    st.warning(f"⚠️ A turma {nova_turma} já está vinculada a {novo_prof_normalizado}!")
                    st.stop()
                
                vinc_existentes.append(nova_turma)
                
                # Salva
                if db.update_vinculo_professor(novo_prof_normalizado, novo_prof_normalizado, vinc_existentes):
                    st.success(f"✅ Turma {nova_turma} registrada para {novo_prof_normalizado}!")
                    # Limpa cache
                    if "modal_professores" in st.session_state:
                        del st.session_state["modal_professores"]
                    if "modal_turmas" in st.session_state:
                        del st.session_state["modal_turmas"]
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Erro ao salvar no banco de dados.")

# ---------- INTERFACE ----------
st.title(":material/group: Professores")

col1, col2, col3 = st.columns(3)
with col1:
    nome_input = st.text_input("Nome do aluno")
    nome_normalizado = val.normalize_nome(nome_input) if nome_input else None

with col2:
    cpf_input = st.text_input("CPF", max_chars=14)
    cpf_normalizado = val.normalize_cpf(cpf_input) if cpf_input else None

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

if st.button(":material/search: Pesquisar Ausências"):
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
    st.session_state["resultados_pesquisa_prof_df"] = df

    if not resultados:
        st.info("Nenhuma ausência encontrada para os critérios informados.")
        st.stop()

    st.write(f":material/search: Resultados da Pesquisa ({len(df)} ausências encontradas)")
    st.dataframe(df, column_config={"ID": None, "Tipo Doc": None, "Data Registro": None}, hide_index=True)

# ========== BOTÃO GERENCIAR PROFESSORES (CONDICIONAL) ==========
if perm.can_perform_action("editar_professores"):
    if st.button(":material/settings: Gerenciar Professores e Turmas"):
        modal_gerenciar_professores()