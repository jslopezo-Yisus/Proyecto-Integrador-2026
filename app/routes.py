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
from datetime import datetime
from reportlab.platypus import Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from flask import Blueprint, render_template, request, redirect, session, flash
from flask import jsonify
import os
import io
import uuid


main = Blueprint('main', __name__)


# MARCA DE AGUA HOMEFIX

def agregar_marca_agua(canvas, doc):

    logo_path = os.path.join(
        'app',
        'static',
        'img',
        'logo.png'
    )

    canvas.saveState()

    # Transparencia
    canvas.setFillAlpha(0.08)

    # Dibujar logo
    canvas.drawImage(
        logo_path,
        180,
        250,
        width=250,
        height=250,
        preserveAspectRatio=True,
        mask='auto'
    )

    canvas.restoreState()

# INDEX

@main.route('/')
def index():
    return render_template ('index.html')



# LOGIN

@main.route ('/login', methods=['GET', 'POST'])
def login():

    if 'user_id' in session:

        rol = session.get('rol')

        if rol == 'admin':
            return redirect('/admin')

        elif rol == 'tecnico':
            return redirect('/tecnico')

        elif rol == 'entidad':
            return redirect('/entidad')

        else:
            return redirect('/dashboard')

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

        session.permanent=True

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

    if 'user_id' in session:

        rol = session.get('rol')

        if rol == 'admin':
            return redirect('/admin')

        elif rol == 'tecnico':
            return redirect('/tecnico')

        elif rol == 'entidad':
            return redirect('/entidad')

        else:
            return redirect('/dashboard')
    
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

    
    # KPI
   

    total_reportes = Reporte.query.count()

    reportes_resueltos = Reporte.query.filter_by(
        estado='Solucionado'
    ).count()

    reportes_pendientes = Reporte.query.filter(
        Reporte.estado != 'Solucionado'
    ).count()

    tecnicos = Usuario.query.filter_by(
        rol='tecnico'
    ).count()

    entidades_total = Entidad.query.count()

    promedio_calificacion = db.session.query(
        db.func.avg(Reporte.calificacion)
    ).scalar()

    if not promedio_calificacion:
        promedio_calificacion = 0

    
    # GRAFICA ESTADOS
    

    iniciados = Reporte.query.filter_by(
        estado='Iniciado'
    ).count()

    proceso = Reporte.query.filter_by(
        estado='En proceso'
    ).count()

    solucionados = Reporte.query.filter_by(
        estado='Solucionado'
    ).count()

    
    # GRAFICA PRIORIDAD
    

    prioridad_alta = Reporte.query.filter_by(
        prioridad='Alta'
    ).count()

    prioridad_media = Reporte.query.filter_by(
        prioridad='Media'
    ).count()

    prioridad_baja = Reporte.query.filter_by(
        prioridad='Baja'
    ).count()

    return render_template(

        'admin.html',

        reportes=reportes,
        entidades=entidades,

        total_reportes=total_reportes,
        reportes_resueltos=reportes_resueltos,
        reportes_pendientes=reportes_pendientes,
        tecnicos=tecnicos,
        entidades_total=entidades_total,

        promedio_calificacion=round(
            promedio_calificacion,
            1
        ),

        # CHARTS

        estados_labels=[
            'Iniciado',
            'En proceso',
            'Solucionado'
        ],

        estados_data=[
            iniciados,
            proceso,
            solucionados
        ],

        prioridad_labels=[
            'Alta',
            'Media',
            'Baja'
        ],

        prioridad_data=[
            prioridad_alta,
            prioridad_media,
            prioridad_baja
        ]
    )



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

    # USUARIO ACTUAL
    user_id = session.get('user_id')

    usuario = Usuario.query.get(user_id)

    # ENTIDAD DEL USUARIO
    entidad_id = usuario.entidad_id

    # REPORTES DE ESA ENTIDAD
    reportes = Reporte.query.filter_by(
        entidad_id=entidad_id
    ).all()

    # TECNICOS DE ESA ENTIDAD
    tecnicos = Usuario.query.filter_by(
        rol='tecnico',
        entidad_id=entidad_id
    ).all()

    
    # KPI
    

    total_reportes = Reporte.query.filter_by(
        entidad_id=entidad_id
    ).count()

    reportes_resueltos = Reporte.query.filter_by(
        entidad_id=entidad_id,
        estado='Solucionado'
    ).count()

    reportes_pendientes = Reporte.query.filter(
        Reporte.entidad_id == entidad_id,
        Reporte.estado != 'Solucionado'
    ).count()

    total_tecnicos = Usuario.query.filter_by(
        rol='tecnico',
        entidad_id=entidad_id
    ).count()

    promedio_calificacion = db.session.query(
        db.func.avg(Reporte.calificacion)
    ).filter(
        Reporte.entidad_id == entidad_id
    ).scalar()

    if not promedio_calificacion:
        promedio_calificacion = 0

    return render_template(

        'entidad.html',

        reportes=reportes,
        tecnicos=tecnicos,

        total_reportes=total_reportes,
        reportes_resueltos=reportes_resueltos,
        reportes_pendientes=reportes_pendientes,
        total_tecnicos=total_tecnicos,
        promedio_calificacion=round(promedio_calificacion, 1)
    )



