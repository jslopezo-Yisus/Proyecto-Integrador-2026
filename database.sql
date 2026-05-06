DROP DATABASE IF EXISTS homefix;
CREATE DATABASE homefix;
USE homefix;

-- ============================================
-- 👤 TABLA USUARIOS
-- ============================================
CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'usuario', 'tecnico', 'entidad') NOT NULL,
    entidad_id INT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 🏢 TABLA ENTIDADES
-- ============================================
CREATE TABLE entidad (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) UNIQUE NOT NULL
);

-- ============================================
-- 🔗 RELACIÓN USUARIO -> ENTIDAD
-- ============================================
ALTER TABLE usuario
ADD CONSTRAINT fk_usuario_entidad
FOREIGN KEY (entidad_id) REFERENCES entidad(id)
ON DELETE SET NULL;

-- ============================================
-- 📄 TABLA REPORTES
-- ============================================
CREATE TABLE reporte (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT,
    direccion VARCHAR(255),
    prioridad ENUM('baja', 'media', 'alta') DEFAULT 'media',
    estado ENUM(
        'pendiente',
        'asignado a entidad',
        'asignado a tecnico',
        'iniciado',
        'en proceso',
        'resuelto'
    ) DEFAULT 'pendiente',

    user_id INT,
    tecnico_id INT NULL,
    entidad_id INT NULL,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 🧠 NUEVO CAMPO
    motivo_eliminacion TEXT NULL,

    -- 🔗 RELACIONES
    FOREIGN KEY (user_id) REFERENCES usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (tecnico_id) REFERENCES usuario(id) ON DELETE SET NULL,
    FOREIGN KEY (entidad_id) REFERENCES entidad(id) ON DELETE SET NULL
);

-- ============================================
-- 🔐 TOKENS PARA TECNICOS
-- ============================================
CREATE TABLE token_tecnico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token VARCHAR(255) UNIQUE NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 🔐 TOKENS PARA ENTIDADES
-- ============================================
CREATE TABLE token_entidad (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token VARCHAR(255) UNIQUE NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 📊 DATOS INICIALES (OPCIONAL PERO RECOMENDADO)
-- ============================================

-- 👑 ADMIN
INSERT INTO usuario (nombre, correo, password, rol)
VALUES ('Admin', 'admin@homefix.com', 'admin123', 'admin');

-- 🏢 ENTIDADES PREDEFINIDAS
INSERT INTO entidad (nombre) VALUES
('Mister Servicio'),
('Todero al instante'),
('EZRY Mantenimientos'),
('MICASAYMICARRO'),
('SOS Asistencia'),
('Vivvidero'),
('AYDA'),
('Jelpit'),
('Habitante'),
('EPM - Asistencia a tu puerta');

-- 👤 USUARIO DE PRUEBA
INSERT INTO usuario (nombre, correo, password, rol)
VALUES ('Usuario Demo', 'usuario@test.com', '123456', 'usuario');