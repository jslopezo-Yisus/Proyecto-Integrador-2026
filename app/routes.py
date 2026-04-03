from flask import Blueprint, render_template, request, redirect, session
from .models import Reporte, Usuario
from . import db
from werkzeug.utils import secure_filename
import os
from flask import current_app
import uuid

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

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['rol'] = user.rol

            if user.rol == 'admin':
                return redirect('/admin')
            else:
                return redirect('/')
        else:
            return "Credenciales incorrectas"

    return render_template('login.html')


# 📝 Registro
@main.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':

        user = Usuario(
            nombre=request.form['nombre'],
            correo=request.form['correo']
        )
        user.set_password(request.form['password'])

        db.session.add(user)
        db.session.commit()

        # 🔗 Vincular reportes de invitado
        token = request.form.get('guest_token')

        if token:
            reportes = Reporte.query.filter_by(guest_token=token).all()
            for r in reportes:
                r.user_id = user.id
                r.guest_token = None

            db.session.commit()

        return redirect('/login')

    return render_template('registro.html')


# 🔓 Logout
@main.route('/logout')
def logout():
    session.clear()
    return redirect('/')


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