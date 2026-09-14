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