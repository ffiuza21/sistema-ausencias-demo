import psycopg2
import pandas as pd
from pathlib import Path

# ========== CONFIGURE AQUI ==========
DATABASE_URL = "postgresql://postgres.xxx:SUA_SENHA@aws-0-sa-east-1.pooler.supabase.com:6543/postgres"
# ====================================

def importar_dados():
    print("🔄 Conectando ao Supabase...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        print("✅ Conectado!")
        
        # ========== IMPORTAR AUSÊNCIAS ==========
        print("\n📊 Importando ausências...")
        df_ausencias = pd.read_csv("data/dados_demo_5000_ausencias.csv")
        
        total = len(df_ausencias)
        for idx, row in df_ausencias.iterrows():
            cur.execute("""
                INSERT INTO ausencias 
                (tipo_doc, cpf, nome_aluno, turma_1, turma_2, ausencia_inicio, ausencia_fim, data_ausencia)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['tipo_doc'],
                row['cpf'],
                row['nome_aluno'],
                row['turma_1'],
                row['turma_2'] if pd.notna(row['turma_2']) else None,
                row['ausencia_inicio'],
                row['ausencia_fim'],
                row['data_ausencia']
            ))
            
            # Commit a cada 500 registros
            if (idx + 1) % 500 == 0:
                conn.commit()
                print(f"   ⏳ {idx + 1}/{total} ausências importadas...")
        
        conn.commit()
        print(f"✅ {total} ausências importadas!\n")
        
        # ========== IMPORTAR PROFESSORES E TURMAS ==========
        print("👨‍🏫 Importando professores e turmas...")
        df_turmas = pd.read_csv("data/turmas_professores.csv")
        
        # Obter professores únicos
        professores = df_turmas[['cpf_professor', 'nome_professor']].drop_duplicates()
        
        for _, prof in professores.iterrows():
            cur.execute("""
                INSERT INTO professores (cpf, nome)
                VALUES (%s, %s)
                ON CONFLICT (cpf) DO NOTHING
            """, (prof['cpf_professor'], prof['nome_professor']))
        
        conn.commit()
        print(f"✅ {len(professores)} professores importados!")
        
        # Importar vínculos turmas-professores
        for _, row in df_turmas.iterrows():
            cur.execute("""
                INSERT INTO turmas_professores (turma, cpf_professor)
                VALUES (%s, %s)
            """, (row['turma'], row['cpf_professor']))
        
        conn.commit()
        print(f"✅ {len(df_turmas)} vínculos turma-professor importados!\n")
        
        # ========== ESTATÍSTICAS ==========
        print("=" * 60)
        print("📊 ESTATÍSTICAS DO BANCO:")
        print("=" * 60)
        
        cur.execute("SELECT COUNT(*) FROM ausencias")
        print(f"📋 Ausências: {cur.fetchone()[0]}")
        
        cur.execute("SELECT COUNT(*) FROM professores")
        print(f"👨‍🏫 Professores: {cur.fetchone()[0]}")
        
        cur.execute("SELECT COUNT(*) FROM turmas_professores")
        print(f"🏫 Vínculos turma-professor: {cur.fetchone()[0]}")
        
        cur.execute("SELECT COUNT(*) FROM usuarios")
        print(f"👤 Usuários: {cur.fetchone()[0]}")
        
        print("=" * 60)
        print("✅ IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 IMPORTAÇÃO DE DADOS DEMO PARA SUPABASE")
    print("=" * 60)
    print()
    
    # Verificar se arquivos existem
    if not Path("data/dados_demo_5000_ausencias.csv").exists():
        print("❌ Arquivo não encontrado: data/dados_demo_5000_ausencias.csv")
        print("   Execute este script na raiz do projeto!")
        exit(1)
    
    if not Path("data/turmas_professores.csv").exists():
        print("❌ Arquivo não encontrado: data/turmas_professores.csv")
        exit(1)
    
    # Confirmar
    print("⚠️  ATENÇÃO: Este script irá POPULAR o banco Supabase com dados demo.")
    print("   Certifique-se de ter configurado a DATABASE_URL corretamente!")
    print()
    resposta = input("Deseja continuar? (s/n): ")
    
    if resposta.lower() != 's':
        print("❌ Operação cancelada.")
        exit(0)
    
    print()
    importar_dados()
