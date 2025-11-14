-- [WITH RECURSIVE] Define um CTE recursivo para mapear a hierarquia organizacional
WITH RECURSIVE hierarquia_org (id_func, nome_func, id_gerente, nivel) AS (
    -- Membro âncora: seleciona os "tops" (CEOs, diretores) que não têm gerente
    SELECT 
        id_func, nome_func, id_gerente, 1 AS nivel
    FROM funcionarios
    WHERE id_gerente IS NULL

    UNION ALL

    -- Membro recursivo: junta funcionários com seus gerentes
    SELECT 
        f.id_func, f.nome_func, f.id_gerente, ho.nivel + 1
    FROM funcionarios f
    JOIN hierarquia_org ho ON f.id_gerente = ho.id_func
),

-- [WITH] Define um segundo CTE (não recursivo) para agregar dados por departamento
sumario_deptos AS (
    SELECT 
        id_depto,
        AVG(salario) AS media_salario_depto,
        COUNT(*) AS total_func_depto
    FROM funcionarios
    -- [GROUP BY] Agrupa pelo departamento
    GROUP BY id_depto
    -- [HAVING] Filtra os grupos, queremos apenas departamentos com mais de 3 pessoas
    HAVING COUNT(*) > 3
)

-- [SELECT] Cláusula principal
SELECT 
    -- [DISTINCT ON] Pega apenas a *primeira* linha por departamento (definido no ORDER BY)
    DISTINCT ON (d.nome_depto) 
    f.nome_func AS nome_funcionario,
    f.salario,
    d.nome_depto,
    d.localizacao,
    sd.media_salario_depto, -- Vindo do CTE 'sumario_deptos'
    ho.nivel AS nivel_hierarquico, -- Vindo do CTE 'hierarquia_org'
    
    -- [WINDOW] Uma função de janela para rankear salários *dentro* da localização
    RANK() OVER (
        PARTITION BY d.localizacao 
        ORDER BY f.salario DESC
    ) AS rank_salario_localizacao,
    
    -- Sub-query na lista de SELECT
    (SELECT COUNT(*) FROM atribuicoes_proj ap WHERE ap.id_func = f.id_func) AS total_projetos_ativos,
    
    -- [LATERAL] Pega o nome do projeto com mais horas para este funcionário
    proj_mais_horas.nome_proj AS projeto_principal

-- [FROM] A fonte principal é uma sub-query que une duas tabelas
FROM (
    -- [UNION] Combina funcionários ativos e arquivados
    SELECT * FROM funcionarios
    UNION
    SELECT * FROM funcionarios_archive
) AS f

-- [JOIN] Junta com departamentos
JOIN departamentos d ON f.id_depto = d.id_depto

-- [JOIN] Junta com o CTE de sumários (apenas deptos com > 3 func)
JOIN sumario_deptos sd ON d.id_depto = sd.id_depto

-- [LEFT JOIN] Junta com a hierarquia (LEFT caso algum func tenha sido excluído da hierarquia)
LEFT JOIN hierarquia_org ho ON f.id_func = ho.id_func

-- [CROSS JOIN LATERAL] Um join avançado. Para cada funcionário 'f',
-- executa a sub-query que busca seu projeto de maior carga horária.
CROSS JOIN LATERAL (
    SELECT p.nome_proj
    FROM atribuicoes_proj apj
    JOIN projetos p ON apj.id_proj = p.id_proj
    WHERE apj.id_func = f.id_func AND p.status_proj = 'Ativo'
    ORDER BY apj.horas_semanais DESC
    LIMIT 1
) AS proj_mais_horas

-- [WHERE] Filtro de linha (antes do agrupamento/window)
WHERE 
    f.data_contratacao > '2019-01-01'
    AND d.localizacao IN ('Sede Principal', 'Filial SP')
    -- [Sub-query com EXCEPT] Seleciona funcionários que NÃO estão em projetos pausados
    AND f.id_func NOT IN (
        SELECT ap.id_func
        FROM atribuicoes_proj ap
        JOIN projetos p ON ap.id_proj = p.id_proj
        WHERE p.status_proj = 'Pausado'
        -- [EXCEPT] (só para complexidade) exceto se for o projeto ID 10
        EXCEPT
        SELECT ap.id_func
        FROM atribuicoes_proj ap
        WHERE ap.id_proj = 10
    )

-- [ORDER BY] Essencial para o DISTINCT ON, e depois para o resultado final
ORDER BY 
    d.nome_depto, -- [DISTINCT ON] requer que isso venha primeiro
    f.salario DESC, -- Pega o funcionário de MAIOR salário de cada depto
    f.nome_func -- Critério de desempate

-- [LIMIT] Paginação: Pega os 5 primeiros departamentos
LIMIT 5
-- [OFFSET] Pula os 2 primeiros
OFFSET 2

-- [FOR UPDATE] Cláusula de travamento: Trava as linhas selecionadas de 'f' e 'd'
-- Isso impede que outra transação mude o salário ou o depto desses funcionários
-- até que nossa transação termine (COMMIT/ROLLBACK).
FOR UPDATE OF f, d;