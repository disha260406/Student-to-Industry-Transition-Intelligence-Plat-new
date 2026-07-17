from flask import Blueprint, request, jsonify
from ml.job_recommender import recommend_jobs

bp = Blueprint('recommend', __name__, url_prefix='/api')

@bp.route('/recommend-jobs', methods=['POST'])
def recommend():
    data = request.get_json()

    branch = data.get('branch', '').strip()
    skills = data.get('skills', '').strip()

    if not branch or not skills:
        return jsonify({'success': False, 'error': 'branch and skills are required'}), 400

    try:
        results = recommend_jobs(branch, skills)
        return jsonify({'success': True, 'recommendations': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
