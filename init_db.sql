-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS lara_bs;

-- Crear usuario con permisos desde cualquier host (%)
CREATE USER IF NOT EXISTS 'daniel'@'%' IDENTIFIED BY 'daniel123';
GRANT ALL PRIVILEGES ON lara_bs.* TO 'daniel'@'%';
FLUSH PRIVILEGES;

-- Seleccionar base de datos
USE lara_bs;

-- Crear tabla si no existe
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL
);

-- Insertar usuario si no estaba
INSERT INTO users (name, email)
SELECT * FROM (SELECT 'Daniel Lara', 'daniel@example.com') AS tmp
WHERE NOT EXISTS (
    SELECT email FROM users WHERE email = 'daniel@example.com'
)
LIMIT 1;
