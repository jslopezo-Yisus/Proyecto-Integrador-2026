from flask import Blueprint, render_template, request, redirect
from .models import Reporte
from . import db

main = Blueprint('main', __name__)

# Ruta principal
@main.route('/')
def index():
    return render_template('index.html')


# Ruta formulario
@main.route('/reportar', methods=['GET', 'POST'])
def reportar():
    if request.method == 'POST':
        nuevo_reporte = Reporte(
            nombre=request.form['nombre'],
            correo=request.form['correo'],
            direccion=request.form['direccion'],
            tipo_dano=request.form['tipo_dano'],
            prioridad=request.form['prioridad'],
            descripcion=request.form['descripcion']
        )

        db.session.add(nuevo_reporte)
        db.session.commit()

        return redirect('/')

    return render_template('reportar.html')