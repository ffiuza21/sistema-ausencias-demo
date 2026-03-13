"""
Script de migração: SQLite → PostgreSQL (Supabase)
Execute UMA VEZ para transferir dados
"""

import sqlite3
import psycopg2
import os

# ========== CONFIGURAÇÃO ==========
SQLITE_PATH = "controle.db"

# Cole aqui a connection string do Supabase
POSTGRES_URL = "postgresql://postgres:SUA_SENHA@db.xxxxx.supabase.co:5432/postgres"

# ========== FUNÇÕES ==========

def migrate_users(sqlite_conn, postgres_conn):
    """Migra tabela users"""
    sqlite_cur = sqlite_conn.cursor()
    postgres_cur = postgres_conn.cursor()
    
    # Busca dados do SQLite
    sqlite_cur.execute("SELECT username, password_hash, role FROM users")
    users = sqlite_cur.fetchall()
    
    print(f"Migrando {len(users)} usuários...")
    
    for username, password_hash, role in users:
        postgres_cur.execute("""
            INSERT INTO users (username, password_hash, role)
            VALUES (%s, %s, %s)
            ON CONFLICT (username) DO NOTHING
        """, (username, password_hash, role))
    
    postgres_conn.commit()
    print("✅ Usuários migrados!")

def migrate_turmas_professores(sqlite_conn, postgres_conn):
    """Migra tabela turmas_professores"""
    sqlite_cur = sqlite_conn.cursor()
    postgres_cur = postgres_conn.cursor()
    
    sqlite_cur.execute("SELECT turma, professor FROM turmas_professores")
    turmas = sqlite_cur.fetchall()
    
    print(f"Migrando {len(turmas)} turmas...")
    
    for turma, professor in turmas:
        postgres_cur.execute("""
            INSERT INTO turmas_professores (turma, professor)
            VALUES (%s, %s)
            ON CONFLICT (turma) DO UPDATE SET professor = EXCLUDED.professor
        """, (turma, professor))
    
    postgres_conn.commit()
    print("✅ Turmas migradas!")

def migrate_ausencias(sqlite_conn, postgres_conn):
    """Migra tabela ausencias"""
    sqlite_cur = sqlite_conn.cursor()
    postgres_cur = postgres_conn.cursor()
    
    sqlite_cur.execute("""
        SELECT tipo_doc, cpf, nome_aluno, turma_1, turma_2, 
               ausencia_inicio, ausencia_fim, data_ausencia
        FROM ausencias
    """)
    ausencias = sqlite_cur.fetchall()
    
    print(f"Migrando {len(ausencias)} ausências...")
    
    for aus in ausencias:
        tipo_doc, cpf, nome, t1, t2, inicio, fim, data_reg = aus
        postgres_cur.execute("""
            INSERT INTO ausencias 
            (tipo_doc, cpf, nome_aluno, turma_1, turma_2, 
             ausencia_inicio, ausencia_fim, data_ausencia)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (tipo_doc, cpf, nome, t1, t2, inicio, fim, data_reg))
    
    postgres_conn.commit()
    print("✅ Ausências migradas!")

# ========== EXECUÇÃO ==========

def main():
    print("🔄 Iniciando migração SQLite → PostgreSQL...")
    print("-" * 50)
    
    # Conecta nos bancos
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    postgres_conn = psycopg2.connect(POSTGRES_URL)
    
    try:
        # Migra dados
        migrate_users(sqlite_conn, postgres_conn)
        migrate_turmas_professores(sqlite_conn, postgres_conn)
        migrate_ausencias(sqlite_conn, postgres_conn)
        
        print("-" * 50)
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("Agora você pode fazer deploy no Streamlit!")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
    
    finally:
        sqlite_conn.close()
        postgres_conn.close()

if __name__ == "__main__":
    main()