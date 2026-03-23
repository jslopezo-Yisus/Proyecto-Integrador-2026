from . import db

class Reporte(db.Model):
    __tablename__ = 'reportes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    correo = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    tipo_dano = db.Column(db.String(100))
    prioridad = db.Column(db.String(50))
    descripcion = db.Column(db.Text)

    def __repr__(self):
        return f"<Reporte {self.nombre}>"