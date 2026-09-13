INSERT INTO curso (codigo, nome) VALUES
('61385', 'Análise e Desenvolvimento de Sistemas'),
('61927', 'Engenharia de Software');

INSERT INTO matriz (curso_id, codigo)
SELECT id, '2024/1' FROM curso WHERE codigo = '61385';

INSERT INTO matriz (curso_id, codigo)
SELECT id, '2024/2' FROM curso WHERE codigo = '61385';

INSERT INTO matriz (curso_id, codigo)
SELECT id, '2025/1' FROM curso WHERE codigo = '61927';

INSERT INTO matriz (curso_id, codigo)
SELECT id, '2025/2' FROM curso WHERE codigo = '61927';