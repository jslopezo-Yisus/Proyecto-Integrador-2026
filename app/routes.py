from flask import Blueprint, render_template, request, redirect, session
from .models import Reporte, Usuario
from . import db
from werkzeug.utils import secure_filename
import os
from flask import current_app
import uuid
from flask import render_template
from .models import Reporte
from flask import render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

# 🏠 Ruta principal
@main.route('/')
def index():
    return render_template('index.html')


# 📄 Crear reporte


@main.route('/reportar', methods=['GET', 'POST'])
def reportar():
    if request.method == 'POST':
        
        imagen = request.files.get('imagen')
        nombre_imagen = None

        if imagen and imagen.filename != '':
            nombre_imagen = secure_filename(imagen.filename)
            ruta = os.path.join('app/static/img', nombre_imagen)
            imagen.save(ruta)

        guest_token = str(uuid.uuid4())

        nuevo_reporte = Reporte(
            titulo=request.form['titulo'],
            descripcion=request.form['descripcion'],
            direccion=request.form['direccion'],
            tipo_dano=request.form['tipo_dano'],
            prioridad=request.form['prioridad'],
            imagen=nombre_imagen,
            guest_token=guest_token
        )

        db.session.add(nuevo_reporte)
        db.session.commit()

        return render_template(
            'confirmacion.html',
            report_id=nuevo_reporte.id
        )

    return render_template('reportar.html')


# 🔐 Login
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']

        user = Usuario.query.filter_by(correo=correo).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Bienvenido 👋', 'success')
            return redirect('/reportes')
        else:
            flash('Credenciales incorrectas ❌', 'danger')

    return render_template('login.html')


# 📝 Registro
@main.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = generate_password_hash(request.form['password'])

        nuevo_usuario = Usuario(
            nombre=nombre,
            correo=correo,
            password=password
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        flash('Cuenta creada correctamente 🎉', 'success')
        return redirect('/login')

    return render_template('registro.html')


# 🔓 Logout
@main.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'info')
    return redirect('/login')


# 📊 Listar reportes
@main.route('/reportes')
def reportes():
    if 'user_id' not in session:
        return redirect('/login')

    reportes = Reporte.query.all()
    return render_template('reportes.html', reportes=reportes)


# 🔍 Detalle
@main.route('/detalle/<int:id>')
def detalle(id):
    if 'user_id' not in session:
        return redirect('/login')

    reporte = Reporte.query.get_or_404(id)
    return render_template('detalle.html', reporte=reporte)


# ✏️ Editar
@main.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'user_id' not in session:
        return redirect('/login')

    reporte = Reporte.query.get_or_404(id)

    if request.method == 'POST':
        reporte.nombre = request.form['nombre']
        reporte.descripcion = request.form['descripcion']

        db.session.commit()
        return redirect('/reportes')

    return render_template('editar.html', reporte=reporte)


# 🗑️ Eliminar (MEJORADO)
@main.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    if 'user_id' not in session:
        return redirect('/login')

    reporte = Reporte.query.get_or_404(id)

    db.session.delete(reporte)
    db.session.commit()

    return redirect('/reportes')


# 👑 Panel Admin
@main.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('rol') != 'admin':
        return redirect('/')

    reportes = Reporte.query.all()
    return render_template('reportes.html', reportes=reportes)

@main.route('/mis-reportes')
def mis_reportes():
    if 'user_id' not in session:
        return redirect('/login')

    reportes = Reporte.query.filter_by(user_id=session['user_id']).all()

    return render_template('mis_reportes.html', reportes=reportes)