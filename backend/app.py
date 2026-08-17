from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config

# Load .env file
from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Path to frontend folder (sibling of backend/ or root fallback)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend'))
if not os.path.exists(FRONTEND_DIR):
    FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

# Ensure directories exist (use /tmp on Vercel where filesystem is read-only)
_tmp = os.environ.get('VERCEL')
os.makedirs(os.path.join(BASE_DIR, 'models'), exist_ok=True) if not _tmp else None
os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True) if not _tmp else None
os.makedirs('/tmp/uploads' if _tmp else os.path.join(BASE_DIR, 'uploads'), exist_ok=True)

def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)
    CORS(app)

    # Initialize SQLite database
    import database_sqlite
    database_sqlite.init_db()

    # Register blueprints
    from routes import student_routes, analysis_routes, job_routes, recommend_routes, application_routes, auth_routes
    app.register_blueprint(student_routes.bp)
    app.register_blueprint(analysis_routes.bp)
    app.register_blueprint(job_routes.bp)
    app.register_blueprint(recommend_routes.bp)
    app.register_blueprint(application_routes.bp)
    app.register_blueprint(auth_routes.bp)

    # Serve frontend HTML files (must NOT match /api/... routes)
    @app.route('/')
    def index():
        return send_from_directory(FRONTEND_DIR, 'index.html')

    @app.route('/<path:filename>')
    def frontend(filename):
        # Don't intercept API calls
        if filename.startswith('api/'):
            from flask import abort
            abort(404)
        return send_from_directory(FRONTEND_DIR, filename)

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "="*60)
    print(f"[OK] Backend running on http://0.0.0.0:{port}")
    print(f"[OK] Serving frontend from {FRONTEND_DIR}")
    print("[OK] Using SQLite database")
    print("="*60 + "\n")
    app.run(debug=False, host='0.0.0.0', port=port)
