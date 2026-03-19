import database as db
import os

print("🔄 Configurando banco local com dados corretos...")
print("-" * 50)

# CRIAR BANCO
db.init_db()
print("✅ Banco inicializado (tabelas criadas)")

# IMPORTAR TURMAS
db.import_turmas_csv("data/turmas_professores_demo.csv")
print("✅ Turmas e professores importados")

# IMPORTAR AUSÊNCIAS
db.import_ausencias_csv("data/dados_ausencias_demo.csv")
print("✅ Ausências importadas")

# CRIAR USUÁRIOS
usuarios = [
    ("admin", "demo123", "admin"),
    ("secretaria", "demo123", "secretaria"),
    ("professor", "demo123", "professores"),
    ("coordenador", "demo123", "coordenador"),
]

for username, password, role in usuarios:
    db.create_user(username, password, role)

print("🎉 BANCO LOCAL CONFIGURADO COM SUCESSO!")
print("\n📋 Próximo passo:")
print("   Execute: streamlit run app.py")