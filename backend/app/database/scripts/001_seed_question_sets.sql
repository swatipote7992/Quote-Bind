-- Seed product_catalog, question_catalog, and one QuestionSet per product
-- (linked to a subset of question_catalog via question_array).
--
-- product_id and question_id are SERIAL, so these rely on insertion order
-- to land on the ids referenced below (product_catalog: 1=Audi, 2=BMW,
-- 3=Mercedes, 4=Honda; question_catalog: 1=18-years-old, 2=UK resident,
-- 3=UK citizen, 4=driving license). Run against an empty product_catalog /
-- question_catalog, or adjust the ids below to match existing rows.

INSERT INTO product_catalog (product_label, is_active) VALUES
('Audi', true),
('BMW', true),
('Mercedes', true),
('Honda', true);

INSERT INTO question_catalog (question_label, default_answer) VALUES
('Are you 18 years old?', 'Yes'),
('Are you UK resident?', 'Yes'),
('Are you UK Citizen?', 'Yes'),
('Do you hold a valid UK driving license?', 'Yes');

-- Audi (product_id = 1): all questions
INSERT INTO question_set (id, label, product_id)
VALUES ('QSAU', 'Audi Question Set', 1);

INSERT INTO question_array (question_set_id, question_id) VALUES
('QSAU', 1),
('QSAU', 2),
('QSAU', 3),
('QSAU', 4);

-- BMW (product_id = 2): 18-years-old, UK resident, driving license
INSERT INTO question_set (id, label, product_id)
VALUES ('QSBM', 'BMW Question Set', 2);

INSERT INTO question_array (question_set_id, question_id) VALUES
('QSBM', 1),
('QSBM', 2),
('QSBM', 4);

-- Mercedes (product_id = 3): 18-years-old, driving license
INSERT INTO question_set (id, label, product_id)
VALUES ('QSME', 'Mercedes Question Set', 3);

INSERT INTO question_array (question_set_id, question_id) VALUES
('QSME', 1),
('QSME', 4);

-- Honda (product_id = 4): driving license only
INSERT INTO question_set (id, label, product_id)
VALUES ('QSHO', 'Honda Question Set', 4);

INSERT INTO question_array (question_set_id, question_id) VALUES
('QSHO', 4);
