from flask import Blueprint, render_template, request, redirect, session, flash
from . models import Reporte, Usuario, TokenTecnico, TokenEntidad, Entidad
from . import db
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file
from .models import HistorialReporte
from flask import make_response
from reportlab.pdfgen import canvas
from io import BytesIO
import io
import uuid


main = Blueprint('main', __name__)


# INDEX

@main.route('/')
def index():
    return render_template('index.html')



# LOGIN

@main.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        correo = request.form.get('correo')
        password = request.form.get('password')
        rol = request.form.get('rol')

        # Buscar usuario
        user = Usuario.query.filter_by(
            correo=correo
        ).first()

        # Validar credenciales
        if not user or not user.check_password(password):

            return render_template(
                'login.html',
                error='Correo o contraseña incorrectos'
            )

        # Validar rol
        if user.rol != rol:

            return render_template(
                'login.html',
                error='El tipo de usuario no coincide'
            )

        # SESIÓN
        session['user_id'] = user.id
        session['rol'] = user.rol
        session['nombre'] = user.nombre

        # 🚀 REDIRECCIONES
        if user.rol == 'admin':
            return redirect('/admin')

        elif user.rol == 'tecnico':

            return redirect('/tecnico')

        elif user.rol == 'entidad':

            return redirect('/entidad')

        else:

            return redirect('/dashboard')

    return render_template('login.html')



# REGISTRO

@main.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':

        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        password = request.form.get('password')
        rol = request.form.get('rol')
        token = request.form.get('token')
        entidad_nombre = request.form.get('entidad')

        # VALIDAR CORREO

        if Usuario.query.filter_by(correo=correo).first():
            flash('El correo ya está registrado', 'danger')
            return redirect('/registro')

        
        # TECNICO
        
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

        
        # ENTIDAD
        
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

    
        # USUARIO NORMAL
        
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

    entidades = Entidad.query.all()
    return render_template('registro.html', entidades = entidades)



# ADMIN

@main.route('/admin')
def admin():
    if session.get('rol') != 'admin':
        return redirect('/login')

    reportes = Reporte.query.all()
    entidades = Entidad.query.all()

    return render_template('admin.html', reportes=reportes, entidades=entidades)



# GENERAR TOKEN TECNICO

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



# GENERAR TOKEN ENTIDAD

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



# PANEL ENTIDAD

@main.route('/entidad')
def entidad():
    if session.get('rol') != 'entidad':
        return redirect('/login')

    #  Usuario actual
    user_id = session.get('user_id')
    usuario = Usuario.query.get(user_id)

    #  Entidad del usuario
    entidad_id = usuario.entidad_id

    #  Reportes SOLO de esa entidad
    reportes = Reporte.query.filter_by(entidad_id=entidad_id).all()

    #  Técnicos SOLO de esa entidad
    tecnicos = Usuario.query.filter_by(rol='tecnico', entidad_id=entidad_id).all()

    return render_template('entidad.html', reportes=reportes, tecnicos=tecnicos)



# PANEL TECNICO

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

    historial = HistorialReporte(
        reporte_id = reporte.id,
        accion = "Reporte actualizado",
        detalle = f"Estado cambiado a {reporte.estado}"
    )

    db.session.commit()

    flash('Reporte actualizado correctamente', 'success')
    return redirect('/tecnico')

@main.route('/eliminar-reporte/<int:id>', methods=['POST'])
def eliminar_reporte(id):

    if session.get('rol') != 'tecnico':
        return redirect('/login')

    reporte = Reporte.query.get_or_404(id)

    motivo = request.form.get('motivo')
    # GUARDAR HISTORIAL
    historial = HistorialReporte(
        reporte_id=reporte.id,
        accion="Reporte eliminado",
        detalle=f"Motivo: {motivo}"
    )

    db.session.add(historial)
    db.session.commit()

    # GENERAR PDF AUTOMÁTICO
    pdf = generar_pdf_interno(reporte.id)

    # ELIMINAR REPORTE
    db.session.delete(reporte)
    db.session.commit()

    return pdf



# DASHBOARD USUARIO

@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    reportes = Reporte.query.filter_by(user_id=session['user_id']).all()

    return render_template('dashboard.html', reportes=reportes)


# VER REPORTES (GENERAL)

@main.route('/reportes')
def ver_reportes():

    # Si no está logueado → lo mando al inicio
    if 'user_id' not in session:
        return redirect('/')

    # FILTRO POR ROL
    if session['rol'] == 'usuario':
        reportes = Reporte.query.filter_by(user_id=session['user_id']).all()

    elif session['rol'] == 'tecnico':
        reportes = Reporte.query.filter_by(tecnico_id=session['user_id']).all()

    elif session['rol'] == 'entidad':
        user = Usuario.query.get(session['user_id'])
        reportes = Reporte.query.filter_by(entidad_id=user.entidad_id).all()

    else:  # admin
        reportes = Reporte.query.all()

    return render_template('reportes.html', reportes=reportes)


# CREAR REPORTE

