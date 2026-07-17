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
    
    def match(self, student_id, job_id):
        """
        Match student skills with job requirements using TF-IDF and Cosine Similarity
        Includes GitHub verification for skill validation
        
        Returns:
            dict: Match results with percentage, missing skills, and recommendations
        """
        # Fetch student and job data
        student = execute_query("SELECT * FROM students WHERE id = ?", (student_id,))[0]
        job = execute_query("SELECT * FROM job_roles WHERE id = ?", (job_id,))[0]
        
        # Get skills
        student_skills_raw = student.get('skills', '')
        required_skills_raw = job.get('required_skills', '')
        preferred_skills_raw = job.get('preferred_skills', '')
        
        # Parse skills into sets
        student_skills_set = self._parse_skills(student_skills_raw)
        required_skills_set = self._parse_skills(required_skills_raw)
        preferred_skills_set = self._parse_skills(preferred_skills_raw)
        
        # Get GitHub verified skills if available
        github_verified_skills = set()
        if student.get('github_url'):
            from ml.github_analyzer import GitHubAnalyzer
            analyzer = GitHubAnalyzer()
            try:
                verification = analyzer.verify_skills(student.get('github_url'), student_skills_raw)
                if verification['success']:
                    github_verified_skills = set([s['skill'].lower() for s in verification['verified_skills']])
            except:
                pass  # Continue without GitHub verification if it fails
        
        # Normalize for TF-IDF
        student_skills_text = self._normalize_skills(student_skills_raw)
        required_skills_text = self._normalize_skills(required_skills_raw)
        
        # Calculate TF-IDF based similarity
        if student_skills_text and required_skills_text:
            try:
                vectors = self.vectorizer.fit_transform([student_skills_text, required_skills_text])
                tfidf_similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            except:
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
        combined_score = (tfidf_similarity * 40) + (exact_match_percentage * 0.6) + verification_bonus
        
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
        
        if combined_score >= 80 and cgpa_eligible:
            friendly_message = f"Strong match for {job.get('company')}. Your profile fits what they're looking for.{github_context}"
        elif combined_score >= 60 and cgpa_eligible:
            friendly_message = f"You're qualified for this role. Pick up a couple more skills and you'll be even stronger.{github_context}"
        elif combined_score >= 40:
            friendly_message = f"You've got some of what they need. Work on the missing skills to boost your chances.{github_context}"
        else:
            friendly_message = f"This one's a stretch right now. Focus on the skills below to get there.{github_context}"
        
        return {
            'student_id': student_id,
            'student_name': student.get('name'),
            'job_id': job_id,
            'job_title': job.get('title'),
            'company': job.get('company'),
            'match_percentage': round(combined_score, 2),
            'match_level': match_level,
            'friendly_message': friendly_message,
            'your_skills': matched_skills_list,
            'github_verified_skills': verified_skills_list,
            'skills_you_have': len(matched_skills_list),
            'skills_verified_on_github': len(verified_skills_list),
            'skills_to_learn': missing_required,
            'bonus_skills': missing_preferred,
            'total_skills_needed': len(required_skills_set),
            'your_cgpa': student_cgpa,
            'required_cgpa': min_cgpa,
            'cgpa_eligible': cgpa_eligible,
            'cgpa_message': f"✅ Your CGPA meets the requirement!" if cgpa_eligible else f"⚠️ CGPA requirement: {min_cgpa} (You have: {student_cgpa})",
            'github_bonus_applied': round(verification_bonus, 2) if verification_bonus > 0 else 0
        }
    
    def identify_gaps(self, student_id):
        """
        Identify skill gaps across all active job roles
        
        Returns:
            list: Skill gaps for each job with match percentages
        """
        student = execute_query("SELECT * FROM students WHERE id = ?", (student_id,))[0]
        jobs = execute_query("SELECT * FROM job_roles WHERE is_active = 1")
        
        student_skills_set = self._parse_skills(student.get('skills', ''))
        
        gaps = []
        for job in jobs:
            required_skills_set = self._parse_skills(job.get('required_skills', ''))
            
            if required_skills_set:
                matched = student_skills_set.intersection(required_skills_set)
                missing = required_skills_set - student_skills_set
                match_percentage = (len(matched) / len(required_skills_set)) * 100
                
                gaps.append({
                    'job_id': job['id'],
                    'job_title': job['title'],
                    'company': job['company'],
                    'match_percentage': round(match_percentage, 2),
                    'matched_skills': list(matched),
                    'missing_skills': list(missing),
                    'total_required': len(required_skills_set)
                })
        
        # Sort by match percentage (descending)
        gaps.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return gaps
    
    def get_recommendations(self, student_id):
        """
        Generate skill recommendations based on gap analysis
        
        Returns:
            dict: Prioritized skill recommendations
        """
        gaps = self.identify_gaps(student_id)
        
        # Count frequency of missing skills across all jobs
        skill_frequency = {}
        for gap in gaps:
            for skill in gap['missing_skills']:
                skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
        
        # Sort skills by frequency (most demanded first)
        sorted_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)
        
        # Categorize by priority
        high_priority = [skill for skill, freq in sorted_skills if freq >= len(gaps) * 0.5]
        medium_priority = [skill for skill, freq in sorted_skills if len(gaps) * 0.25 <= freq < len(gaps) * 0.5]
        low_priority = [skill for skill, freq in sorted_skills if freq < len(gaps) * 0.25]
        
        # Get best matching jobs
        best_matches = [gap for gap in gaps if gap['match_percentage'] >= 50][:5]
        
        return {
            'student_id': student_id,
            'total_jobs_analyzed': len(gaps),
            'high_priority_skills': high_priority,
            'medium_priority_skills': medium_priority,
            'low_priority_skills': low_priority,
            'skill_frequency': dict(sorted_skills[:10]),  # Top 10 most demanded
            'best_matching_jobs': best_matches,
            'overall_recommendation': self._generate_overall_recommendation(high_priority, medium_priority, best_matches)
        }
    
    def _generate_overall_recommendation(self, high_priority, medium_priority, best_matches):
        """Generate user-friendly recommendation text"""
        recommendations = []
        
        if high_priority:
            recommendations.append(f"Start with {', '.join(high_priority[:3])} - these show up everywhere")
        
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
        jobs = execute_query("SELECT id FROM job_roles WHERE is_active = 1")
        
        results = []
        for job in jobs:
            match_result = self.match(student_id, job['id'])
            results.append(match_result)
        
        # Sort by match percentage
        results.sort(key=lambda x: x['skill_match_percentage'], reverse=True)
        
        return results
