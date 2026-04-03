CREATE DATABASE proyecto_viviendas;
USE proyecto_viviendas;


CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    correo VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    rol ENUM('usuario', 'admin') DEFAULT 'usuario'
);


CREATE TABLE reportes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    tipo_dano VARCHAR(100),
    prioridad VARCHAR(50),
    estado VARCHAR(50) DEFAULT 'en revisión',
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INT NULL,
    guest_token VARCHAR(100) UNIQUE,
    imagen VARCHAR(255),

    FOREIGN KEY (user_id) REFERENCES usuarios(id)
);