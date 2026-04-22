from flask import Blueprint, render_template, request, redirect, session, flash
from .models import Reporte, Usuario, TokenTecnico
from . import db
from werkzeug.utils import secure_filename
import os

import uuid


main = Blueprint('main', __name__)

# 🏠 Inicio
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



        nuevo_reporte = Reporte(
            titulo=request.form['titulo'],
            descripcion=request.form['descripcion'],
            direccion=request.form['direccion'],
            tipo_dano=request.form['tipo_dano'],
            prioridad=request.form['prioridad'],
            imagen=nombre_imagen,
            user_id=session.get('user_id')
        )

        db.session.add(nuevo_reporte)
        db.session.commit()

        return render_template('confirmacion.html', report_id=nuevo_reporte.id)

    return render_template('reportar.html')


# 🔐 LOGIN
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        correo = request.form.get('correo')
        password = request.form.get('password')
        rol = request.form.get('rol')  # 👈 importante

        user = Usuario.query.filter_by(correo=correo).first()

        if user and user.check_password(password):

            # 🔥 VALIDAR ROL CORRECTO
            if user.rol != rol:
                return "Rol incorrecto"

            session['user_id'] = user.id
            session['rol'] = user.rol

            if user.rol == 'admin':
                return redirect('/admin')
            elif user.rol == 'tecnico':
                return redirect('/tecnico')
            else:
                return redirect('/dashboard')

        else:
            return "Credenciales incorrectas"

    return render_template('login.html')


# 📝 REGISTRO
@main.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':

        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        password = request.form.get('password')
        rol = request.form.get('rol')
        token = request.form.get('token')

        # 🔍 VALIDAR SI YA EXISTE
        if Usuario.query.filter_by(correo=correo).first():
            return "El usuario ya existe"

        # 🔐 VALIDAR TOKEN PARA TECNICO (DINÁMICO)
        if rol == 'tecnico':
            token_db = TokenTecnico.query.filter_by(token=token).first()

            if not token_db:
                return "Token inválido"

            # 🔥 eliminar token después de usarlo
            db.session.delete(token_db)

        # 👤 CREAR USUARIO
        user = Usuario(
            nombre=nombre,
            correo=correo,
            rol=rol
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # 🔥 LOGIN AUTOMÁTICO
        session['user_id'] = user.id
        session['rol'] = user.rol

        # 🔄 REDIRECCIÓN SEGÚN ROL
        if rol == 'admin':
            return redirect('/admin')
        elif rol == 'tecnico':
            return redirect('/tecnico')
        else:
            return redirect('/dashboard')

    return render_template('registro.html')


# 🔓 Logout
@main.route('/logout')
def logout():
    session.clear()

    return redirect('/login')


# 👤 Dashboard usuario
@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    reportes = Reporte.query.filter_by(user_id=session['user_id']).all()
    return render_template('dashboard.html', reportes=reportes)


# 👑 Admin
@main.route('/admin')
def admin():
    if session.get('rol') != 'admin':
        return redirect('/login')

    reportes = Reporte.query.all()
    tecnicos = Usuario.query.filter_by(rol='tecnico').all()

    return render_template('admin.html', reportes=reportes, tecnicos=tecnicos)


# 👷 Técnico
@main.route('/tecnico')
def tecnico():
    # 🔐 Verificar si hay sesión activa
    if 'user_id' not in session:
        return redirect('/login')

    # 🔐 Verificar rol correcto
    if session.get('rol') != 'tecnico':
        return redirect('/')

    # 📊 Obtener reportes asignados
    reportes = Reporte.query.filter_by(tecnico_id=session['user_id']).all()

    return render_template('tecnico.html', reportes=reportes)


# 📊 Ver todos (opcional)
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


# 🧠 Asignar técnico (ADMIN)
@main.route('/asignar/<int:id>', methods=['POST'])
def asignar(id):
    if session.get('rol') != 'admin':
        return redirect('/')

    reporte = Reporte.query.get_or_404(id)

    reporte.tecnico_id = request.form['tecnico_id']
    reporte.estado = 'asignado'

    db.session.commit()

    return redirect('/admin')


# 🔐 Generar token (ADMIN)
@main.route('/generar-token')
def generar_token():

    if session.get('rol') != 'admin':

        return redirect('/login')

    nuevo_token = str(uuid.uuid4())

    token_db = TokenTecnico(token=nuevo_token)

    db.session.add(token_db)
    db.session.commit()

    return f"Token generado: {nuevo_token}"

from flask import send_from_directory
import os

@main.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(os.getcwd(), 'app', 'Static', 'img'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )