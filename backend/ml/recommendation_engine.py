"""
Recommendation Engine for Skill Development
Provides course, certification, and project recommendations based on missing skills
"""

class RecommendationEngine:
    def __init__(self):
        # Skill-based recommendations mapping
        self.skill_recommendations = {
            # Programming Languages
            'python': {
                'courses': [
                    'Python for Everybody (Coursera)',
                    'Complete Python Bootcamp (Udemy)',
                    'Python Programming Masterclass (Udemy)'
                ],
                'certifications': [
                    'PCEP - Certified Entry-Level Python Programmer',
                    'PCAP - Certified Associate Python Programmer',
                    'Microsoft Python Certification'
                ],
                'projects': [
                    'Build a Web Scraper with BeautifulSoup',
                    'Create a REST API with Flask',
                    'Develop a Data Analysis Dashboard',
                    'Build an Automation Script for Daily Tasks'
                ]
            },
            'java': {
                'courses': [
                    'Java Programming Masterclass (Udemy)',
                    'Java Fundamentals (Pluralsight)',
                    'Object-Oriented Programming in Java (Coursera)'
                ],
                'certifications': [
                    'Oracle Certified Associate Java Programmer',
                    'Oracle Certified Professional Java SE Programmer',
                    'Spring Professional Certification'
                ],
                'projects': [
                    'Build a Banking Management System',
                    'Create a Library Management System',
                    'Develop a Chat Application',
                    'Build an E-commerce Backend'
                ]
            },
            'javascript': {
                'courses': [
                    'The Complete JavaScript Course (Udemy)',
                    'JavaScript: Understanding the Weird Parts (Udemy)',
                    'Modern JavaScript From The Beginning (Udemy)'
                ],
                'certifications': [
                    'JavaScript Developer Certification (W3Schools)',
                    'Meta Front-End Developer Certificate',
                    'Microsoft Certified: JavaScript Developer'
                ],
                'projects': [
                    'Build a Todo App with Local Storage',
                    'Create an Interactive Quiz Application',
                    'Develop a Weather App using API',
                    'Build a Portfolio Website'
                ]
            },
            
            # Web Development
            'react': {
                'courses': [
                    'React - The Complete Guide (Udemy)',
                    'Modern React with Redux (Udemy)',
                    'React Front To Back (Udemy)'
                ],
                'certifications': [
                    'Meta React Developer Certificate',
                    'React Developer Certification (HackerRank)',
                    'Microsoft Certified: React Developer'
                ],
                'projects': [
                    'Build a Social Media Dashboard',
                    'Create an E-commerce Frontend',
                    'Develop a Movie Search App',
                    'Build a Real-time Chat Application'
                ]
            },
            'node.js': {
                'courses': [
                    'The Complete Node.js Developer Course (Udemy)',
                    'Node.js, Express, MongoDB Bootcamp (Udemy)',
                    'Node.js API Masterclass (Udemy)'
                ],
                'certifications': [
                    'OpenJS Node.js Application Developer',
                    'OpenJS Node.js Services Developer',
                    'Node.js Certified Developer (W3Schools)'
                ],
                'projects': [
                    'Build a RESTful API with Express',
                    'Create a Real-time Chat Server',
                    'Develop a Blog Platform Backend',
                    'Build an Authentication System'
                ]
            },
            'angular': {
                'courses': [
                    'Angular - The Complete Guide (Udemy)',
                    'Angular Fundamentals (Pluralsight)',
                    'Angular Essential Training (LinkedIn Learning)'
                ],
                'certifications': [
                    'Angular Certification (HackerRank)',
                    'Google Angular Developer Certificate',
                    'Angular Developer Certification (W3Schools)'
                ],
                'projects': [
                    'Build a Task Management App',
                    'Create a Recipe Book Application',
                    'Develop an Admin Dashboard',
                    'Build a Shopping Cart System'
                ]
            },
            
            # Data Science & ML
            'machine learning': {
                'courses': [
                    'Machine Learning by Andrew Ng (Coursera)',
                    'Machine Learning A-Z (Udemy)',
                    'Applied Machine Learning in Python (Coursera)'
                ],
                'certifications': [
                    'Google Machine Learning Engineer Certificate',
                    'AWS Certified Machine Learning - Specialty',
                    'Microsoft Certified: Azure AI Engineer'
                ],
                'projects': [
                    'Build a House Price Prediction Model',
                    'Create a Customer Churn Prediction System',
                    'Develop a Sentiment Analysis Tool',
                    'Build a Recommendation System'
                ]
            },
            'deep learning': {
                'courses': [
                    'Deep Learning Specialization (Coursera)',
                    'Deep Learning A-Z (Udemy)',
                    'Practical Deep Learning for Coders (fast.ai)'
                ],
                'certifications': [
                    'TensorFlow Developer Certificate',
                    'Deep Learning Specialization Certificate',
                    'NVIDIA Deep Learning Institute Certification'
                ],
                'projects': [
                    'Build an Image Classification Model',
                    'Create a Chatbot using NLP',
                    'Develop a Face Recognition System',
                    'Build an Object Detection System'
                ]
            },
            'data science': {
                'courses': [
                    'Data Science Specialization (Coursera)',
                    'Python for Data Science and Machine Learning (Udemy)',
                    'Data Science Career Track (DataCamp)'
                ],
                'certifications': [
                    'IBM Data Science Professional Certificate',
                    'Google Data Analytics Certificate',
                    'Microsoft Certified: Data Analyst Associate'
                ],
                'projects': [
                    'Analyze Sales Data and Create Visualizations',
                    'Build a Customer Segmentation Model',
                    'Create a COVID-19 Data Dashboard',
                    'Develop a Stock Price Prediction System'
                ]
            },
            
            # Databases
            'sql': {
                'courses': [
                    'The Complete SQL Bootcamp (Udemy)',
                    'SQL for Data Science (Coursera)',
                    'Advanced SQL: MySQL Data Analysis (Udemy)'
                ],
                'certifications': [
                    'Oracle Database SQL Certified Associate',
                    'Microsoft Certified: Azure Database Administrator',
                    'MySQL Database Administrator Certification'
                ],
                'projects': [
                    'Design a School Management Database',
                    'Create a Hospital Management System DB',
                    'Build an Inventory Management Database',
                    'Develop a Sales Analytics Database'
                ]
            },
            'mongodb': {
                'courses': [
                    'MongoDB - The Complete Developer Guide (Udemy)',
                    'MongoDB University Courses (Free)',
                    'Complete MongoDB Administration Guide (Udemy)'
                ],
                'certifications': [
                    'MongoDB Certified Developer Associate',
                    'MongoDB Certified DBA Associate',
                    'MongoDB University Completion Certificate'
                ],
                'projects': [
                    'Build a Blog Platform with MongoDB',
                    'Create a Social Media Backend',
                    'Develop a Real-time Analytics System',
                    'Build a Content Management System'
                ]
            },
            
            # Cloud & DevOps
            'aws': {
                'courses': [
                    'AWS Certified Solutions Architect (Udemy)',
                    'AWS Fundamentals Specialization (Coursera)',
                    'Ultimate AWS Certified Developer (Udemy)'
                ],
                'certifications': [
                    'AWS Certified Solutions Architect - Associate',
                    'AWS Certified Developer - Associate',
                    'AWS Certified Cloud Practitioner'
                ],
                'projects': [
                    'Deploy a Web App on AWS EC2',
                    'Build a Serverless Application with Lambda',
                    'Create a Static Website on S3',
                    'Set up a CI/CD Pipeline with AWS'
                ]
            },
            'docker': {
                'courses': [
                    'Docker Mastery: Complete Toolset (Udemy)',
                    'Docker and Kubernetes: The Complete Guide (Udemy)',
                    'Docker for Developers (Pluralsight)'
                ],
                'certifications': [
                    'Docker Certified Associate',
                    'Kubernetes and Docker Certification',
                    'Docker Fundamentals Certificate'
                ],
                'projects': [
                    'Containerize a Full-Stack Application',
                    'Create a Multi-Container App with Docker Compose',
                    'Build a Microservices Architecture',
                    'Set up a Development Environment with Docker'
                ]
            },
            'kubernetes': {
                'courses': [
                    'Kubernetes for Developers (Udemy)',
                    'Kubernetes Mastery (Udemy)',
                    'Kubernetes Fundamentals (Linux Foundation)'
                ],
                'certifications': [
                    'Certified Kubernetes Application Developer (CKAD)',
                    'Certified Kubernetes Administrator (CKA)',
                    'Kubernetes Security Specialist (CKS)'
                ],
                'projects': [
                    'Deploy a Microservices App on Kubernetes',
                    'Set up a CI/CD Pipeline with K8s',
                    'Create a Scalable Web Application',
                    'Build a Monitoring System with Prometheus'
                ]
            },
            
            # Mobile Development
            'android': {
                'courses': [
                    'The Complete Android Development Bootcamp (Udemy)',
                    'Android App Development Specialization (Coursera)',
                    'Android Basics by Google (Udacity)'
                ],
                'certifications': [
                    'Google Associate Android Developer',
                    'Android Developer Certification (HackerRank)',
                    'Meta Android Developer Certificate'
                ],
                'projects': [
                    'Build a Weather App',
                    'Create a News Reader Application',
                    'Develop a Fitness Tracker App',
                    'Build a Social Media Clone'
                ]
            },
            'kotlin': {
                'courses': [
                    'Kotlin for Android Development (Udemy)',
                    'Kotlin Programming Masterclass (Udemy)',
                    'Kotlin for Java Developers (Coursera)'
                ],
                'certifications': [
                    'Kotlin Developer Certification (JetBrains)',
                    'Google Associate Android Developer (Kotlin)',
                    'Kotlin Programming Certificate'
                ],
                'projects': [
                    'Build a Todo App with Kotlin',
                    'Create a Recipe App',
                    'Develop a Chat Application',
                    'Build a Music Player App'
                ]
            },
            
            # Other Technologies
            'git': {
                'courses': [
                    'Git Complete: The Definitive Guide (Udemy)',
                    'Version Control with Git (Coursera)',
                    'Git & GitHub Crash Course (YouTube)'
                ],
                'certifications': [
                    'GitHub Foundations Certification',
                    'Git Version Control Certification',
                    'GitLab Certified Associate'
                ],
                'projects': [
                    'Contribute to Open Source Projects',
                    'Create a Portfolio Repository',
                    'Set up Git Workflow for Team Project',
                    'Build a Documentation Repository'
                ]
            },
            'rest api': {
                'courses': [
                    'REST API Design, Development & Management (Udemy)',
                    'Building RESTful APIs (Pluralsight)',
                    'API Development Fundamentals (LinkedIn Learning)'
                ],
                'certifications': [
                    'API Design and Development Certificate',
                    'RESTful API Developer Certification',
                    'Postman API Fundamentals Student Expert'
                ],
                'projects': [
                    'Build a CRUD API for Blog',
                    'Create a User Authentication API',
                    'Develop a Payment Gateway Integration',
                    'Build a File Upload API'
                ]
            }
        }
    
    def get_skill_recommendations(self, skill):
        """
        Get recommendations for a specific skill
        """
        skill_lower = skill.lower().strip()
        
        # Direct match
        if skill_lower in self.skill_recommendations:
            return {
                'skill': skill,
                'courses': self.skill_recommendations[skill_lower]['courses'],
                'certifications': self.skill_recommendations[skill_lower]['certifications'],
                'projects': self.skill_recommendations[skill_lower]['projects']
            }
        
        # Partial match
        for key in self.skill_recommendations:
            if key in skill_lower or skill_lower in key:
                return {
                    'skill': skill,
                    'courses': self.skill_recommendations[key]['courses'],
                    'certifications': self.skill_recommendations[key]['certifications'],
                    'projects': self.skill_recommendations[key]['projects']
                }
        
        # Generic recommendations
        return {
            'skill': skill,
            'courses': [
                f'Search for "{skill}" courses on Udemy',
                f'Search for "{skill}" courses on Coursera',
                f'Search for "{skill}" tutorials on YouTube'
            ],
            'certifications': [
                f'Search for "{skill}" certifications online',
                f'Check vendor-specific certifications for {skill}'
            ],
            'projects': [
                f'Build a beginner project using {skill}',
                f'Contribute to open source projects using {skill}',
                f'Create a portfolio project showcasing {skill}'
            ]
        }
    
    def get_bulk_recommendations(self, skills_list):
        """
        Get recommendations for multiple skills
        """
        recommendations = []
        for skill in skills_list:
            rec = self.get_skill_recommendations(skill)
            if rec:
                recommendations.append(rec)
        return recommendations
