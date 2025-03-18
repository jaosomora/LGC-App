"""
Blueprint para manejar la funcionalidad de feedback de usuarios
"""
import os
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify, current_app

# Configurar el logger específico para feedback
feedback_logger = logging.getLogger('feedback')
feedback_logger.setLevel(logging.INFO)

# Crear un manejador para los logs de feedback
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
feedback_logger.addHandler(handler)

# Crear el blueprint
feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/enviar_feedback', methods=['POST'])
def enviar_feedback():
    """
    Endpoint para recibir feedback del usuario y enviarlo por correo.
    Registra información detallada en los logs para facilitar la depuración.
    """
    feedback_logger.info("Recibida solicitud de envío de feedback")
    
    try:
        # Obtener el contenido del feedback
        feedback_text = request.form.get('feedback', '')
        feedback_logger.info(f"Contenido del feedback: {feedback_text[:50]}...")
        
        if not feedback_text or feedback_text.strip() == '':
            feedback_logger.warning("Se intentó enviar feedback vacío")
            return jsonify({"success": False, "message": "El mensaje está vacío"}), 400
        
        # Configuración del correo electrónico
        remitente = os.getenv('SMTP_USER', 'no-reply@julianosoriom.com')
        destinatario = 'info@julianosoriom.com'
        
        # Crear el mensaje
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = f"Feedback de LGC App - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        # Añadir información adicional al cuerpo del mensaje
        ip_usuario = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'No disponible')
        referer = request.headers.get('Referer', 'No disponible')
        
        cuerpo_mensaje = f"""
        Nuevo feedback recibido:
        
        {feedback_text}
        
        ---
        Información adicional:
        - Fecha y hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        - IP: {ip_usuario}
        - Navegador: {user_agent}
        - Página de origen: {referer}
        """
        
        msg.attach(MIMEText(cuerpo_mensaje, 'plain'))
        
        # Configurar el servidor SMTP y enviar el correo
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.tu-proveedor.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_usuario = os.getenv('SMTP_USER', 'tu-usuario@proveedor.com')
        smtp_password = os.getenv('SMTP_PASSWORD', 'tu-contraseña')

        # Añade estas líneas de depuración después de obtener las variables de entorno
        feedback_logger.info(f"Variables SMTP cargadas: servidor={smtp_server}, puerto={smtp_port}, usuario={smtp_usuario[:3]}...")
        
        feedback_logger.info(f"Intentando conectar a servidor SMTP: {smtp_server}:{smtp_port}")
        
        # Intentar enviar el correo
        with smtplib.SMTP(smtp_server, smtp_port) as servidor:
            feedback_logger.info("Conexión establecida con servidor SMTP")
            servidor.starttls()
            feedback_logger.info("TLS activado")
            
            feedback_logger.info(f"Intentando login con usuario: {smtp_usuario}")
            servidor.login(smtp_usuario, smtp_password)
            feedback_logger.info("Login exitoso")
            
            feedback_logger.info(f"Enviando mensaje a: {destinatario}")
            servidor.send_message(msg)
            feedback_logger.info("Mensaje enviado correctamente")
        
        feedback_logger.info(f"✅ Feedback enviado correctamente a {destinatario}")
        return jsonify({"success": True, "message": "Feedback enviado correctamente"}), 200
    
    except Exception as e:
        feedback_logger.error(f"❌ Error al enviar feedback: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"Error al enviar feedback: {str(e)}"}), 500


# Ruta alternativa para guardar feedback en base de datos
@feedback_bp.route('/guardar_feedback', methods=['POST'])
def guardar_feedback():
    """
    Endpoint alternativo para guardar el feedback en la base de datos.
    Útil cuando no se puede configurar SMTP o como respaldo.
    """
    feedback_logger.info("Recibida solicitud para guardar feedback en DB")
    
    try:
        # Obtener el contenido del feedback
        feedback_text = request.form.get('feedback', '')
        
        if not feedback_text or feedback_text.strip() == '':
            feedback_logger.warning("Se intentó guardar feedback vacío")
            return jsonify({"success": False, "message": "El mensaje está vacío"}), 400
        
        # Obtener la conexión a la base de datos desde la aplicación
        from app import db_path, sqlite3
        feedback_logger.info(f"Conectando a base de datos en: {db_path}")
        
        # Crear conexión a la base de datos
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Crear tabla si no existe
        feedback_logger.info("Verificando/creando tabla feedback")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip TEXT,
                user_agent TEXT,
                referer TEXT
            )
        ''')
        
        # Insertar feedback en la base de datos
        ip_usuario = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'No disponible')
        referer = request.headers.get('Referer', 'No disponible')
        
        feedback_logger.info(f"Insertando feedback en la base de datos: {feedback_text[:50]}...")
        cursor.execute(
            "INSERT INTO feedback (contenido, ip, user_agent, referer) VALUES (?, ?, ?, ?)",
            (feedback_text, ip_usuario, user_agent, referer)
        )
        
        connection.commit()
        connection.close()
        
        feedback_logger.info("✅ Feedback guardado correctamente en la base de datos")
        return jsonify({"success": True, "message": "Feedback recibido correctamente"}), 200
    
    except Exception as e:
        feedback_logger.error(f"❌ Error al guardar feedback: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"Error al procesar feedback: {str(e)}"}), 500