# PANEL TECNICO

@main.route('/tecnico')
def tecnico():

    if session.get('rol') != 'tecnico':
        return redirect('/login')

    tecnico_id = session.get('user_id')

    # REPORTES DEL TECNICO
    reportes = Reporte.query.filter_by(
        tecnico_id=tecnico_id
    ).all()

    
    # KPI
    

    total_reportes = Reporte.query.filter_by(
        tecnico_id=tecnico_id
    ).count()

    reportes_resueltos = Reporte.query.filter_by(
        tecnico_id=tecnico_id,
        estado='Solucionado'
    ).count()

    reportes_pendientes = Reporte.query.filter(
        Reporte.tecnico_id == tecnico_id,
        Reporte.estado != 'Solucionado'
    ).count()

    promedio_calificacion = db.session.query(
        db.func.avg(Reporte.calificacion)
    ).filter(
        Reporte.tecnico_id == tecnico_id
    ).scalar()

    if not promedio_calificacion:
        promedio_calificacion = 0

    return render_template(

        'tecnico.html',

        reportes=reportes,

        total_reportes=total_reportes,
        reportes_resueltos=reportes_resueltos,
        reportes_pendientes=reportes_pendientes,
        promedio_calificacion=round(promedio_calificacion, 1)
    )

@main.route('/editar-tecnico/<int:id>', methods=['POST'])
def editar_tecnico(id):

    if session.get('rol') != 'tecnico':
        return redirect('/login')

    reporte = Reporte.query.get_or_404(id)

    # ACTUALIZAR DATOS
    reporte.estado = request.form.get('estado')
    reporte.descripcion = request.form.get('descripcion')

    # SI EL REPORTE FUE SOLUCIONADO
    if reporte.estado == 'Solucionado':

        reporte.fecha_solucion = datetime.utcnow()

    # GUARDAR HISTORIAL
    historial = HistorialReporte(
        reporte_id=reporte.id,
        accion="Reporte actualizado",
        detalle=f"Estado cambiado a {reporte.estado}"
    )

    db.session.add(historial)

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

        tipo_dano = request.form.get('tipo_dano')

        # ⏰ Hora actual
        hora_actual = datetime.now().hour

        # 🔥 PRIORIDAD AUTOMÁTICA

        if tipo_dano == 'eléctrico':

            if hora_actual >= 18 or hora_actual <= 5:
                prioridad = 'alta'
            else:
                prioridad = 'media'

        elif tipo_dano == 'plomería':
            prioridad = 'media'

        elif tipo_dano == 'estructura':
            prioridad = 'alta'

        else:
            prioridad = 'baja'

        # 📌 CREAR REPORTE
        nuevo = Reporte(
            titulo=request.form['titulo'],
            descripcion=request.form['descripcion'],
            direccion=request.form['direccion'],
            tipo_dano=tipo_dano,
            prioridad=prioridad,
            latitud=request.form.get('latitud'),
            longitud=request.form.get('longitud'),
            user_id=session.get('user_id')
        )

        db.session.add(nuevo)
        db.session.commit()

        # 🧾 HISTORIAL
        historial = HistorialReporte(
            reporte_id=nuevo.id,
            accion='Reporte creado',
            detalle=f'''
            El usuario creó el reporte.
            Tipo de daño: {tipo_dano}.
            Prioridad asignada automáticamente: {prioridad}
            '''
        )

        db.session.add(historial)
        db.session.commit()

        flash('Reporte enviado correctamente', 'success')

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
            detalle = f"El administrador asignó una entidad ID{entidad_id}"
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
            detalle = f"La entidad asignó un técnico ID{tecnico_id}"
        )
    
    db.session.add(historial)
    db.session.commit()

    flash('Tecnico asignado correctamente','seccess')

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
            detalle = 'Se modifico la información del reporte'
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

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    contenido = []

    
    # LOGO
    

    logo_path = os.path.join(
        'app',
        'static',
        'img',
        'logo.png'
    )

    logo = Image(
        logo_path,
        width=80,
        height=80
    )

    contenido.append(logo)

    
    # TITULO
    

    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        textColor=colors.black,
        fontSize=22,
        leading=30
    )

    contenido.append(
        Paragraph(
            "HOME-FIX<br/>Reporte Técnico Oficial",
            titulo_style
        )
    )

    contenido.append(Spacer(1, 25))

    
    # INFORMACION GENERAL

    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['BodyText'],
        textColor=colors.white,
        fontName='Helvetica-Bold'
    )
    

    datos = [

        [
            Paragraph('Campo', header_style),
            Paragraph('Información', header_style)
        ],

        [
            Paragraph('Título', styles['BodyText']),
            Paragraph(f"{reporte.titulo or ''}", styles['BodyText'])
        ],

        [
            Paragraph('Descripción', styles['BodyText']),
            Paragraph(f"{reporte.descripcion or ''}", styles['BodyText'])
        ],

        [
            Paragraph('Dirección', styles['BodyText']),
            Paragraph(f"{reporte.direccion or ''}", styles['BodyText'])
        ],

        [
            Paragraph('Prioridad', styles['BodyText']),
            Paragraph(f"{reporte.prioridad or ''}", styles['BodyText'])
        ],

        [
            Paragraph('Estado', styles['BodyText']),
            Paragraph(f"{reporte.estado or ''}", styles['BodyText'])
        ],

        [
            Paragraph('Latitud', styles['BodyText']),
            Paragraph(f"{reporte.latitud or ''}", styles['BodyText'])
        ],

        [
            Paragraph('Longitud', styles['BodyText']),
            Paragraph(f"{reporte.longitud or ''}", styles['BodyText'])
        ]

    ]

    tabla = Table(
        datos,
        colWidths=[150, 320]
    )

    tabla.setStyle(TableStyle([

        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1F3C88")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),

        ('GRID', (0,0), (-1,-1), 1, colors.grey),

        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),

        ('BACKGROUND', (0,1), (-1,-1), colors.beige),

        ('BOTTOMPADDING', (0,0), (-1,0), 12),

        ('VALIGN', (0,0), (-1,-1), 'TOP')

    ]))

    contenido.append(tabla)

    contenido.append(Spacer(1, 25))

    
    # HISTORIAL
    

    contenido.append(
        Paragraph(
            "Historial del Reporte",
            styles['Heading2']
        )
    )

    historial_data = [
        ['Fecha', 'Acción', 'Detalle']
    ]

    for h in historial:

        historial_data.append([
            str(h.fecha_creacion),
            h.accion,
            h.detalle
        ])

    tabla_historial = Table(
        historial_data,
        colWidths=[140, 150, 180]
    )

    tabla_historial.setStyle(TableStyle([

        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1F3C88")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),

        ('GRID', (0,0), (-1,-1), 1, colors.grey),

        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),

        ('BACKGROUND', (0,1), (-1,-1), colors.beige),

        ('VALIGN', (0,0), (-1,-1), 'TOP')

    ]))

    contenido.append(tabla_historial)

    contenido.append(Spacer(1, 30))

   
    # FOOTER
    

    footer = Paragraph(
        "HomeFix © 2026 | Plataforma Inteligente de Gestión de Incidencias",
        ParagraphStyle(
            'footer',
            alignment=TA_CENTER,
            textColor=colors.grey,
            fontSize=9
        )
    )

    contenido.append(footer)

    
    # CONSTRUIR PDF
    

    doc.build(
        contenido,
        onFirstPage=agregar_marca_agua,
        onLaterPages=agregar_marca_agua
    )

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"reporte_tecnico_{id}.pdf",
        mimetype='application/pdf'
    )


