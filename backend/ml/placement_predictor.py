import pickle
import numpy as np
import os
from database_sqlite import execute_query

class PlacementPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model and scaler"""
        try:
            models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
            model_path = os.path.join(models_dir, 'placement_model.pkl')
            scaler_path = os.path.join(models_dir, 'scaler.pkl')
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                print("Model and scaler loaded successfully!")
            else:
                print("Model files not found. Auto-training model...")
                try:
                    try:
                        from ml.train_model import train_placement_model
                    except ImportError:
                        from train_model import train_placement_model
                    self.model, self.scaler, _ = train_placement_model()
                    print("Auto-training completed successfully!")
                except Exception as train_err:
                    print(f"Auto-training failed: {train_err}. Using rule-based fallback.")
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def predict(self, student_id):
        """Predict placement probability for a student"""
        student = execute_query("SELECT * FROM students WHERE id = ?", (student_id,))[0]
        
        # Extract features
        cgpa = float(student.get('cgpa', 0))
        skills = student.get('skills', '')
        skills_count = len([s.strip() for s in skills.split(',') if s.strip()]) if skills else 0
        internships = int(student.get('internships_count', 0))
        projects = int(student.get('projects_count', 0))
        certifications = int(student.get('certifications_count', 0))
        
        # Prepare features
        features = np.array([[cgpa, skills_count, internships, projects, certifications]])
        
        # Use trained model if available
        if self.model and self.scaler:
            features_scaled = self.scaler.transform(features)
            probability = min(self.model.predict_proba(features_scaled)[0][1] * 100, 95)
            prediction = self.model.predict(features_scaled)[0]
            
            # Determine readiness level
            if probability >= 75:
                readiness = 'High'
            elif probability >= 50:
                readiness = 'Medium'
            else:
                readiness = 'Low'
        else:
            # Fallback to rule-based prediction (weighted, max 100)
            cgpa_score        = min(cgpa / 10, 1.0) * 35          # max 35 pts
            skills_score      = min(skills_count / 8, 1.0) * 25   # max 25 pts (target 8 skills)
            internship_score  = min(internships / 3, 1.0) * 20    # max 20 pts (target 3)
            project_score     = min(projects / 5, 1.0) * 12       # max 12 pts (target 5)
            cert_score        = min(certifications / 4, 1.0) * 8  # max  8 pts (target 4)

            probability = round(min(cgpa_score + skills_score + internship_score + project_score + cert_score, 95), 2)
            readiness = 'High' if probability >= 75 else 'Medium' if probability >= 50 else 'Low'
            prediction = 1 if probability >= 50 else 0
        
        return {
            'student_id': student_id,
            'student_name': student.get('name'),
            'placement_probability': round(probability, 2),
            'placement_prediction': 'Likely to be Placed' if prediction == 1 else 'May Need Improvement',
            'placement_readiness': readiness,
            'factors': {
                'cgpa': cgpa,
                'skills_count': skills_count,
                'internships_count': internships,
                'projects_count': projects,
                'certifications_count': certifications
            },
            'recommendations': self._generate_recommendations(cgpa, skills_count, internships, projects, certifications)
        }
    
    def _generate_recommendations(self, cgpa, skills_count, internships, projects, certifications):
        """Generate personalized recommendations"""
        recommendations = []
        
        if cgpa < 7.5:
            recommendations.append("Focus on improving academic performance (target CGPA > 7.5)")
        if skills_count < 6:
            recommendations.append("Learn more in-demand technical skills (target 6+ skills)")
        if internships < 2:
            recommendations.append("Gain practical experience through internships (target 2+ internships)")
        if projects < 4:
            recommendations.append("Build more projects to showcase your abilities (target 4+ projects)")
        if certifications < 3:
            recommendations.append("Obtain relevant certifications to validate your skills (target 3+ certifications)")
        
        if not recommendations:
            recommendations.append("Excellent profile! Focus on interview preparation and soft skills")
        
        return recommendations
