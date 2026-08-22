from flask import Blueprint, request, jsonify
from database_sqlite import execute_query, execute_update

bp = Blueprint('jobs', __name__, url_prefix='/api/jobs')

@bp.route('/', methods=['GET'])
def get_jobs():
    """Get all job roles, optionally filtered by branch"""
    branch = request.args.get('branch')
    
    if branch:
        jobs = execute_query("SELECT * FROM job_roles WHERE is_active = 1 AND branch = ?", (branch,))
    else:
        jobs = execute_query("SELECT * FROM job_roles WHERE is_active = 1")
    
    return jsonify({
        'success': True,
        'count': len(jobs) if jobs else 0,
        'data': jobs or []
    })

@bp.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Get job by ID"""
    job = execute_query("SELECT * FROM job_roles WHERE id = ?", (job_id,))
    if job:
        return jsonify({
            'success': True,
            'data': job[0]
        })
    return jsonify({
        'success': False,
        'error': 'Job not found'
    }), 404

@bp.route('/', methods=['POST'])
def create_job():
    """Create a new job role"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['title', 'company', 'required_skills']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        query = """INSERT INTO job_roles 
                   (title, company, branch, description, required_skills, preferred_skills, 
                    min_cgpa, experience_required, salary_range, location, job_type) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        
        params = (
            data['title'],
            data['company'],
            data.get('branch', ''),
            data.get('description', ''),
            data['required_skills'],
            data.get('preferred_skills', ''),
            data.get('min_cgpa', 0),
            data.get('experience_required', 'Fresher'),
            data.get('salary_range', ''),
            data.get('location', ''),
            data.get('job_type', 'Full-time')
        )
        
        job_id = execute_update(query, params)
        
        if job_id:
            return jsonify({
                'success': True,
                'message': 'Job created successfully',
                'job_id': job_id
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create job'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500
