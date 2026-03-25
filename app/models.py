from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# 📊 Modelo de Reportes
from datetime import datetime
import uuid

class Reporte(db.Model):
    __tablename__ = 'reportes'

    id = db.Column(db.Integer, primary_key=True)

    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    tipo_dano = db.Column(db.String(100))
    prioridad = db.Column(db.String(50))

    estado = db.Column(db.String(50), default='en revisión')

    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔗 Relación con usuario (opcional)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)

    # 👤 Invitado
    guest_token = db.Column(db.String(100), unique=True)

    # 📸 Imagen
    imagen = db.Column(db.String(200))


# 👤 Modelo de Usuarios
class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default='usuario')

    # 🔐 Encriptar contraseña
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # 🔍 Verificar contraseña
    def check_password(self, password):
        return check_password_hash(self.password, password)