import streamlit as st

# ---------- PERMISSÕES POR ROLE ----------
PERMISSIONS = {
    "admin": {
        "pages": ["Secretaria", "Professores", "Dados"],
        "actions": {
            "criar_ausencia": True,
            "editar_ausencia": True,
            "deletar_ausencia": True,
            "editar_professores": True,
            "visualizar_dados": True,
        }
    },
    "secretaria": {
        "pages": ["Secretaria", "Dados"],
        "actions": {
            "criar_ausencia": True,
            "editar_ausencia": True,
            "deletar_ausencia": True,
            "editar_professores": False,
            "visualizar_dados": True,
        }
    },
    "professores": {
        "pages": ["Professores", "Dados"],
        "actions": {
            "criar_ausencia": False,
            "editar_ausencia": False,
            "deletar_ausencia": False,
            "editar_professores": False,
            "visualizar_dados": True,
        }
    },
    "diretor": {
        "pages": ["Secretaria", "Professores", "Dados"],
        "actions": {
            "criar_ausencia": True,
            "editar_ausencia": True,
            "deletar_ausencia": True,
            "editar_professores": False,
            "visualizar_dados": True,
        }
    },
    "coordenador": {
        "pages": ["Secretaria", "Professores", "Dados"],
        "actions": {
            "criar_ausencia": False,
            "editar_ausencia": False,
            "deletar_ausencia": False,
            "editar_professores": True,
            "visualizar_dados": True,
        }
    }
}

# ========== FUNÇÕES DE VERIFICAÇÃO ==========

def check_login():
    """Verifica se usuário está logado"""
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        st.info("👉 Use o menu lateral para voltar ao Login")
        st.stop()

def get_user_role():
    """Retorna o role do usuário logado."""
    check_login()
    return st.session_state.get("role", None)

def can_access_page(page_name):
    """Verifica se o usuário pode acessar uma página específica."""
    role = get_user_role()
    if role not in PERMISSIONS:
        return False
    return page_name in PERMISSIONS[role]["pages"]

def can_perform_action(action_name):
    """Verifica se o usuário pode realizar uma ação específica."""
    role = get_user_role()
    if role not in PERMISSIONS:
        return False
    return PERMISSIONS[role]["actions"].get(action_name, False)

def require_page_access(page_name):
    """
    Decorator/função para proteger páginas.
    Bloqueia acesso se usuário não tiver permissão.
    """
    check_login()
    
    if not can_access_page(page_name):
        st.error(f"🚫 Acesso Negado")
        st.warning(f"Seu perfil ({get_user_role()}) não tem permissão para acessar esta página.")
        st.info("👉 Use o menu lateral para navegar para uma página permitida.")
        st.stop()

def show_action_button(label, action_name, key=None, **kwargs):
    """
    Mostra um botão apenas se o usuário tiver permissão para a ação.
    Retorna True se botão foi clicado, False caso contrário.
    """
    if not can_perform_action(action_name):
        return False
    
    return st.button(label, key=key, **kwargs)

def get_allowed_pages():
    """Retorna lista de páginas que o usuário pode acessar."""
    role = get_user_role()
    if role not in PERMISSIONS:
        return []
    return PERMISSIONS[role]["pages"]

# ========== INFORMAÇÕES DE USUÁRIO ==========

def get_username():
    """Retorna o username do usuário logado."""
    return st.session_state.get("username", "Usuário")

def logout():
    """Faz logout do usuário."""
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.rerun()

# ========== HELPER PARA SIDEBAR ==========

def show_user_info():
    """Mostra informações do usuário na sidebar."""
    if "logged_in" in st.session_state and st.session_state.logged_in:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"👤 **Usuário:** {get_username()}")
        st.sidebar.markdown(f"🔑 **Perfil:** {get_user_role().title()}")
        
        if st.sidebar.button("🚪 Sair", use_container_width=True):
            logout()