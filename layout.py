import streamlit as st

def config_pg():
    st.set_page_config(
        page_title="Sistema de Ausências",
        page_icon="📋",
        layout="wide"
    )

# ----- SIDEBAR -----
def apply_layout():
    st.markdown("""
    <style>
    div[data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.title(":material/menu: Navegação")

    # Menu sempre visível (Login)
    st.sidebar.page_link("app.py",label=":material/login: Login")

    # Menu dinâmico baseado em permissões
    if "logged_in" in st.session_state and st.session_state.logged_in:
        role = st.session_state.get("role", "")
        
        page_permissions = {
            "admin": ["Secretaria", "Professores", "Dados"],
            "secretaria": ["Secretaria", "Dados"],
            "professores": ["Professores", "Dados"],
            "diretor": ["Secretaria", "Professores", "Dados"],
            "coordenador": ["Secretaria", "Professores", "Dados"]
        }
        
        allowed_pages = page_permissions.get(role, [])
        
        # Mostra apenas páginas permitidas
        if "Secretaria" in allowed_pages:
            st.sidebar.page_link("pages/1_Secretaria.py", label=":material/view_cozy: Secretaria")
        
        if "Professores" in allowed_pages:
            st.sidebar.page_link("pages/2_Professores.py",label=":material/group: Professores")
        
        if "Dados" in allowed_pages:
            st.sidebar.page_link("pages/3_Dados.py",label=":material/bar_chart: Dados")
        
        # Info do usuário
        st.sidebar.markdown("---")
        st.sidebar.markdown(f":material/boy: {st.session_state.get('username', 'N/A')}")

    st.markdown("""
        <style>
        /* Esconde footer padrão do Streamlit */
        footer {visibility: hidden;}
        
        /* Customiza o menu para mostrar só o botão de tema */
        [data-testid="stToolbar"] {
            display: flex !important;
            visibility: visible !important;
        }
        
        /* Esconde itens do menu exceto configurações */
        #MainMenu > div > ul > li:not(:last-child) {
            display: none;
        }
        
        /* Rodapé minimalista - apenas texto */
        .dev-footer {
            position: fixed;
            bottom: 10px;
            right: 20px;
            font-size: 12px;
            color: #808495;
            z-index: 999;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .dev-footer a.name-link {
            color: #808495;
            text-decoration: none;
            transition: color 0.2s ease;
        }
               
        /* Ícones sociais */
        .dev-footer .social-icons {
            display: flex;
            gap: 6px;
            margin-left: 4px;
        }
        
        .dev-footer .social-icons a {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 18px;
            height: 18px;
            color: #808495;
            text-decoration: none;
            transition: color 0.2s ease, transform 0.2s ease;
            opacity: 0.8;
        }
        
        .dev-footer .social-icons a:hover {
            opacity: 1;
            transform: translateY(-1px);
        }
        
        .dev-footer .social-icons a.linkedin:hover {
            color: #0077b5;
        }
        
        .dev-footer .social-icons a.github:hover {
            color: #000000;
        }
        
        /* Ícones SVG inline */
        .dev-footer .social-icons svg {
            width: 16px;
            height: 16px;
            fill: currentColor;
        }
        </style>
        
        <div class="dev-footer">
            <span>Desenvolvido por</span>
            <div class="social-icons">
                <a href="https://www.linkedin.com/in/ffiuza/" target="_blank" class="linkedin" title="LinkedIn">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                    </svg>
                </a>
                <a href="https://github.com/ffiuza21" target="_blank" class="github" title="GitHub">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)