# PDF CIUDADANO

def generar_pdf_ciudadano(id):

    reporte = Reporte.query.get_or_404(id)

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    contenido = []

    # =========================
    # LOGO
    # =========================

    logo_path = os.path.join(
        'app',
        'static',
        'img',
        'logo.png'
    )

    logo = Image(
        logo_path,
        width=70,
        height=70
    )

    contenido.append(logo)

    # =========================
    # TITULO
    # =========================

    titulo_style = ParagraphStyle(
        'TituloCiudadano',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1F3C88"),
        fontSize=20,
        leading=25
    )

    contenido.append(
        Paragraph(
            "HOMEFIX<br/>Resumen Ciudadano del Reporte",
            titulo_style
        )
    )

    contenido.append(Spacer(1, 20))

    # =========================
    # MENSAJE
    # =========================

    mensaje = """
    Gracias por utilizar HomeFix.
    Este documento resume la información principal
    de su incidencia reportada.
    """

    contenido.append(
        Paragraph(
            mensaje,
            styles['BodyText']
        )
    )

    contenido.append(Spacer(1, 20))

    # =========================
    # TABLA PRINCIPAL
    # =========================

    datos = [

        [
            Paragraph('<b>Campo</b>', styles['BodyText']),
            Paragraph('<b>Información</b>', styles['BodyText'])
        ],

        [
            Paragraph('Título', styles['BodyText']),
            Paragraph(f"{reporte.titulo or ''}", styles['BodyText'])
        ],

        [
            Paragraph('Descripción', styles['BodyText']),
            Paragraph(f"{reporte.descripcion or ''}", styles['BodyText'])
        ],

        [
            Paragraph('Dirección', styles['BodyText']),
            Paragraph(f"{reporte.direccion or ''}", styles['BodyText'])
        ],

        [
            Paragraph('Estado actual', styles['BodyText']),
            Paragraph(f"{reporte.estado or ''}", styles['BodyText'])
        ],

        [
            Paragraph('Prioridad', styles['BodyText']),
            Paragraph(f"{reporte.prioridad or ''}", styles['BodyText'])
        ]

    ]

    tabla = Table(
        datos,
        colWidths=[150, 320]
    )

    tabla.setStyle(TableStyle([

        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1F3C88")),

        ('TEXTCOLOR', (0,0), (-1,0), colors.white),

        ('GRID', (0,0), (-1,-1), 1, colors.grey),

        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),

        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),

        ('BOTTOMPADDING', (0,0), (-1,0), 10),

        ('VALIGN', (0,0), (-1,-1), 'TOP')

    ]))

    contenido.append(tabla)

    contenido.append(Spacer(1, 25))

    # =========================
    # MENSAJE FINAL
    # =========================

    texto_final = """
    HomeFix continúa trabajando para mejorar
    la atención y solución de incidencias
    ciudadanas de manera rápida y eficiente.
    """

    contenido.append(
        Paragraph(
            texto_final,
            styles['Italic']
        )
    )

    contenido.append(Spacer(1, 30))

    # =========================
    # FOOTER
    # =========================

    footer = Paragraph(
        "HomeFix © 2026 | Plataforma Inteligente de Gestión de Incidencias",
        ParagraphStyle(
            'footerCiudadano',
            alignment=TA_CENTER,
            textColor=colors.grey,
            fontSize=9
        )
    )

    contenido.append(footer)

    # =========================
    # CONSTRUIR PDF
    # =========================

    doc.build(
        contenido,
        onFirstPage=agregar_marca_agua,
        onLaterPages=agregar_marca_agua
    )

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"reporte_ciudadano_{id}.pdf",
        mimetype='application/pdf'
    )



