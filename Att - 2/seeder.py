"""
seeder.py
Popula o banco de dados e verifica a "mágica" dos triggers.
"""

import psycopg2
import sys

# --- CONFIGURE SEUS DADOS DE ACESSO ---
# (Recomendado usar variáveis de ambiente, mas para a atividade,
# preencher aqui é mais direto)
DB_CONFIG = {
    "dbname": "seu_banco",     # Nome do seu banco de dados
    "user": "seu_usuario",     # Seu usuário do Postgres
    "password": "sua_senha", # Sua senha
    "host": "localhost",
    "port": "5432"
}
# ---------------------------------------

def seed_database():
    """
    Conecta ao DB, limpa tabelas, insere dados e verifica os triggers.
    """
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        print("Conectado ao banco de dados com sucesso.")

        # Limpa as tabelas para que o script seja re-executável
        print("Limpando tabelas (TRUNCATE)...")
        cur.execute("TRUNCATE TABLE funcionarios, departamentos, audit_log RESTART IDENTITY CASCADE;")

        # --- 1. Inserir Departamentos (sem triggers) ---
        print("Inserindo departamentos...")
        cur.execute(
            "INSERT INTO departamentos (nome_depto) VALUES (%s), (%s), (%s);",
            ('Engenharia de Software', 'Marketing Digital', 'Recursos Humanos')
        )

        # --- 2. Inserir Funcionários (OS TRIGGERS DISPARAM AQUI) ---
        print("Inserindo funcionários (triggers serão acionados)...")
        
        # Veja o email "Ana.Beatriz@EXAMPLE.COM" com letras maiúsculas
        sql_insert_func = """
        INSERT INTO funcionarios (nome_func, email, salario, id_depto) 
        VALUES (%s, %s, %s, %s) RETURNING id_func;
        """
        
        # Inserção 1
        cur.execute(sql_insert_func, ('Ana Beatriz', 'Ana.Beatriz@EXAMPLE.COM', 9000.00, 1))
        ana_id = cur.fetchone()[0]
        print(f"  -> Inserida Ana Beatriz (ID: {ana_id}). Email usado: 'Ana.Beatriz@EXAMPLE.COM'")

        # Inserção 2
        cur.execute(sql_insert_func, ('Bruno Costa', 'bruno.costa@example.com', 7500.00, 2))
        bruno_id = cur.fetchone()[0]
        print(f"  -> Inserido Bruno Costa (ID: {bruno_id}). Email usado: 'bruno.costa@example.com'")

        # Commit da transação para salvar tudo
        conn.commit()
        print("\n--- TRANSAÇÃO COMMITADA ---")

        # --- 3. VERIFICAR A MÁGICA ---
        print("\nVerificando resultados dos triggers:")

        # Verificação do Trigger 1 (Normalizar Email)
        print("\n[VERIFICAÇÃO TRIGGER 1: Normalização de Email]")
        cur.execute("SELECT email FROM funcionarios WHERE id_func = %s;", (ana_id,))
        email_result = cur.fetchone()[0]
        
        if email_result == 'ana.beatriz@example.com':
            print(f"  [SUCESSO] O email da Ana foi salvo como: '{email_result}' (minúsculo)")
        else:
            print(f"  [FALHA] O email da Ana é: '{email_result}' (esperava minúsculo)")

        # Verificação do Trigger 2 (Log de Auditoria)
        print("\n[VERIFICAÇÃO TRIGGER 2: Log de Auditoria]")
        cur.execute("SELECT evento, detalhes FROM audit_log ORDER BY id_log;")
        logs = cur.fetchall()
        
        if len(logs) == 2:
            print(f"  [SUCESSO] {len(logs)} registros encontrados no 'audit_log':")
            for i, log in enumerate(logs):
                print(f"    Log {i+1}: Evento='{log[0]}', Detalhes='{log[1]}'")
        else:
            print(f"  [FALHA] Esperávamos 2 logs, mas foram encontrados {len(logs)}.")

    except psycopg2.Error as e:
        print(f"\n[ERRO] Erro ao executar o script: {e}", file=sys.stderr)
        if conn:
            conn.rollback() # Desfaz a transação em caso de erro
    finally:
        # Fecha a conexão e o cursor
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("\nConexão com o banco de dados fechada.")

if __name__ == "__main__":
    seed_database()""