# 📊 Sistema de Controle de Ausências Escolares

> Sistema de gestão de ausências com autenticação, controle de acesso baseado em funções (RBAC) e interface intuitiva. Todos os dados das ausências são fictícios.

**[🚀 Acesse a Demo Aqui](https://sistema-ausencias-demo.streamlit.app/)**

> ⚠️ **Nota:** Esta é uma versão de demonstração com 5.000 registros 
> fictícios gerados para fins de portfólio. O sistema foi originalmente 
> desenvolvido para uso em ambiente real com dados reais.

### 👤 Credenciais de Teste

| Perfil | Usuário | Senha |
|--------|---------|-------|
| 👨‍💼 Admin | `admin` | `demo123` |
| 📝 Secretaria | `secretaria` | `demo123` |
| 👨‍🏫 Professor | `professor` | `demo123` |
| 🎯 Coordenador | `coordenador` | `demo123` |

---

## ✨ Funcionalidades

### 🔐 Sistema de Autenticação
- Login com senha hash SHA-256
- Controle de acesso baseado em funções (RBAC)

### 📋 Gestão de Ausências (admin/secretaria)
- Cadastro de ausências com validação de CPF
- Detecção automática de duplicatas
- Busca com múltiplos filtros
- Edição e exclusão de ausências (permissões)

### 👨‍🏫 Visão do Professor (admin/professor)
- Visualizar ausências apenas das suas turmas
- Filtrar alunos por turma específica
- Acompanhar períodos de ausência
- Exportar relatórios das suas turmas

### 👥 Gerenciamento de Professores (admin/coordenador)
- Vincular turmas a professores
- Edição de vínculos em tempo real
- Busca rápida de professores

### 📊 Visualização de Dados (todos)
- Dashboard intuitivo
- Tabelas com paginação
- Exportação de dados
- Filtros de dados dinâmicos (por ano)

---

## 🛠️ Tecnologias

**Frontend:**
- [Streamlit](https://streamlit.io) - Interface web interativa
- CSS customizado

**Backend:**
- Python 3.9+
- PostgreSQL (Supabase)
- SQLite (desenvolvimento local)

**Bibliotecas:**
- `pandas` - Manipulação de dados
- `psycopg2` - Conexão PostgreSQL
- `unidecode` - Normalização de texto
- `plotly` - Gráficos (futuro)

---

## 📁 Estrutura do Projeto

```
sistema-ausencias/
├── app.py                    # Aplicação principal (login)
├── database.py               # Gerenciamento do banco de dados
├── layout.py                 # Layout e estilização
├── permissions.py            # Sistema RBAC
├── validators.py             # Validações (CPF, nomes, datas)
├── pages/
│   ├── 1_Secretaria.py      # Página da secretaria
│   ├── 2_Professores.py     # Página de professores
│   └── 3_Dados.py           # Visualização de dados
├── data/
│   ├── dados_demo_ausencias.csv      # Dados importados
│   └── turmas_professores_demo.csv
├── requirements.txt
└── README.md
```

---

## 🎯 Permissões por Perfil

| Funcionalidade | Admin | Secretaria | Professor | Coordenador |
|----------------|-------|------------|-----------|-------------|
| Cadastrar ausências | ✅ | ✅ | ❌ | ❌ |
| Editar ausências | ✅ | ✅ | ❌ | ❌ |
| Excluir ausências | ✅ | ✅ | ❌ | ❌ |
| Pesquisar ausências | ✅ | ✅ | ✅ | ✅ |
| Gerenciar professores | ✅ | ❌ | ❌ | ✅ |
| Visualizar dados | ✅ | ✅ | ✅ | ✅ |

---

## 👨‍💻 Autor

**Felipe Fiuza**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ffiuza/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ffiuza21)

---
