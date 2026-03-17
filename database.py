import os
import hashlib
import csv
from datetime import datetime
import validators as val
import streamlit as st

# Detecta ambiente (local ou produção)
DATABASE_URL = os.getenv("DATABASE_URL")  # Supabase fornece isso

if DATABASE_URL:
    # PRODUÇÃO: PostgreSQL (Supabase)
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    def get_connection():
        return psycopg2.connect(DATABASE_URL)
else:
    # LOCAL: SQLite
    import sqlite3
    DB_PATH = "controle.db"
    
    def get_connection():
        return sqlite3.connect(DB_PATH, timeout=10)

#-------- USUÁRIOS --------
def hash_password(password):
    """Transforma senha em um hash SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

#-------- INICIAR DB --------
def init_db():
    """Iniciar a base de dados, criar tabelas e views se não existirem"""
    with get_connection() as conn:
        cursor = conn.cursor()

        # ---------- USERS ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """ if DATABASE_URL else """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)

        # ---------- TURMAS / PROFESSORES ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS turmas_professores (
                turma TEXT PRIMARY KEY,
                professor TEXT NOT NULL
            )
        """)

        # ---------- AUSÊNCIAS ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ausencias (
                id SERIAL PRIMARY KEY,
                tipo_doc TEXT NOT NULL,
                cpf TEXT NOT NULL,
                nome_aluno TEXT NOT NULL,
                turma_1 TEXT NOT NULL,
                turma_2 TEXT,
                ausencia_inicio TEXT NOT NULL,
                ausencia_fim TEXT NOT NULL,
                data_ausencia TEXT NOT NULL,

                UNIQUE (
                    cpf,
                    turma_1,
                    turma_2,
                    ausencia_inicio,
                    ausencia_fim
                )
            )
        """ if DATABASE_URL else """
            CREATE TABLE IF NOT EXISTS ausencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_doc TEXT NOT NULL,
                cpf TEXT NOT NULL,
                nome_aluno TEXT NOT NULL,
                turma_1 TEXT NOT NULL,
                turma_2 TEXT,
                ausencia_inicio TEXT NOT NULL,
                ausencia_fim TEXT NOT NULL,
                data_ausencia TEXT NOT NULL,

                UNIQUE (
                    cpf,
                    turma_1,
                    turma_2,
                    ausencia_inicio,
                    ausencia_fim
                )
            )
        """)

        # CREATE OR REPLACE VIEW (compatível com PostgreSQL)
        cursor.execute("""
            CREATE OR REPLACE VIEW view_ausencias AS
            SELECT
                ausencias.id,
                ausencias.tipo_doc,
                ausencias.data_ausencia,
                ausencias.cpf,
                ausencias.nome_aluno,
                ausencias.turma_1,
                tp1.professor AS professor_1,
                ausencias.turma_2,
                COALESCE(tp2.professor, '') AS professor_2,
                ausencias.ausencia_inicio,
                ausencias.ausencia_fim
            FROM ausencias
        
            LEFT JOIN turmas_professores tp1
                ON ausencias.turma_1 = tp1.turma 
            LEFT JOIN turmas_professores tp2
                ON ausencias.turma_2 = tp2.turma
        """)
        
        conn.commit()

def create_user(username, password, role):
    """Criar usuário e senha"""
    with get_connection() as conn:
        cursor = conn.cursor()
        password_hash = hash_password(password)
        
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)" if DATABASE_URL 
                else "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )
            conn.commit()
        except Exception as e:
            print(f"Erro ao criar usuário {username}: {e}")

def authenticate(username, password):
    """Autenticar se login é válido"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT role FROM users WHERE username=%s AND password_hash=%s" if DATABASE_URL
            else "SELECT role FROM users WHERE username=? AND password_hash=?",
            (username, hash_password(password))
        )
        
        return cursor.fetchone()

