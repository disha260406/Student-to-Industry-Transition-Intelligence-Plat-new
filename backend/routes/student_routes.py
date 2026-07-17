from flask import Blueprint, request, jsonify, send_from_directory
from database_sqlite import execute_query, execute_update
from ml.github_analyzer import GitHubAnalyzer
import os, json, uuid

bp = Blueprint('students', __name__, url_prefix='/api/students')
github_analyzer = GitHubAnalyzer()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_file(file_obj, prefix=''):
    if not file_obj or file_obj.filename == '':
        return None
    ext = os.path.splitext(file_obj.filename)[1].lower()
    if ext != '.pdf':
        return None
    stored_name = f"{prefix}_{uuid.uuid4().hex}{ext}"
    file_obj.save(os.path.join(UPLOAD_DIR, stored_name))
    return stored_name

@bp.route('/uploads/<filename>', methods=['GET'])
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@bp.route('/', methods=['GET'])
def get_students():
    students = execute_query("SELECT id, name, email, branch, cgpa, skills, github_url, internships_count, projects_count, certifications_count, created_at FROM students")
    return jsonify({'success': True, 'count': len(students) if students else 0, 'data': students or []})

@bp.route('/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = execute_query("SELECT id, name, email, branch, cgpa, skills, github_url, internships_count, projects_count, certifications_count, created_at FROM students WHERE id = ?", (student_id,))
    if student:
        return jsonify({'success': True, 'data': student[0]})
    return jsonify({'success': False, 'error': 'Student not found'}), 404

@bp.route('/add-student', methods=['POST'])
def add_student():
    try:
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = request.form.to_dict()
            for key in ['certs_data', 'internships_data', 'projects_data']:
                if key in data:
                    try: data[key] = json.loads(data[key])
                    except: data[key] = []
        else:
            data = request.json

        for field in ['name', 'email', 'branch', 'cgpa']:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400

        cgpa = float(data['cgpa'])
        if not (0 <= cgpa <= 10):
            return jsonify({'success': False, 'error': 'CGPA must be between 0 and 10'}), 400

        student_id = execute_update(
            """INSERT INTO students (name, email, branch, cgpa, skills, github_url,
               internships_count, projects_count, certifications_count)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (data['name'], data['email'], data['branch'], cgpa,
             data.get('skills', ''), data.get('github_url', ''),
             data.get('internships_count', 0), data.get('projects_count', 0),
             data.get('certifications_count', 0))
        )

        if not student_id:
            return jsonify({'success': False, 'error': 'Failed to add student'}), 500

        # Save certificates
        certs = data.get('certs_data', [])
        if isinstance(certs, str):
            try: certs = json.loads(certs)
            except: certs = []
        for i, c in enumerate(certs):
            if not c.get('name'): continue
            stored = save_file(request.files.get(f'cert_file_{i+1}'), f'cert_{student_id}_{i+1}')
            execute_update(
                'INSERT INTO student_certificates (student_id, name, file_name, has_file) VALUES (?,?,?,?)',
                (student_id, c.get('name', ''), stored or c.get('file_name', ''), 1 if stored else 0)
            )

        # Save internships
        internships = data.get('internships_data', [])
        if isinstance(internships, str):
            try: internships = json.loads(internships)
            except: internships = []
        for i, intern in enumerate(internships):
            if not (intern.get('company') or intern.get('role')): continue
            stored = save_file(request.files.get(f'intern_cert_{i+1}'), f'intern_{student_id}_{i+1}')
            execute_update(
                'INSERT INTO student_internships (student_id, company, role, duration, has_certificate, cert_name) VALUES (?,?,?,?,?,?)',
                (student_id, intern.get('company', ''), intern.get('role', ''), intern.get('duration', ''),
                 1 if stored else 0, stored or intern.get('cert_name', ''))
            )

        # Save projects
        projects = data.get('projects_data', [])
        if isinstance(projects, str):
            try: projects = json.loads(projects)
            except: projects = []
        for p in projects:
            if p.get('name'):
                execute_update('INSERT INTO student_projects (student_id, name) VALUES (?,?)',
                               (student_id, p.get('name', '')))

        return jsonify({
            'success': True, 'message': 'Student added successfully',
            'student_id': student_id,
            'data': {'id': student_id, 'name': data['name'], 'email': data['email'],
                     'branch': data['branch'], 'cgpa': cgpa}
        }), 201

    except ValueError as e:
        return jsonify({'success': False, 'error': f'Invalid data format: {str(e)}'}), 400
    except Exception as e:
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'success': False, 'error': 'This email is already registered. Please use a different email.'}), 400
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@bp.route('/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    try:
        data = request.json
        update_fields, params = [], []
        for field in ['name', 'email', 'branch', 'cgpa', 'skills', 'internships_count', 'projects_count', 'certifications_count']:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        if not update_fields:
            return jsonify({'success': False, 'error': 'No fields to update'}), 400
        params.append(student_id)
        execute_update(f"UPDATE students SET {', '.join(update_fields)} WHERE id = ?", tuple(params))
        return jsonify({'success': True, 'message': 'Student updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@bp.route('/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        execute_update("DELETE FROM students WHERE id = ?", (student_id,))
        return jsonify({'success': True, 'message': 'Student deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@bp.route('/<int:student_id>/portfolio', methods=['GET'])
def get_portfolio(student_id):
    try:
        certs = execute_query('SELECT * FROM student_certificates WHERE student_id = ?', (student_id,))
        internships = execute_query('SELECT * FROM student_internships WHERE student_id = ?', (student_id,))
        projects = execute_query('SELECT * FROM student_projects WHERE student_id = ?', (student_id,))
        return jsonify({'success': True, 'data': {
            'certificates': certs or [],
            'internships': internships or [],
            'projects': projects or []
        }})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/verify-github', methods=['POST'])
def verify_github():
    try:
        data = request.json
        if 'github_url' not in data or 'skills' not in data:
            return jsonify({'success': False, 'error': 'Missing github_url or skills'}), 400
        result = github_analyzer.verify_skills(data['github_url'], data['skills'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Verification error: {str(e)}'}), 500
