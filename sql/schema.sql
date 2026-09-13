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