# DESCARGAR PDF


@main.route('/reporte/pdf/<int:id>')
def generar_pdf(id):

    if 'user_id' not in session:
        return redirect('/login')

    return generar_pdf_interno(id)

# PDF CIUDADANO

@main.route('/reporte/pdf-ciudadano/<int:id>')
def pdf_ciudadano(id):

    if 'user_id' not in session:
        return redirect('/login')

    return generar_pdf_ciudadano(id)


# APIs HOMEFIX


# API 1 - LISTAR TODOS LOS REPORTES


@main.route('/api/reportes', methods=['GET'])
def api_reportes():

    reportes = Reporte.query.all()

    lista = []

    for r in reportes:

        lista.append({

            'id': r.id,
            'titulo': r.titulo,
            'descripcion': r.descripcion,
            'direccion': r.direccion,
            'tipo_dano': r.tipo_dano,
            'prioridad': r.prioridad,
            'estado': r.estado,
            'latitud': r.latitud,
            'longitud': r.longitud,
            'fecha': str(r.fecha_creacion),
            'tecnico_id': r.tecnico_id,
            'entidad_id': r.entidad_id

        })

    return jsonify(lista)




# API 2 - DETALLE DE UN REPORTE

from flask import jsonify

@main.route('/api/reportes/<int:id>', methods=['GET'])
def api_detalle_reporte(id):

    reporte = Reporte.query.get_or_404(id)

    data = {

        'id': reporte.id,
        'titulo': reporte.titulo,
        'descripcion': reporte.descripcion,
        'direccion': reporte.direccion,
        'tipo_dano': reporte.tipo_dano,
        'prioridad': reporte.prioridad,
        'estado': reporte.estado,
        'latitud': reporte.latitud,
        'longitud': reporte.longitud,

        'fecha_creacion': str(reporte.fecha_creacion),

        'usuario_id': reporte.user_id,
        'tecnico_id': reporte.tecnico_id,
        'entidad_id': reporte.entidad_id

    }

    return jsonify(data)




