"""
Blueprint para la funcionalidad de analítica y seguimiento.
Proporciona rutas y funciones para recopilar datos de uso de la aplicación.
"""
import os
import logging
import sqlite3
import json
import uuid
import functools
from datetime import datetime
from flask import Blueprint, request, render_template, session, jsonify, g, current_app, Response

# Configurar logger específico para analytics
analytics_logger = logging.getLogger('analytics')
analytics_logger.setLevel(logging.INFO)

# Crear el manejador
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
analytics_logger.addHandler(handler)

# Crear el blueprint
analytics_bp = Blueprint('analytics', __name__)

# Decorador para requerir autenticación de administrador
def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        admin_user = os.getenv("ADMIN_USER", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD")
        
        # Si estamos en desarrollo, permitir acceso sin autenticación
        if os.getenv("ENV") in ["DEVELOPMENT", "LOCAL"] and not admin_password:
            return f(*args, **kwargs)
        
        if not auth or auth.username != admin_user or auth.password != admin_password:
            return Response(
                'Acceso no autorizado', 401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'}
            )
        return f(*args, **kwargs)
    return decorated_function

def get_device_info(user_agent_string):
    """
    Extrae información básica del dispositivo y navegador a partir del User-Agent.
    """
    user_agent = user_agent_string.lower()
    
    # Determinar el tipo de dispositivo
    if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent or 'ipad' in user_agent:
        if 'tablet' in user_agent or 'ipad' in user_agent:
            device_type = 'tablet'
        else:
            device_type = 'mobile'
    else:
        device_type = 'desktop'
    
    # Determinar el sistema operativo
    if 'android' in user_agent:
        os = 'android'
    elif 'iphone' in user_agent or 'ipad' in user_agent or 'ios' in user_agent:
        os = 'ios'
    elif 'windows' in user_agent:
        os = 'windows'
    elif 'mac' in user_agent:
        os = 'macos'
    elif 'linux' in user_agent:
        os = 'linux'
    else:
        os = 'other'
    
    # Determinar el navegador
    if 'chrome' in user_agent and 'edg' not in user_agent and 'opr' not in user_agent:
        browser = 'chrome'
    elif 'firefox' in user_agent:
        browser = 'firefox'
    elif 'safari' in user_agent and 'chrome' not in user_agent:
        browser = 'safari'
    elif 'edg' in user_agent:
        browser = 'edge'
    elif 'opr' in user_agent or 'opera' in user_agent:
        browser = 'opera'
    else:
        browser = 'other'
    
    return {
        'device_type': device_type,
        'os': os,
        'browser': browser
    }

@analytics_bp.context_processor
def inject_analytics():
    """
    Inyecta variables para Analytics y recopilación de estadísticas.
    Solo se activa en producción.
    """
    analytics_enabled = os.getenv("ENV") == "PRODUCTION" or os.getenv("ENABLE_ANALYTICS") == "1"
    analytics_id = "G-X79LQBG6YN" if analytics_enabled else None
    
    # Obtener información del dispositivo
    if request and request.user_agent and analytics_enabled:
        device_info = get_device_info(request.user_agent.string)
    else:
        device_info = {'device_type': 'unknown', 'os': 'unknown', 'browser': 'unknown'}
    
    return {
        'analytics_id': analytics_id,
        'device_info': device_info,
        'env': os.getenv("ENV", "LOCAL")
    }

@analytics_bp.route("/api/stats/page-view", methods=["POST"])
def register_page_view():
    """
    Endpoint para registrar vistas de página y estadísticas.
    Esta ruta permite almacenar datos de uso en la base de datos.
    """
    try:
        # Obtener datos de la solicitud
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        # Extraer información relevante
        path = data.get('path', '')
        device_type = data.get('device_type', 'unknown')
        os = data.get('os', 'unknown')
        browser = data.get('browser', 'unknown')
        feature = data.get('feature', 'page_view')
        
        # Obtener la ruta de la base de datos desde app
        db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
        if not db_path:
            from app import db_path  # Fallback
        
        analytics_logger.info(f"Registrando estadística: {feature} en {path} desde {device_type}/{os}/{browser}")
        
        # Guardar en la base de datos
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Crear tabla si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                path TEXT,
                device_type TEXT,
                os TEXT,
                browser TEXT,
                feature TEXT,
                session_id TEXT
            )
        ''')
        
        # Generar o reutilizar ID de sesión
        session_id = session.get('analytics_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['analytics_session_id'] = session_id
        
        # Insertar datos
        cursor.execute(
            "INSERT INTO analytics (path, device_type, os, browser, feature, session_id) VALUES (?, ?, ?, ?, ?, ?)",
            (path, device_type, os, browser, feature, session_id)
        )
        
        connection.commit()
        connection.close()
        
        return jsonify({"success": True}), 200
        
    except Exception as e:
        analytics_logger.error(f"Error al registrar estadísticas: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500

@analytics_bp.route("/api/stats/app-event", methods=["POST"])
def register_app_event():
    """
    Endpoint para registrar eventos específicos de la aplicación.
    Captura métricas que son difíciles de configurar en Google Analytics.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        # Extraer información relevante
        feature = data.get('feature', '')
        details = data.get('details', {})
        
        # Obtener la ruta de la base de datos desde app
        db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
        if not db_path:
            from app import db_path  # Fallback
        
        analytics_logger.info(f"Registrando evento específico: {feature} con detalles: {details}")
        
        # Guardar en la base de datos
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Crear tabla si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_specific_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                feature TEXT,
                details TEXT,
                session_id TEXT
            )
        ''')
        
        # Generar o reutilizar ID de sesión
        session_id = session.get('analytics_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['analytics_session_id'] = session_id
        
        # Insertar datos
        cursor.execute(
            "INSERT INTO app_specific_events (feature, details, session_id) VALUES (?, ?, ?)",
            (feature, json.dumps(details), session_id)
        )
        
        connection.commit()
        connection.close()
        
        return jsonify({"success": True}), 200
        
    except Exception as e:
        analytics_logger.error(f"Error al registrar evento específico: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500

@analytics_bp.route("/admin/stats", methods=["GET"])
@admin_required
def view_stats():
    """
    Panel simple para visualizar estadísticas de uso.
    Protegido por autenticación básica.
    """
    try:
        # Obtener la ruta de la base de datos desde app
        db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
        if not db_path:
            from app import db_path  # Fallback
            
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analytics'")
        if not cursor.fetchone():
            return render_template("admin/stats.html", stats={
                'total_views': 0,
                'unique_sessions': 0,
                'device_breakdown': [],
                'os_breakdown': [],
                'browser_breakdown': [],
                'feature_usage': [],
                'daily_stats': []
            }, app_events=[])
        
        # Estadísticas generales
        cursor.execute("SELECT COUNT(*) FROM analytics")
        total_views = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT session_id) FROM analytics")
        unique_sessions = cursor.fetchone()[0]
        
        # Distribución por dispositivo
        cursor.execute("SELECT device_type, COUNT(*) as count FROM analytics GROUP BY device_type ORDER BY count DESC")
        device_breakdown = cursor.fetchall()
        
        # Distribución por sistema operativo
        cursor.execute("SELECT os, COUNT(*) as count FROM analytics GROUP BY os ORDER BY count DESC")
        os_breakdown = cursor.fetchall()
        
        # Distribución por navegador
        cursor.execute("SELECT browser, COUNT(*) as count FROM analytics GROUP BY browser ORDER BY count DESC")
        browser_breakdown = cursor.fetchall()
        
        # Uso de características
        cursor.execute("SELECT feature, COUNT(*) as count FROM analytics GROUP BY feature ORDER BY count DESC")
        feature_usage = cursor.fetchall()
        
        # Estadísticas diarias
        cursor.execute("SELECT DATE(timestamp) as day, COUNT(*) as views, COUNT(DISTINCT session_id) as sessions FROM analytics GROUP BY day ORDER BY day DESC LIMIT 30")
        daily_stats = cursor.fetchall()
        
        # Cargar eventos específicos de la aplicación (últimos 50)
        cursor.execute("""
            SELECT feature, details, timestamp 
            FROM app_specific_events 
            ORDER BY timestamp DESC 
            LIMIT 50
        """)
        
        app_events = []
        for row in cursor.fetchall():
            try:
                details_json = json.loads(row[1]) if row[1] else {}
                details_str = ", ".join([f"{k}: {v}" for k, v in details_json.items()]) if isinstance(details_json, dict) else str(details_json)
            except:
                details_str = str(row[1])
                
            app_events.append({
                'feature': row[0],
                'details': details_str,
                'timestamp': row[2]
            })
        
        connection.close()
        
        # Preparar datos para la plantilla
        stats = {
            'total_views': total_views,
            'unique_sessions': unique_sessions,
            'device_breakdown': device_breakdown,
            'os_breakdown': os_breakdown,
            'browser_breakdown': browser_breakdown,
            'feature_usage': feature_usage,
            'daily_stats': daily_stats
        }
        
        analytics_logger.info(f"Mostrando estadísticas: {total_views} vistas, {unique_sessions} sesiones")
        
        # Renderizar stats.html
        return render_template("admin/stats.html", stats=stats, app_events=app_events)
        
    except Exception as e:
        analytics_logger.error(f"Error al mostrar estadísticas: {str(e)}", exc_info=True)
        return f"Error: {str(e)}", 500