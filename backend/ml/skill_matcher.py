from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from database_sqlite import execute_query

class SkillMatcher:
    def __init__(self):
        # TF-IDF Vectorizer with custom parameters for skill matching
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            token_pattern=r'(?u)\b[a-zA-Z][a-zA-Z0-9+#.]*\b',  # Handle skills like C++, C#, .NET
            stop_words=None,  # Don't remove stop words for technical skills
            max_features=1000
        )
    
    def _normalize_skills(self, skills_text):
        """Normalize skill text for better matching"""
        if not skills_text:
            return ""
        # Convert to lowercase and clean up
        skills_text = skills_text.lower().strip()
        # Replace common variations
        replacements = {
            'javascript': 'javascript js',
            'typescript': 'typescript ts',
            'python': 'python py',
            'c++': 'cpp cplusplus',
            'c#': 'csharp',
            '.net': 'dotnet',
            'node.js': 'nodejs node',
            'react.js': 'reactjs react',
            'vue.js': 'vuejs vue',
            'angular.js': 'angularjs angular'
        }
        for old, new in replacements.items():
            skills_text = skills_text.replace(old, new)
        return skills_text
    
    def _parse_skills(self, skills_text):
        """Parse comma-separated skills into a clean set"""
        if not skills_text:
            return set()
        skills = [s.strip().lower() for s in skills_text.split(',') if s.strip()]
        return set(skills)
    
    def match(self, student_id, job_id, student_data=None, job_data=None, github_verified_skills=None):
        """
        Match student skills with job requirements using TF-IDF and Cosine Similarity
        Includes GitHub verification for skill validation
        
        Returns:
            dict: Match results with percentage, missing skills, and recommendations
        """
        # Fetch student and job data if not provided
        if student_data is not None:
            student = student_data
        else:
            students = execute_query("SELECT * FROM students WHERE id = ?", (student_id,))
            if not students:
                raise ValueError(f"Student with id {student_id} not found")
            student = students[0]

        if job_data is not None:
            job = job_data
        else:
            jobs = execute_query("SELECT * FROM job_roles WHERE id = ?", (job_id,))
            if not jobs:
                raise ValueError(f"Job with id {job_id} not found")
            job = jobs[0]
        
        # Get skills
        student_skills_raw = student.get('skills', '')
        required_skills_raw = job.get('required_skills', '')
        preferred_skills_raw = job.get('preferred_skills', '')
        
        # Parse skills into sets
        student_skills_set = self._parse_skills(student_skills_raw)
        required_skills_set = self._parse_skills(required_skills_raw)
        preferred_skills_set = self._parse_skills(preferred_skills_raw)
        
        # Get GitHub verified skills if available and not passed in
        if github_verified_skills is None:
            github_verified_skills = set()
            if student.get('github_url'):
                from ml.github_analyzer import GitHubAnalyzer
                analyzer = GitHubAnalyzer()
                try:
                    verification = analyzer.verify_skills(student.get('github_url'), student_skills_raw)
                    if verification and verification.get('success'):
                        github_verified_skills = set([s['skill'].lower() for s in verification.get('verified_skills', [])])
                except Exception:
                    pass  # Continue without GitHub verification if it fails
        
        # Normalize for TF-IDF
        student_skills_text = self._normalize_skills(student_skills_raw)
        required_skills_text = self._normalize_skills(required_skills_raw)
        
        # Calculate TF-IDF based similarity
        if student_skills_text and required_skills_text:
            try:
                vectors = self.vectorizer.fit_transform([student_skills_text, required_skills_text])
                tfidf_similarity = float(cosine_similarity(vectors[0:1], vectors[1:2])[0][0])
            except Exception:
                tfidf_similarity = 0.0
        else:
            tfidf_similarity = 0.0
        
        # Calculate exact match percentage with GitHub verification bonus
        if required_skills_set:
            matched_skills = student_skills_set.intersection(required_skills_set)
            verified_matched_skills = matched_skills.intersection(github_verified_skills)
            
            # Base match percentage
            exact_match_percentage = (len(matched_skills) / len(required_skills_set)) * 100
            
            # Add bonus for GitHub-verified skills (up to 15% bonus)
            if matched_skills:
                verification_bonus = (len(verified_matched_skills) / len(matched_skills)) * 15
            else:
                verification_bonus = 0
        else:
            exact_match_percentage = 0.0
            verification_bonus = 0
            matched_skills = set()
            verified_matched_skills = set()
        
        # Combine both scores (weighted average) + GitHub verification bonus
        combined_score = min(100.0, (tfidf_similarity * 40) + (exact_match_percentage * 0.6) + verification_bonus)
        
        # Identify missing skills
        missing_required = list(required_skills_set - student_skills_set)
        missing_preferred = list(preferred_skills_set - student_skills_set) if preferred_skills_set else []
        matched_skills_list = list(matched_skills)
        verified_skills_list = list(verified_matched_skills)
        
        # Check CGPA eligibility
        student_cgpa = float(student.get('cgpa', 0))
        min_cgpa = float(job.get('min_cgpa', 0))
        cgpa_eligible = student_cgpa >= min_cgpa
        
        # Determine match level
        if combined_score >= 80 and cgpa_eligible:
            match_level = 'Excellent Match'
        elif combined_score >= 60 and cgpa_eligible:
            match_level = 'Good Match'
        elif combined_score >= 40:
            match_level = 'Moderate Match'
        else:
            match_level = 'Poor Match'
        
        # Generate message with GitHub verification context
        github_context = ""
        if verified_skills_list:
            github_context = f" We verified {len(verified_skills_list)} of these through your GitHub repos."
            
        if match_level == 'Excellent Match':
            message = f"You are a great fit for this role! You have {len(matched_skills_list)} of {len(required_skills_set)} required skills.{github_context}"
        elif match_level == 'Good Match':
            message = f"You are a solid candidate. Focus on: {', '.join(missing_required[:2]) if missing_required else 'refining current skills'}.{github_context}"
        elif match_level == 'Moderate Match':
            message = f"You have potential. You need to learn: {', '.join(missing_required[:3]) if missing_required else 'more role-specific skills'}."
        else:
            message = f"Significant skill gap. Learn {', '.join(missing_required[:3]) if missing_required else 'required skills'} to qualify."
        
        return {
            'student_id': student_id,
            'job_id': job_id,
            'job_title': job.get('title'),
            'company': job.get('company'),
            'branch': job.get('branch'),
            'match_percentage': round(combined_score, 2),
            'skill_match_percentage': round(combined_score, 2),
            'match_level': match_level,
            'tfidf_similarity': round(tfidf_similarity * 100, 2),
            'exact_match_percentage': round(exact_match_percentage, 2),
            'matched_skills': matched_skills_list,
            'verified_matched_skills': verified_skills_list,
            'github_verification_bonus': round(verification_bonus, 2),
            'missing_required_skills': missing_required,
            'missing_preferred_skills': missing_preferred,
            'cgpa_eligible': cgpa_eligible,
            'student_cgpa': student_cgpa,
            'min_cgpa_required': min_cgpa,
            'message': message
        }
    
    def identify_gaps(self, student_id):
        """
        Identify overall skill gaps across all relevant jobs in the database
        
        Returns:
            list: Gaps for each job role
        """
        student = execute_query("SELECT * FROM students WHERE id = ?", (student_id,))[0]
        jobs = execute_query("SELECT * FROM job_roles WHERE is_active = 1")
        
        gaps = []
        for job in jobs:
            match_result = self.match(student_id, job['id'], student_data=student, job_data=job, github_verified_skills=set())
            
            # Only include jobs with meaningful gap analysis
            if match_result['missing_required_skills']:
                gaps.append({
                    'job_id': job['id'],
                    'job_title': job['title'],
                    'company': job['company'],
                    'match_percentage': match_result['match_percentage'],
                    'missing_skills': match_result['missing_required_skills'],
                    'preferred_missing': match_result['missing_preferred_skills'],
                    'skills_to_learn_count': len(match_result['missing_required_skills']),
                    'match_level': match_result['match_level']
                })
        
        # Sort by match percentage (highest first)
        gaps.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return gaps
    
    def get_recommendations(self, student_id):
        """
        Generate actionable learning recommendations based on skill gaps
        
        Returns:
            dict: Categorized recommendations with priority
        """
        gaps = self.identify_gaps(student_id)
        
        # Count frequency of missing skills
        missing_freq = {}
        for gap in gaps:
            for skill in gap['missing_skills']:
                missing_freq[skill] = missing_freq.get(skill, 0) + 1
        
        # Sort by frequency (most in-demand first)
        sorted_skills = sorted(missing_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Categorize by priority
        high_priority = [skill for skill, count in sorted_skills if count >= 3]
        medium_priority = [skill for skill, count in sorted_skills if count == 2]
        low_priority = [skill for skill, count in sorted_skills if count == 1]
        
        # Find best matching jobs
        best_matches = [g for g in gaps if g['match_percentage'] >= 60][:5]
        
        return {
            'high_priority_skills': high_priority[:5],
            'medium_priority_skills': medium_priority[:5],
            'low_priority_skills': low_priority[:5],
            'best_matched_jobs': best_matches,
            'total_jobs_analyzed': len(gaps),
            'action_plan': self._generate_action_plan(high_priority, medium_priority, best_matches)
        }
    
    def _generate_action_plan(self, high_priority, medium_priority, best_matches):
        """Generate human-readable action plan"""
        recommendations = []
        
        if high_priority:
            recommendations.append(f"Focus on learning {', '.join(high_priority[:3])} to unlock most jobs")
        
        if medium_priority:
            recommendations.append(f"After that, look at {', '.join(medium_priority[:3])}")
        
        if best_matches:
            recommendations.append(f"You can already apply to {len(best_matches)} jobs, including {', '.join([j['job_title'] for j in best_matches[:2]])}")
        else:
            recommendations.append("Keep building. You'll get there.")
        
        return recommendations
    
    def batch_match(self, student_id):
        """
        Match student against all active jobs
        
        Returns:
            list: Match results for all jobs sorted by match percentage
        """
        students = execute_query("SELECT * FROM students WHERE id = ?", (student_id,))
        if not students:
            return []
        student = students[0]

        # Get GitHub verified skills once for the batch
        github_verified_skills = set()
        student_skills_raw = student.get('skills', '')
        if student.get('github_url'):
            from ml.github_analyzer import GitHubAnalyzer
            analyzer = GitHubAnalyzer()
            try:
                verification = analyzer.verify_skills(student.get('github_url'), student_skills_raw)
                if verification and verification.get('success'):
                    github_verified_skills = set([s['skill'].lower() for s in verification.get('verified_skills', [])])
            except Exception:
                pass

        jobs = execute_query("SELECT * FROM job_roles WHERE is_active = 1")
        
        results = []
        for job in jobs:
            match_result = self.match(
                student_id, 
                job['id'], 
                student_data=student, 
                job_data=job, 
                github_verified_skills=github_verified_skills
            )
            results.append(match_result)
        
        # Sort by match percentage
        results.sort(key=lambda x: x.get('match_percentage', 0), reverse=True)
        
        return results
