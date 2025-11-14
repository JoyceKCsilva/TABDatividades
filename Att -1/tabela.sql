-- Departamentos da empresa
CREATE TABLE departamentos (
    id_depto SERIAL PRIMARY KEY,
    nome_depto VARCHAR(100) NOT NULL UNIQUE,
    localizacao VARCHAR(50)
);

-- Funcionários, com auto-relacionamento para hierarquia (gerente)
CREATE TABLE funcionarios (
    id_func SERIAL PRIMARY KEY,
    nome_func VARCHAR(150) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    salario NUMERIC(10, 2) NOT NULL,
    data_contratacao DATE NOT NULL,
    id_depto INT REFERENCES departamentos(id_depto),
    id_gerente INT REFERENCES funcionarios(id_func) -- Auto-relacionamento
);

-- Tabela de arquivo para funcionários demitidos (para usar UNION)
CREATE TABLE funcionarios_archive (
    -- Mesma estrutura do funcionário
    id_func INT PRIMARY KEY,
    nome_func VARCHAR(150) NOT NULL,
    email VARCHAR(100) NOT NULL,
    salario NUMERIC(10, 2) NOT NULL,
    data_contratacao DATE NOT NULL,
    id_depto INT,
    id_gerente INT
);

-- Projetos da empresa
CREATE TABLE projetos (
    id_proj SERIAL PRIMARY KEY,
    nome_proj VARCHAR(200) NOT NULL,
    status_proj VARCHAR(20) DEFAULT 'Ativo' -- Ex: 'Ativo', 'Concluído', 'Pausado'
);

-- Tabela de ligação Muitos-para-Muitos (Funcionários <-> Projetos)
CREATE TABLE atribuicoes_proj (
    id_atribuicao SERIAL PRIMARY KEY,
    id_func INT NOT NULL REFERENCES funcionarios(id_func),
    id_proj INT NOT NULL REFERENCES projetos(id_proj),
    horas_semanais INT NOT NULL,
    UNIQUE(id_func, id_proj)
);