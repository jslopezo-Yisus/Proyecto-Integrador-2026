from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
from datetime import datetime

# USUARIOS
class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    rol = db.Column(db.String(20), nullable=False)  # admin, usuario, tecnico, entidad

    # Relación con entidad (solo técnicos)
    entidad_id = db.Column(db.Integer, db.ForeignKey('entidades.id'), nullable=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)



# ENTIDADES

class Entidad(db.Model):
    __tablename__ = 'entidades'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False, unique=True)

    # Relación con técnicos
    tecnicos = db.relationship('Usuario', backref='entidad', lazy=True)



# REPORTES

class Reporte(db.Model):

    __tablename__ = 'reportes'

    id = db.Column(db.Integer, primary_key=True)

    titulo = db.Column(db.String(100), nullable=False)

    descripcion = db.Column(db.Text, nullable=False)

    direccion = db.Column(db.String(200), nullable=False)

    prioridad = db.Column(db.String(50))

    estado = db.Column(
        db.String(50),
        default='Pendiente'
    )

    imagen = db.Column(db.String(200))

    motivo_eliminacion = db.Column(db.Text)

    latitud = db.Column(db.Float)

    longitud = db.Column(db.Float)

    fecha = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # 👤 Usuario creador
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id')
    )

    # 👷 Técnico asignado
    tecnico_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id')
    )

    # 🏢 Entidad asignada
    entidad_id = db.Column(
        db.Integer,
        db.ForeignKey('entidades.id')
    )

    # 🔗 RELACION USUARIO
    usuario = db.relationship(
        'Usuario',
        foreign_keys=[user_id]
    )

    # 🔗 RELACION TECNICO
    tecnico = db.relationship(
        'Usuario',
        foreign_keys=[tecnico_id]
    )


# TOKEN TÉCNICO

class TokenTecnico(db.Model):
    __tablename__ = 'tokens_tecnico'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True)
    usado = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)



# TOKEN ENTIDAD

class TokenEntidad(db.Model):
    __tablename__ = 'tokens_entidad'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True)
    usado = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

class HistorialReporte(db.Model):

    __tablename__ = 'historial_reporte'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    reporte_id = db.Column(
        db.Integer,
        db.ForeignKey('reportes.id'),
        nullable=False
    )

    accion = db.Column(
        db.String(200),
        nullable=False
    )

    detalle = db.Column(
        db.Text
    )

    fecha = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )