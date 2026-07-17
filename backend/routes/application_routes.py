from flask import Blueprint, request, jsonify
from database_sqlite import execute_query, execute_update

bp = Blueprint('applications', __name__, url_prefix='/api/applications')

@bp.route('/<int:student_id>', methods=['GET'])
def get_applications(student_id):
    rows = execute_query(
        "SELECT * FROM applications WHERE student_id = ? ORDER BY id DESC",
        (student_id,)
    )
    return jsonify({'success': True, 'data': rows or []})

@bp.route('/apply', methods=['POST'])
def apply():
    data = request.get_json()
    student_id = data.get('student_id')
    job_role   = data.get('job_role', '').strip()
    company    = data.get('company', '').strip()

    if not student_id or not job_role or not company:
        return jsonify({'success': False, 'error': 'student_id, job_role and company are required'}), 400

    # Prevent duplicate
    existing = execute_query(
        "SELECT id FROM applications WHERE student_id=? AND job_role=? AND company=?",
        (student_id, job_role, company)
    )
    if existing:
        return jsonify({'success': True, 'message': 'Already applied', 'id': existing[0]['id']})

    app_id = execute_update(
        "INSERT INTO applications (student_id, job_role, company, field, match_percentage, status, applied_date) VALUES (?,?,?,?,?,?,?)",
        (
            student_id,
            job_role,
            company,
            data.get('field', ''),
            float(data.get('match_percentage', 0)),
            'Applied',
            data.get('applied_date', '')
        )
    )
    return jsonify({'success': True, 'id': app_id}), 201

@bp.route('/status', methods=['PUT'])
def update_status():
    data = request.get_json()
    app_id = data.get('id')
    status = data.get('status')
    if not app_id or not status:
        return jsonify({'success': False, 'error': 'id and status required'}), 400
    execute_update("UPDATE applications SET status=? WHERE id=?", (status, app_id))
    return jsonify({'success': True})

@bp.route('/<int:app_id>', methods=['DELETE'])
def delete_application(app_id):
    execute_update("DELETE FROM applications WHERE id=?", (app_id,))
    return jsonify({'success': True})
