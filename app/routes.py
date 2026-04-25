from flask import Blueprint, render_template, request, redirect, session, flash
from .models import Reporte, Usuario, TokenTecnico, TokenEntidad, Entidad
from . import db


import uuid


main = Blueprint('main', __name__)

# =========================
# 🏠 INDEX
# =========================
@main.route('/')
def index():
    return render_template('index.html')


# =========================
# 🔐 LOGIN
# =========================
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        correo = request.form.get('correo')
        password = request.form.get('password')
        rol = request.form.get('rol')

        user = Usuario.query.filter_by(correo=correo).first()

        if not user or not user.check_password(password) or user.rol != rol:
            flash('Credenciales incorrectas', 'danger')
            return redirect('/login')

        session['user_id'] = user.id
        session['rol'] = user.rol

        if rol == 'admin':
            return redirect('/admin')
        elif rol == 'tecnico':
            return redirect('/tecnico')
        elif rol == 'entidad':
            return redirect('/entidad')
        else:
            return redirect('/dashboard')
    return render_template('login.html')


# =========================
# 📝 REGISTRO
# =========================
@main.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':

        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        password = request.form.get('password')
        rol = request.form.get('rol')
        token = request.form.get('token')
        entidad_nombre = request.form.get('entidad')

        # ❌ VALIDAR CORREO
        if Usuario.query.filter_by(correo=correo).first():
            flash('El correo ya está registrado', 'danger')
            return redirect('/registro')

        # =========================
        # 🔐 TECNICO
        # =========================
        if rol == 'tecnico':
            token_db = TokenTecnico.query.filter_by(token=token, usado=False).first()

            if not token_db:
                flash('Token de técnico inválido', 'danger')
                return redirect('/registro')

            entidad = Entidad.query.filter_by(nombre=entidad_nombre).first()

            if not entidad:
                flash('Entidad no válida', 'danger')
                return redirect('/registro')

            user = Usuario(
                nombre=nombre,
                correo=correo,
                rol='tecnico',
                entidad_id=entidad.id
            )

            token_db.usado = True

        # =========================
        # 🏢 ENTIDAD
        # =========================
        elif rol == 'entidad':
            token_db = TokenEntidad.query.filter_by(token=token, usado=False).first()

            if not token_db:
                flash('Token de entidad inválido', 'danger')
                return redirect('/registro')

            entidad = Entidad.query.filter_by(nombre=entidad_nombre).first()

            if not entidad:
                entidad = Entidad(nombre=entidad_nombre)
                db.session.add(entidad)

            user = Usuario(
                nombre=nombre,
                correo=correo,
                rol='entidad'
            )

            token_db.usado = True

        # =========================
        # 👤 USUARIO NORMAL
        # =========================
        else:
            user = Usuario(
                nombre=nombre,
                correo=correo,
                rol='usuario'
            )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()


        session['user_id'] = user.id
        session['rol'] = user.rol

        return redirect('/dashboard')

    return render_template('registro.html')


# =========================
# 📊 ADMIN
# =========================
@main.route('/admin')
def admin():
    if session.get('rol') != 'admin':
        return redirect('/login')

    reportes = Reporte.query.all()
    entidades = Entidad.query.all()

    return render_template('admin.html', reportes=reportes, entidades=entidades)


# =========================
# 🔐 GENERAR TOKEN TECNICO
# =========================
@main.route('/generar-token-tecnico')
def generar_token_tecnico():
    if session.get('rol') != 'admin':
        return redirect('/login')

    token = str(uuid.uuid4())
    nuevo = TokenTecnico(token=token)

    db.session.add(nuevo)
    db.session.commit()

    flash(f'Token técnico generado: {token}', 'success')
    return redirect('/admin')


# =========================
# 🔐 GENERAR TOKEN ENTIDAD
# =========================
@main.route('/generar-token-entidad')
def generar_token_entidad():
    if session.get('rol') != 'admin':
        return redirect('/login')

    token = str(uuid.uuid4())
    nuevo = TokenEntidad(token=token)

    db.session.add(nuevo)
    db.session.commit()

    flash(f'Token entidad generado: {token}', 'success')
    return redirect('/admin')


