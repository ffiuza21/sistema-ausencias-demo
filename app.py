import streamlit as st
import database as db
import layout as ly

# ---------- LAYOUT ----------
ly.config_pg()
ly.apply_layout()

# ---------- INICIAR DB ----------
db.init_db()

# ---------- LOGIN ----------
# Estado inicial = usuário deslogado
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    
if not st.session_state.logged_in: # Se não está logado mostre a tela de login
    st.title(":material/login: Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = db.authenticate(usuario, senha)

        if user:
            st.session_state.logged_in = True
            st.session_state.role = user[0]
            st.session_state.username = usuario

            if user[0] in ["admin", "secretaria", "diretor", "coordenador"]:
                st.switch_page("pages/1_Secretaria.py")
            elif user[0] == "professores":
                st.switch_page("pages/2_Professores.py")
        else:
            st.error("Usuário ou senha inválidos")

# ---------- INTERFACE ----------
else:
    st.title(":material/check_circle: Login Realizado")
    st.success(f'**{st.session_state.username}** logado com sucesso!')
    st.info("Use o menu lateral para navegar entre as páginas")

