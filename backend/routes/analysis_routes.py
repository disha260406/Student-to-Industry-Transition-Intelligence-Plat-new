from flask import Blueprint, request, jsonify
from ml.skill_matcher import SkillMatcher
from ml.placement_predictor import PlacementPredictor
from ml.recommendation_engine import RecommendationEngine

bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

# Initialize ML components
skill_matcher = SkillMatcher()
placement_predictor = PlacementPredictor()
recommendation_engine = RecommendationEngine()

@bp.route('/match/<int:student_id>/<int:job_id>', methods=['GET'])
def match_student_job(student_id, job_id):
    """
    Match a student with a specific job using TF-IDF and Cosine Similarity
    Returns skill match percentage and missing skills
    """
    try:
        result = skill_matcher.match(student_id, job_id)
        return jsonify({
            'success': True,
            'data': result
        })
    except IndexError:
        return jsonify({
            'success': False,
            'error': 'Student or job not found'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Analysis error: {str(e)}'
        }), 500

@bp.route('/predict-placement/<int:student_id>', methods=['GET'])
def predict_placement(student_id):
    """
    Predict placement probability for a student
    Returns placement probability percentage and readiness level
    """
    try:
        prediction = placement_predictor.predict(student_id)
        return jsonify({
            'success': True,
            'data': prediction
        })
    except IndexError:
        return jsonify({
            'success': False,
            'error': 'Student not found'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Prediction error: {str(e)}'
        }), 500

@bp.route('/skill-gap/<int:student_id>', methods=['GET'])
def analyze_skill_gap(student_id):
    """
    Comprehensive skill gap analysis across all active jobs
    Returns missing skills, match percentages, and job-specific gaps
    """
    try:
        gaps = skill_matcher.identify_gaps(student_id)
        
        # Calculate summary statistics
        if gaps:
            avg_match = sum(g['match_percentage'] for g in gaps) / len(gaps)
            best_match = gaps[0] if gaps else None
            
            # Aggregate all missing skills
            all_missing = set()
            for gap in gaps:
                all_missing.update(gap['missing_skills'])
            
            # Generate friendly summary message
            if avg_match >= 70:
                summary_message = "🌟 Excellent! You're well-prepared for most positions!"
            elif avg_match >= 50:
                summary_message = "👍 Good progress! A few more skills will boost your opportunities."
            elif avg_match >= 30:
                summary_message = "💪 You're on the right track! Focus on the key skills below."
            else:
                summary_message = "📚 Let's build your skills! Start with the most in-demand ones."
        else:
            avg_match = 0
            best_match = None
            all_missing = set()
            summary_message = "No active job postings available at the moment."
        
        return jsonify({
            'success': True,
            'data': {
                'student_id': student_id,
                'summary_message': summary_message,
                'jobs_checked': len(gaps),
                'your_average_match': round(avg_match, 2),
                'best_opportunity': best_match,
                'skills_to_focus_on': len(all_missing),
                'recommended_skills': sorted(list(all_missing)),
                'all_opportunities': gaps
            }
        })
    except IndexError:
        return jsonify({
            'success': False,
            'error': 'Student not found'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Analysis error: {str(e)}'
        }), 500

@bp.route('/recommendations/<int:student_id>', methods=['GET'])
def get_recommendations(student_id):
    """
    Get personalized skill recommendations with courses, certifications, and projects
    """
    try:
        # Get skill recommendations from matcher
        skill_recs = skill_matcher.get_recommendations(student_id)
        
        # Get learning resources for high priority skills
        learning_resources = []
        for skill in skill_recs['high_priority_skills'][:5]:  # Top 5 high priority
            resources = recommendation_engine.get_skill_recommendations(skill)
            if resources:
                learning_resources.append(resources)
        
        # Create friendly message
        priority_count = len(skill_recs['high_priority_skills'])
        if priority_count > 0:
            action_message = f"🎯 Focus on these {priority_count} skills to maximize your job opportunities!"
        else:
            action_message = "🌟 Great job! You have most of the in-demand skills!"
        
        return jsonify({
            'success': True,
            'data': {
                'student_id': student_id,
                'action_message': action_message,
                'your_learning_path': skill_recs,
                'courses_and_resources': learning_resources
            }
        })
    except IndexError:
        return jsonify({
            'success': False,
            'error': 'Student not found'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Recommendation error: {str(e)}'
        }), 500

@bp.route('/batch-match/<int:student_id>', methods=['GET'])
def batch_match_student(student_id):
    """
    Match student against all active jobs
    Returns sorted list of job matches
    """
    try:
        results = skill_matcher.batch_match(student_id)
        return jsonify({
            'success': True,
            'data': {
                'student_id': student_id,
                'total_jobs': len(results),
                'matches': results
            }
        })
    except IndexError:
        return jsonify({
            'success': False,
            'error': 'Student not found'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Batch match error: {str(e)}'
        }), 500