@main.route('/reportar', methods=['GET', 'POST'])
def reportar():
    if request.method == 'POST':

        nuevo = Reporte(
            titulo=request.form['titulo'],
            descripcion=request.form['descripcion'],
            direccion=request.form['direccion'],
            prioridad=request.form['prioridad'],
            latitud=request.form.get('latitud'),
            longitud=request.form.get('longitud'),
            user_id=session.get('user_id')
        )

        db.session.add(nuevo)
        db.session.commit()

        historial = HistorialReporte(
            reporte_id = nuevo.id,
            accion = 'Reporte Creado',
            descripcion = 'El ususario creó el reporte'
        )
        db.session.add(historial)
        db.session.commit()

        return redirect('/dashboard')

    return render_template('reportar.html')



#  ASIGNAR ENTIDAD (ADMIN)

@main.route('/asignar-entidad/<int:id>', methods=['POST'])
def asignar_entidad(id):
    if session.get('rol') != 'admin':
        return redirect('/login')

    reporte = Reporte.query.get_or_404(id)
    entidad_id = request.form.get('entidad_id')

    reporte.entidad_id = entidad_id
    reporte.estado = "Asignado a entidad"
    
    historial = HistorialReporte(
            reporte_id = reporte.id,
            accion = "Entidad asignada",
            descripcion = f"El administrador asignó una entidad ID{entidad_id}"
        )
    
    db.session.add(historial)
    db.session.commit()

    return redirect('/admin')



# ASIGNAR TECNICO (ENTIDAD)

@main.route('/asignar-tecnico/<int:id>', methods=['POST'])
def asignar_tecnico(id):
    if session.get('rol') != 'entidad':
        return redirect('/login')

    reporte = Reporte.query.get_or_404(id)
    tecnico_id = request.form.get('tecnico_id')

    reporte.tecnico_id = tecnico_id
    reporte.estado = "Asignado a técnico"


    historial = HistorialReporte(
            reporte_id = reporte.id,
            accion = "Tecnico asignado",
            descripcion = f"La entidad asignó un técnico ID{tecnico_id}"
        )
    
    db.session.add(historial)
    db.session.commit()

    return redirect('/entidad')

# Ver reporte

@main.route('/ver-reporte/<int:id>')
def ver_reporte(id):

    if 'user_id' not in session:
        return redirect('/login')
    reporte = Reporte.query.get_or_404(id)
    return render_template('ver_reporte.html', reporte=reporte)

# Editar Reporte

@main.route('/editar-reporte/<int:id>', methods=['GET','POST'])
def editar_reporte(id):
    if 'user_id' not in session:
        return redirect('/login')

    reporte = Reporte.query.get_or_404(id)

    if request.method == 'POST':

        reporte.titulo = request.form.get('titulo')
        reporte.descripcion = request.form.get('descripcion')
        reporte.direccion = request.form.get('direccion')
        reporte.prioridad = request.form.get('prioridad')

        db.session.commit()

        historial = HistorialReporte(
            reporte_id = reporte.id,
            accion = 'Reporte editado',
            descripcion = 'Se modifico la información del reporte'
        )

        db.session.add(historial)
        db.session.commit()


        flash('Reporte actualizado correctamente','success')
        return redirect('/reportes')
    return render_template('editar_reporte.html', reporte=reporte)

# Eliminar Reporte

@main.route('/eliminar-reporte-usuario/<int:id>', methods=['POST'])
def eliminar_reporte_usuario(id):

    if 'user_id' not in session:
        return redirect('/login')
    reporte = reporte.query.get_or_404(id)

    db.session.delete(reporte)
    db.session.commit()

    flash('Reporte eliminado correctamente','danger')

    return redirect('/reportes')

# Lista Reportes

@main.route('/reportes')
def reportes():

    if 'user_id' not in session:
        return redirect('/login')

    reportes = Reporte.query.filter_by(user_id = session['user_id']).all()
    return render_template('reporte.html',reportes=reportes)

# LOGOUT

@main.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# FUNCION INTERNA PDF

def generar_pdf_interno(id):

    reporte = Reporte.query.get_or_404(id)

    historial = HistorialReporte.query.filter_by(
        reporte_id=id
    ).all()

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()

    contenido = []


    contenido.append(
        Paragraph("Reporte HomeFix", styles['Title'])
    )

    contenido.append(Spacer(1, 12))
    contenido.append(
        Paragraph(f"Título: {reporte.titulo}", styles['Normal'])
    )

    contenido.append(
        Paragraph(f"Descripción: {reporte.descripcion}", styles['Normal'])
    )

    contenido.append(
        Paragraph(f"Dirección: {reporte.direccion}", styles['Normal'])
    )

    contenido.append(
        Paragraph(f"Prioridad: {reporte.prioridad}", styles['Normal'])
    )

    contenido.append(
        Paragraph(f"Estado: {reporte.estado}", styles['Normal'])
    )

    contenido.append(Spacer(1, 20))

    contenido.append(
        Paragraph("Historial del reporte", styles['Heading2'])
    )

    for h in historial:

        texto = f"""
        {h.fecha} <br/>
        Acción: {h.accion} <br/>
        Detalle: {h.detalle}
        """

        contenido.append(
            Paragraph(texto, styles['Normal'])
        )

        contenido.append(Spacer(1, 10))
    doc.build(contenido)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"reporte_{id}.pdf",
        mimetype='application/pdf'
    )



# DESCARGAR PDF

@main.route('/reporte/pdf/<int:id>')
def generar_pdf(id):

    if 'user_id' not in session:
        return redirect('/login')

    return generar_pdf_interno(id)