#-------- DADOS INICIAIS --------
def import_turmas_csv(caminho_csv="data/turmas_professores.csv"):
    """Importar turmas e professores de CSV"""
    with get_connection() as conn:
        cursor = conn.cursor()

        with open(caminho_csv, encoding="utf-8") as arquivo:
            leitor = csv.DictReader(arquivo, delimiter=';')

            for linha in leitor:
                turma = linha["turma"].strip()
                professor = linha["professor"].strip()

                if DATABASE_URL:
                    cursor.execute(
                        """
                        INSERT INTO turmas_professores (turma, professor)
                        VALUES (%s, %s)
                        ON CONFLICT (turma) DO UPDATE SET professor = EXCLUDED.professor
                        """,
                        (turma, professor)
                    )
                else:
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO turmas_professores (turma, professor)
                        VALUES (?, ?)
                        """,
                        (turma, professor)
                    )
        conn.commit()

def import_ausencias_csv(caminho_csv):
    with get_connection() as conn:
        cursor = conn.cursor()

        with open(caminho_csv, encoding="utf-8") as arquivo:
            leitor = csv.DictReader(arquivo)

            for linha in leitor:
                tipo_doc = linha["tipo_doc"].strip()
                cpf = linha["cpf"].strip()
                nome_aluno = linha["nome_aluno"].strip()
                turma_1 = linha["turma_1"].strip()
                turma_2 = linha["turma_2"].strip() or None

                ausencia_inicio = linha["ausencia_inicio"].strip()
                ausencia_fim = linha["ausencia_fim"].strip()
                data_ausencia = linha["data_ausencia"].strip()
       
                if DATABASE_URL:
                    cursor.execute("""
                        INSERT INTO ausencias (
                            tipo_doc, cpf, nome_aluno, turma_1, turma_2,
                            ausencia_inicio, ausencia_fim, data_ausencia
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (tipo_doc, cpf, nome_aluno, turma_1, turma_2,
                          ausencia_inicio, ausencia_fim, data_ausencia))
                else:
                    cursor.execute("""
                        INSERT OR REPLACE INTO ausencias (
                            tipo_doc, cpf, nome_aluno, turma_1, turma_2,
                            ausencia_inicio, ausencia_fim, data_ausencia
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (tipo_doc, cpf, nome_aluno, turma_1, turma_2,
                          ausencia_inicio, ausencia_fim, data_ausencia))
        conn.commit()

#-------- TURMAS E PROFESSORES --------
@st.cache_data(ttl=300)
def get_turmas():
    """Retornar lista com todas as turmas"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT turma FROM turmas_professores ORDER BY turma")
        return [linha[0] for linha in cursor.fetchall()]

@st.cache_data(ttl=300)
def get_professores():
    """Retornar lista com todos os professores"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT professor FROM turmas_professores ORDER BY professor")
        return [linha[0] for linha in cursor.fetchall()]

@st.cache_data(ttl=60)
def get_professor_da_turma(turma):
    """Retornar professor de turma passada como argumento se existir"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT professor FROM turmas_professores WHERE turma = %s" if DATABASE_URL
            else "SELECT professor FROM turmas_professores WHERE turma = ?",
            (turma,)
        )
        professor_turma = cursor.fetchone()
        return professor_turma[0] if professor_turma else ""

@st.cache_data(ttl=60)
def get_turmas_por_professor(nome_professor):
    """Retorna a lista de turmas vinculadas a um professor específico"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT turma FROM turmas_professores WHERE professor = %s ORDER BY turma ASC" if DATABASE_URL
            else "SELECT turma FROM turmas_professores WHERE professor = ? ORDER BY turma ASC",
            (nome_professor,)
        )
        return [linha[0] for linha in cursor.fetchall()]

def update_vinculo_professor(nome_original, nome_novo, turmas_finais):
    """Atualiza vínculos entre professores e turmas"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            placeholder = "%s" if DATABASE_URL else "?"
            
            # 1. PRIMEIRO: Remove turmas desmarcadas (usando nome ORIGINAL)
            if turmas_finais:
                placeholders = ','.join([placeholder] * len(turmas_finais))
                query = f"DELETE FROM turmas_professores WHERE professor = {placeholder} AND turma NOT IN ({placeholders})"
                cursor.execute(query, (nome_original, *turmas_finais))
            else:
                # Se não tem turmas finais, remove TODAS as turmas do professor
                cursor.execute(
                    f"DELETE FROM turmas_professores WHERE professor = {placeholder}",
                    (nome_original,)
                )
            
            # 2. SEGUNDO: Atualiza nome do professor nas turmas RESTANTES
            cursor.execute(
                f"UPDATE turmas_professores SET professor = {placeholder} WHERE professor = {placeholder}",
                (nome_novo, nome_original)
            )
            
            # 3. TERCEIRO: Insere ou atualiza turmas selecionadas (com nome NOVO)
            for turma in turmas_finais:
                if DATABASE_URL:
                    cursor.execute("""
                        INSERT INTO turmas_professores (turma, professor) 
                        VALUES (%s, %s)
                        ON CONFLICT (turma) DO UPDATE SET professor = EXCLUDED.professor
                    """, (turma.strip(), nome_novo))
                else:
                    cursor.execute("""
                        INSERT OR REPLACE INTO turmas_professores (turma, professor) 
                        VALUES (?, ?)
                    """, (turma.strip(), nome_novo))
            
            conn.commit()
            
            # 4. Limpa cache após modificação
            st.cache_data.clear()
            
            return True
    except Exception as e:
        st.error(f"Erro no Banco de Dados: {e}")
        return False

