from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config

# Load .env file
from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Path to frontend folder (sibling of backend/)
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)
    CORS(app)

    # Initialize SQLite database
    import database_sqlite

    # Register blueprints
    from routes import student_routes, analysis_routes, job_routes, recommend_routes, application_routes
    app.register_blueprint(student_routes.bp)
    app.register_blueprint(analysis_routes.bp)
    app.register_blueprint(job_routes.bp)
    app.register_blueprint(recommend_routes.bp)
    app.register_blueprint(application_routes.bp)

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
    print("\n" + "="*60)
    print("✅ Backend running on http://localhost:5000")
    print("✅ Serving frontend from /frontend")
    print("✅ Using SQLite database (no MySQL needed)")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