# =========================
# 🏢 PANEL ENTIDAD
# =========================
@main.route('/entidad')
def entidad():
    if session.get('rol') != 'entidad':
        return redirect('/login')

    # 👤 Usuario actual
    user_id = session.get('user_id')
    usuario = Usuario.query.get(user_id)

    # 🏢 Entidad del usuario
    entidad_id = usuario.entidad_id

    # 📊 Reportes SOLO de esa entidad
    reportes = Reporte.query.filter_by(entidad_id=entidad_id).all()

    # 👷 Técnicos SOLO de esa entidad
    tecnicos = Usuario.query.filter_by(rol='tecnico', entidad_id=entidad_id).all()

    return render_template('entidad.html', reportes=reportes, tecnicos=tecnicos)


# =========================
# 👷 PANEL TECNICO
# =========================
@main.route('/tecnico')
def tecnico():

    if session.get('rol') != 'tecnico':
        return redirect('/login')
    reportes = Reporte.query.filter_by(tecnico_id=session['user_id']).all()

    return render_template('tecnico.html', reportes=reportes)

@main.route('/editar-tecnico/<int:id>', methods=['POST'])
def editar_tecnico(id):
    if session.get('rol') != 'tecnico':
        return redirect('/login')

    reporte = Reporte.query.get_or_404(id)

    reporte.estado = request.form.get('estado')
    reporte.descripcion = request.form.get('descripcion')

    db.session.commit()

    flash('Reporte actualizado correctamente', 'success')
    return redirect('/tecnico')

@main.route('/eliminar-reporte/<int:id>', methods=['POST'])
def eliminar_reporte(id):
    if session.get('rol') != 'tecnico':
        return redirect('/login')

    reporte = Reporte.query.get_or_404(id)

    motivo = request.form.get('motivo')
    reporte.motivo_eliminacion = motivo

    db.session.delete(reporte)
    db.session.commit()

    flash('Reporte eliminado correctamente', 'warning')
    return redirect('/tecnico')


# =========================
# 👤 DASHBOARD USUARIO
# =========================
@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    reportes = Reporte.query.filter_by(user_id=session['user_id']).all()

    return render_template('dashboard.html', reportes=reportes)


# =========================
# 📄 CREAR REPORTE
# =========================
@main.route('/reportar', methods=['GET', 'POST'])
def reportar():
    if request.method == 'POST':

        nuevo = Reporte(
            titulo=request.form['titulo'],
            descripcion=request.form['descripcion'],
            direccion=request.form['direccion'],
            prioridad=request.form['prioridad'],
            user_id=session.get('user_id')
        )

        db.session.add(nuevo)
        db.session.commit()

        return redirect('/dashboard')

    return render_template('reportar.html')


# =========================
# 🧠 ASIGNAR ENTIDAD (ADMIN)
# =========================
@main.route('/asignar-entidad/<int:id>', methods=['POST'])
def asignar_entidad(id):
    if session.get('rol') != 'admin':
        return redirect('/login')

    reporte = Reporte.query.get_or_404(id)
    entidad_id = request.form.get('entidad_id')

    reporte.entidad_id = entidad_id
    reporte.estado = "Asignado a entidad"

    db.session.commit()

    return redirect('/admin')


# =========================
# 🧠 ASIGNAR TECNICO (ENTIDAD)
# =========================
@main.route('/asignar-tecnico/<int:id>', methods=['POST'])
def asignar_tecnico(id):
    if session.get('rol') != 'entidad':
        return redirect('/login')

    reporte = Reporte.query.get_or_404(id)
    tecnico_id = request.form.get('tecnico_id')

    reporte.tecnico_id = tecnico_id
    reporte.estado = "Asignado a técnico"
    db.session.commit()

    return redirect('/entidad')


# =========================
# 🔓 LOGOUT
# =========================
@main.route('/logout')
def logout():
    session.clear()
    return redirect('/login')