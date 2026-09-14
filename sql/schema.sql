CREATE TABLE curso (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    nome VARCHAR(150) NOT NULL
);

CREATE TABLE matriz (
    id SERIAL PRIMARY KEY,
    curso_id INTEGER NOT NULL REFERENCES curso(id),
    codigo VARCHAR(10) NOT NULL,
    UNIQUE (curso_id, codigo)
);

CREATE TABLE analise (
    id SERIAL PRIMARY KEY,
    nome_aluno VARCHAR(150) NOT NULL,
    ra VARCHAR(30),
    semestre_ano VARCHAR(20),
    situacao VARCHAR(100),
    procedencia VARCHAR(150),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE matriz
ADD CONSTRAINT uq_matriz_curso_id UNIQUE (curso_id, id);

ALTER TABLE analise
ADD COLUMN curso_id INTEGER,
ADD COLUMN matriz_id INTEGER;

ALTER TABLE analise
ADD CONSTRAINT fk_analise_curso
FOREIGN KEY (curso_id)
REFERENCES curso(id);

ALTER TABLE analise
ADD CONSTRAINT fk_analise_matriz_do_curso
FOREIGN KEY (curso_id, matriz_id)
REFERENCES matriz(curso_id, id);

ALTER TABLE analise
ADD CONSTRAINT ck_analise_curso_matriz
CHECK (
    (curso_id IS NULL AND matriz_id IS NULL)
    OR
    (curso_id IS NOT NULL AND matriz_id IS NOT NULL)
);