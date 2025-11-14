/*
 * scheme.sql
 * Define o esquema do banco de dados e os triggers de INSERT.
 */

-- Limpa o ambiente (opcional, cuidado ao usar em produção)
DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS funcionarios;
DROP TABLE IF EXISTS departamentos;
DROP FUNCTION IF EXISTS fn_normalizar_email();
DROP FUNCTION IF EXISTS fn_log_nova_contratacao();

---
-- 1. DEFINIÇÃO DAS TABELAS
---

CREATE TABLE departamentos (
    id_depto SERIAL PRIMARY KEY,
    nome_depto VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE funcionarios (
    id_func SERIAL PRIMARY KEY,
    nome_func VARCHAR(150) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    salario NUMERIC(10, 2) NOT NULL,
    data_contratacao DATE NOT NULL DEFAULT CURRENT_DATE,
    id_depto INT REFERENCES departamentos(id_depto)
);

-- Tabela para auditoria, será populada pelo Trigger 2
CREATE TABLE audit_log (
    id_log SERIAL PRIMARY KEY,
    evento VARCHAR(50) NOT NULL,
    tabela_afetada VARCHAR(50) NOT NULL,
    id_registro_afetado INT,
    timestamp_evento TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    detalhes TEXT
);

---
-- 2. TRIGGER 1: NORMALIZAR EMAIL (BEFORE INSERT)
---

-- Primeiro, criamos a FUNÇÃO (Procedure) que será executada
CREATE OR REPLACE FUNCTION fn_normalizar_email()
RETURNS TRIGGER AS $$
BEGIN
    -- 'NEW' é uma variável especial que contém a linha a ser inserida.
    -- Modificamos o campo 'email' da nova linha.
    NEW.email = lower(NEW.email);
    
    -- Retornamos a linha modificada para que o INSERT possa continuar.
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Agora, criamos o TRIGGER que vincula a função à tabela.
CREATE TRIGGER trg_before_insert_func_email
    BEFORE INSERT ON funcionarios -- Dispara ANTES do insert
    FOR EACH ROW                 -- Para cada linha individual sendo inserida
    EXECUTE FUNCTION fn_normalizar_email();


---
-- 3. TRIGGER 2: LOG DE AUDITORIA (AFTER INSERT)
---

-- Criamos a segunda FUNÇÃO
CREATE OR REPLACE FUNCTION fn_log_nova_contratacao()
RETURNS TRIGGER AS $$
BEGIN
    -- Insere um registro na tabela de log.
    -- 'NEW.id_func' já está disponível pois o trigger é AFTER INSERT
    -- (o SERIAL já gerou o ID).
    INSERT INTO audit_log (evento, tabela_afetada, id_registro_afetado, detalhes)
    VALUES (
        'NOVA CONTRATACAO',
        'funcionarios',
        NEW.id_func,
        'Funcionário ' || NEW.nome_func || ' (ID: ' || NEW.id_func || ') foi contratado.'
    );
    
    -- Em um trigger AFTER, o valor de retorno é geralmente ignorado.
    RETURN NEW; 
END;
$$ LANGUAGE plpgsql;

-- Criamos o segundo TRIGGER
CREATE TRIGGER trg_after_insert_func_log
    AFTER INSERT ON funcionarios -- Dispara DEPOIS do insert
    FOR EACH ROW
    EXECUTE FUNCTION fn_log_nova_contratacao();