# API 3 - CREAR REPORTE


@main.route('/api/crear-reporte', methods=['POST'])
def api_crear_reporte():

    data = request.get_json()

    titulo = data.get('titulo')
    descripcion = data.get('descripcion')
    direccion = data.get('direccion')
    tipo_dano = data.get('tipo_dano')

    prioridad = 'media'

    if tipo_dano == 'eléctrico':
        prioridad = 'alta'

    elif tipo_dano == 'estructura':
        prioridad = 'alta'

    elif tipo_dano == 'plomería':
        prioridad = 'media'

    else:
        prioridad = 'baja'

    nuevo = Reporte(

        titulo=titulo,
        descripcion=descripcion,
        direccion=direccion,
        tipo_dano=tipo_dano,
        prioridad=prioridad,
        estado='Iniciado'

    )

    db.session.add(nuevo)
    db.session.commit()

    return jsonify({

        'mensaje': 'Reporte creado correctamente',
        'reporte_id': nuevo.id

    }), 201




# API 4 - KPIs ADMINISTRATIVOS


@main.route('/api/kpis', methods=['GET'])
def api_kpis():

    total_reportes = Reporte.query.count()

    resueltos = Reporte.query.filter_by(
        estado='Solucionado'
    ).count()

    pendientes = Reporte.query.filter(
        Reporte.estado != 'Solucionado'
    ).count()

    tecnicos = Usuario.query.filter_by(
        rol='tecnico'
    ).count()

    entidades = Entidad.query.count()

    promedio = db.session.query(
        db.func.avg(Reporte.calificacion)
    ).scalar()

    if not promedio:
        promedio = 0

    data = {

        'total_reportes': total_reportes,
        'reportes_resueltos': resueltos,
        'reportes_pendientes': pendientes,
        'tecnicos_activos': tecnicos,
        'entidades': entidades,
        'satisfaccion_promedio': round(promedio, 1)

    }

    return jsonify(data)




