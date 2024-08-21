# biblioteca
Banco de dados

-- Criando o schema da biblioteca
CREATE SCHEMA biblioteca;

-- Selecionando o schema para uso
USE biblioteca;

-- Criando a tabela de empréstimos
CREATE TABLE emprestimos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(20) NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    autor VARCHAR(255) NOT NULL,
    usuario VARCHAR(255) NOT NULL,
    data_emprestimo DATE NOT NULL,
    data_devolucao DATE
);

-- Criando a tabela de usuários
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);
