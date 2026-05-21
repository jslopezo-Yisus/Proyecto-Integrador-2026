from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid


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

    
    # ID PRINCIPAL
    

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    
    # INFORMACIÓN GENERAL
    

    titulo = db.Column(
        db.String(100),
        nullable=False
    )

    descripcion = db.Column(
        db.Text,
        nullable=False
    )

    direccion = db.Column(
        db.String(200),
        nullable=False
    )

    tipo_dano = db.Column(
        db.String(100)
    )

    imagen = db.Column(
        db.String(200)
    )

    motivo_eliminacion = db.Column(
        db.Text
    )

    
    # GEOLOCALIZACIÓN
    

    latitud = db.Column(
        db.Float
    )

    longitud = db.Column(
        db.Float
    )

    
    # PRIORIDAD Y ESTADO
    

    prioridad = db.Column(
        db.String(50),
        default='Media'
    )

    estado = db.Column(
        db.String(50),
        default='Pendiente'
    )

    
    # FECHAS
    

    fecha_creacion = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    fecha_actualizacion = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    fecha_solucion = db.Column(
        db.DateTime
    )

    
    # SATISFACCIÓN
    

    calificacion = db.Column(
        db.Integer
    )

    comentario_calificacion = db.Column(
        db.Text
    )

    
    # RELACIONES
    

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

    
    # RELACIONES SQLALCHEMY
    

    usuario = db.relationship(
        'Usuario',
        foreign_keys=[user_id]
    )


    tecnico = db.relationship(
        'Usuario',
        foreign_keys=[tecnico_id]
    )

    
    # SERIALIZADOR API
    

    def to_dict(self):

        return {

            "id": self.id,

            "titulo": self.titulo,

            "descripcion": self.descripcion,

            "direccion": self.direccion,

            "tipo_dano": self.tipo_dano,

            "prioridad": self.prioridad,

            "estado": self.estado,

            "latitud": self.latitud,

            "longitud": self.longitud,

            "fecha_creacion": (
                self.fecha_creacion.strftime('%Y-%m-%d %H:%M')
                if self.fecha_creacion else None
            ),

            "fecha_actualizacion": (
                self.fecha_actualizacion.strftime('%Y-%m-%d %H:%M')
                if self.fecha_actualizacion else None
            ),

            "fecha_solucion": (
                self.fecha_solucion.strftime('%Y-%m-%d %H:%M')
                if self.fecha_solucion else None
            ),

            "calificacion": self.calificacion,

            "comentario_calificacion":
                self.comentario_calificacion,

            "user_id": self.user_id,

            "tecnico_id": self.tecnico_id,

            "entidad_id": self.entidad_id
        }


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

    reporte = db.relationship(
        'Reporte',
        backref='historiales'
    )