@bp.route('/comprehensive/<int:student_id>', methods=['GET'])
def comprehensive_analysis(student_id):
    """
    Complete analysis: placement prediction + skill gaps + recommendations
    """
    try:
        # Get all analyses
        prediction = placement_predictor.predict(student_id)
        gaps = skill_matcher.identify_gaps(student_id)
        recommendations = skill_matcher.get_recommendations(student_id)
        
        # Get learning resources for top missing skills
        learning_resources = []
        for skill in recommendations['high_priority_skills'][:3]:
            resources = recommendation_engine.get_skill_recommendations(skill)
            if resources:
                learning_resources.append(resources)
        
        return jsonify({
            'success': True,
            'data': {
                'student_id': student_id,
                'placement_prediction': prediction,
                'skill_gap_summary': {
                    'total_jobs_analyzed': len(gaps),
                    'best_match': gaps[0] if gaps else None,
                    'average_match': round(sum(g['match_percentage'] for g in gaps) / len(gaps), 2) if gaps else 0
                },
                'recommendations': recommendations,
                'learning_resources': learning_resources
            }
        })
    except IndexError:
        return jsonify({
            'success': False,
            'error': 'Student not found'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Comprehensive analysis error: {str(e)}'
        }), 500

@bp.route('/skill-recommendations/<skill>', methods=['GET'])
def get_skill_learning_resources(skill):
    """
    Get learning resources (courses, certifications, projects) for a specific skill
    """
    try:
        resources = recommendation_engine.get_skill_recommendations(skill)
        return jsonify({
            'success': True,
            'data': resources
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Resource lookup error: {str(e)}'
        }), 500


@bp.route('/curriculum-gap', methods=['POST'])
def analyze_curriculum_gap():
    """
    Analyze college program structure PDF.
    Extracts subjects, compares with industry requirements,
    returns: what's taught, what industry expects, skill gaps + level gaps.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        f = request.files['file']
        if not f.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Only PDF files are accepted'}), 400

        from ml.curriculum_analyzer import analyze_curriculum_pdf
        result = analyze_curriculum_pdf(f.read())
        return jsonify(result)

    except ImportError as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Analysis error: {str(e)}'}), 500

@bp.route('/save-syllabus/<int:student_id>', methods=['POST'])
def save_syllabus(student_id):
    """Save uploaded syllabus PDF to student record."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file'}), 400
        f = request.files['file']
        pdf_bytes = f.read()
        from database_sqlite import execute_update
        execute_update("UPDATE students SET syllabus_pdf=? WHERE id=?", (pdf_bytes, student_id))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/curriculum-gap/<int:student_id>', methods=['GET'])
def analyze_curriculum_by_student(student_id):
    """Analyze syllabus + GitHub skills for a student."""
    try:
        from database_sqlite import execute_query
        rows = execute_query(
            "SELECT syllabus_pdf, github_url, skills FROM students WHERE id=?",
            (student_id,)
        )
        if not rows:
            return jsonify({'success': False, 'error': 'Student not found'})

        student = rows[0]
        pdf_bytes = student.get('syllabus_pdf')
        github_url = student.get('github_url', '')
        claimed_skills = student.get('skills', '')

        if not pdf_bytes:
            return jsonify({'success': False, 'error': 'No syllabus uploaded for this student'})

        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode()

        from ml.curriculum_analyzer import analyze_curriculum_pdf, extract_curriculum, compare_with_industry, extract_text_from_pdf

        # Step 1: Extract topics from PDF
        text = extract_text_from_pdf(pdf_bytes)
        if not text.strip():
            raise ValueError("Could not extract text from PDF.")
        curriculum_topics = extract_curriculum(text)

        # Step 2: Add skills from GitHub repos
        if github_url and github_url.strip():
            try:
                from ml.github_analyzer import GitHubAnalyzer
                analyzer = GitHubAnalyzer()
                gh = analyzer.verify_skills(github_url, claimed_skills or 'python')
                if gh.get('success'):
                    # Add verified GitHub skills to curriculum topics
                    for s in gh.get('verified_skills', []):
                        skill = s['skill'].lower()
                        if skill not in curriculum_topics:
                            curriculum_topics[skill] = 'Intermediate'
                    # Also add detected languages
                    for lang in gh.get('languages_used', {}).keys():
                        if lang not in curriculum_topics:
                            curriculum_topics[lang] = 'Basic'
            except Exception:
                pass  # GitHub fetch failed, continue with PDF only

        # Step 3: Add manually entered skills
        if claimed_skills:
            for s in claimed_skills.split(','):
                s = s.strip().lower()
                if s and s not in curriculum_topics:
                    curriculum_topics[s] = 'Basic'

        # Step 4: Compare with industry
        industry_comparison = compare_with_industry(curriculum_topics)
        best_domain = max(industry_comparison, key=lambda d: industry_comparison[d]['coverage_percent'])

        return jsonify({
            'success': True,
            'topics_found': len(curriculum_topics),
            'curriculum_topics': curriculum_topics,
            'industry_comparison': industry_comparison,
            'best_matching_domain': best_domain,
            'best_coverage': industry_comparison[best_domain]['coverage_percent'],
            'sources': {
                'pdf': True,
                'github': bool(github_url),
                'manual_skills': bool(claimed_skills)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