# API 5 - LISTAR TECNICOS


@main.route('/api/tecnicos', methods=['GET'])
def api_tecnicos():

    tecnicos = Usuario.query.filter_by(
        rol='tecnico'
    ).all()

    lista = []

    for t in tecnicos:

        lista.append({

            'id': t.id,
            'nombre': t.nombre,
            'correo': t.correo,
            'entidad_id': t.entidad_id

        })

    return jsonify(lista)




# API 6 - LISTAR ENTIDADES


@main.route('/api/entidades', methods=['GET'])
def api_entidades():

    entidades = Entidad.query.all()

    lista = []

    for e in entidades:

        lista.append({

            'id': e.id,
            'nombre': e.nombre

        })

    return jsonify(lista)




# API 7 - HISTORIAL DE REPORTE


@main.route('/api/historial/<int:id>', methods=['GET'])
def api_historial(id):

    historial = HistorialReporte.query.filter_by(
        reporte_id=id
    ).all()

    lista = []

    for h in historial:

        lista.append({

            'fecha': str(h.fecha),
            'accion': h.accion,
            'detalle': h.detalle

        })

    return jsonify(lista)




# API 8 - ELIMINAR REPORTE


@main.route('/api/eliminar-reporte/<int:id>', methods=['DELETE'])
def api_eliminar_reporte(id):

    reporte = Reporte.query.get_or_404(id)

    db.session.delete(reporte)
    db.session.commit()

    return jsonify({

        'mensaje': 'Reporte eliminado correctamente'

    })




# API 9 - ACTUALIZAR ESTADO


@main.route('/api/actualizar-estado/<int:id>', methods=['PUT'])
def api_actualizar_estado(id):

    reporte = Reporte.query.get_or_404(id)

    data = request.get_json()

    nuevo_estado = data.get('estado')

    reporte.estado = nuevo_estado

    db.session.commit()

    return jsonify({

        'mensaje': 'Estado actualizado correctamente',
        'nuevo_estado': nuevo_estado

    })




# API 10 - DASHBOARD TECNICO


@main.route('/api/dashboard-tecnico/<int:id>', methods=['GET'])
def api_dashboard_tecnico(id):

    total = Reporte.query.filter_by(
        tecnico_id=id
    ).count()

    resueltos = Reporte.query.filter_by(
        tecnico_id=id,
        estado='Solucionado'
    ).count()

    pendientes = Reporte.query.filter(
        Reporte.tecnico_id == id,
        Reporte.estado != 'Solucionado'
    ).count()

    data = {

        'tecnico_id': id,
        'total_reportes': total,
        'resueltos': resueltos,
        'pendientes': pendientes

    }

    return jsonify(data)