#-------- AUSÊNCIAS --------
def insert_ausencia(tipo_doc, cpf, nome_aluno, turma_1, turma_2, ausencia_inicio, ausencia_fim) -> bool:
    """Inserir nova ausência com verificação de duplicata (considera turmas em qualquer ordem)"""
    turma_2 = turma_2 or ""
    data_ausencia = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # ========== VERIFICAÇÃO DE DUPLICATA ==========
            if DATABASE_URL:
                cursor.execute("""
                    SELECT COUNT(*) FROM ausencias 
                    WHERE cpf = %s 
                    AND ausencia_inicio = %s 
                    AND ausencia_fim = %s
                    AND (
                        (turma_1 = %s AND (turma_2 = %s OR turma_2 = ''))
                        OR 
                        (turma_1 = %s AND turma_2 = %s)
                        OR
                        (turma_2 = %s AND turma_1 = %s)
                    )
                """, (cpf, ausencia_inicio, ausencia_fim, 
                      turma_1, turma_2,
                      turma_2, turma_1,
                      turma_1, turma_2))
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM ausencias 
                    WHERE cpf = ? 
                    AND ausencia_inicio = ? 
                    AND ausencia_fim = ?
                    AND (
                        (turma_1 = ? AND (turma_2 = ? OR turma_2 = ''))
                        OR 
                        (turma_1 = ? AND turma_2 = ?)
                        OR
                        (turma_2 = ? AND turma_1 = ?)
                    )
                """, (cpf, ausencia_inicio, ausencia_fim, 
                      turma_1, turma_2,
                      turma_2, turma_1,
                      turma_1, turma_2))
            
            count = cursor.fetchone()[0]
            if count > 0:
                return False
            
            # ========== INSERÇÃO NORMAL ==========
            if DATABASE_URL:
                cursor.execute("""
                    INSERT INTO ausencias (
                        tipo_doc, cpf, nome_aluno, turma_1, turma_2,
                        ausencia_inicio, ausencia_fim, data_ausencia
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (tipo_doc, cpf, nome_aluno, turma_1, turma_2,
                      ausencia_inicio, ausencia_fim, data_ausencia))
            else:
                cursor.execute("""
                    INSERT INTO ausencias (
                        tipo_doc, cpf, nome_aluno, turma_1, turma_2,
                        ausencia_inicio, ausencia_fim, data_ausencia
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (tipo_doc, cpf, nome_aluno, turma_1, turma_2,
                      ausencia_inicio, ausencia_fim, data_ausencia))
            
            conn.commit()
        return True           
 
    except Exception:
        return False

def get_ausencias_recentes(limit=100):
    """Buscar ausências recentes"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM view_ausencias ORDER BY id DESC LIMIT %s" if DATABASE_URL
            else "SELECT * FROM view_ausencias ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return cursor.fetchall()

def search_ausencias(data_inicio, data_fim, cpf=None, nome=None, turma=None, professor=None):
    """Buscar ausências com filtros"""
    with get_connection() as conn:
        cursor = conn.cursor()
        placeholder = "%s" if DATABASE_URL else "?"

        query = f"""
            SELECT * FROM view_ausencias
            WHERE ausencia_inicio <= {placeholder}
            AND ausencia_fim >= {placeholder}
        """

        criterios = [data_fim, data_inicio]

        if nome:
            nome_normalizado = val.normalize_nome(nome)
            query += f" AND nome_aluno LIKE {placeholder}"
            criterios.append(f"%{nome_normalizado}%")

        if cpf:
            query += f" AND cpf = {placeholder}"
            criterios.append(cpf)

        if turma:
            query += f" AND (turma_1 = {placeholder} OR turma_2 = {placeholder})"
            criterios.extend([turma, turma])

        if professor:
            query += f" AND (professor_1 = {placeholder} OR professor_2 = {placeholder})"
            criterios.extend([professor, professor])

        query += " ORDER BY id DESC"

        cursor.execute(query, criterios)
        return cursor.fetchall()

def update_ausencia(id, tipo_doc, cpf, nome_aluno, turma_1, turma_2, ausencia_inicio, ausencia_fim):
    """Atualizar ausência existente"""
    with get_connection() as conn:
        cursor = conn.cursor()
        placeholder = "%s" if DATABASE_URL else "?"

        cursor.execute(f"""
            UPDATE ausencias
            SET
                tipo_doc = {placeholder},
                cpf = {placeholder},
                nome_aluno = {placeholder},
                turma_1 = {placeholder},
                turma_2 = {placeholder},
                ausencia_inicio = {placeholder},
                ausencia_fim = {placeholder}
            WHERE id = {placeholder}
        """, (tipo_doc, cpf, nome_aluno, turma_1, turma_2,
              ausencia_inicio, ausencia_fim, id))
        
        conn.commit()

def delete_ausencia(id):
    """Deletar ausência"""
    with get_connection() as conn:
        cursor = conn.cursor()
        placeholder = "%s" if DATABASE_URL else "?"
        cursor.execute(f"DELETE FROM ausencias WHERE id = {placeholder}", (id,))
        conn.commit()
        return cursor.rowcount > 0