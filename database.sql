CREATE DATABASE proyecto_viviendas;
USE proyecto_viviendas;

-- Tabla usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    correo VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    rol ENUM('usuario', 'admin') DEFAULT 'usuario'
);

-- Tabla reportes
CREATE TABLE reportes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    correo VARCHAR(100),
    direccion VARCHAR(200),
    tipo_dano VARCHAR(100),
    prioridad VARCHAR(50),
    descripcion TEXT,
    imagen VARCHAR(255)
);