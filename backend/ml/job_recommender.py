import os
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', 'jobs_dataset.csv')


def load_jobs():
    jobs = []
    with open(DATASET_PATH, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)  # job_role, company_name, field, required_skills...
        for row in reader:
            if len(row) < 4:
                continue
            job_role = row[0].strip()
            company_name = row[1].strip()
            field = row[2].strip()
            # columns 3 onwards are individual skills
            skills = [s.strip() for s in row[3:] if s.strip()]
            jobs.append({
                'job_role': job_role,
                'company_name': company_name,
                'field': field,
                'required_skills': skills,
                'skills_str': ' '.join(skills)  # for TF-IDF
            })
    return jobs


def recommend_jobs(branch: str, skills: str, top_n: int = 10):
    jobs = load_jobs()

    # No branch filter — recommend purely based on skill match across ALL jobs
    filtered = jobs

    # TF-IDF + Cosine Similarity
    job_skill_strings = [j['skills_str'] for j in filtered]
    student_skills_str = skills.replace(',', ' ')

    corpus = job_skill_strings + [student_skills_str]

    vectorizer = TfidfVectorizer(token_pattern=r"[a-zA-Z0-9#\+\.\-/]+")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    student_vector = tfidf_matrix[-1]
    job_vectors = tfidf_matrix[:-1]

    scores = cosine_similarity(student_vector, job_vectors).flatten()

    # Step 3: Attach scores and sort
    for i, job in enumerate(filtered):
        job['match_score'] = float(scores[i])

    top_jobs = sorted(filtered, key=lambda x: x['match_score'], reverse=True)[:top_n]

    # Step 4: Build result with missing skills
    student_skill_set = set(s.strip().lower() for s in skills.split(','))

    results = []
    for job in top_jobs:
        missing = [s for s in job['required_skills'] if s.lower() not in student_skill_set]
        missing = list(dict.fromkeys(missing))[:5]  # dedupe, max 5

        results.append({
            'job_role': job['job_role'],
            'company_name': job['company_name'],
            'field': job['field'],
            'match_percentage': round(job['match_score'] * 100, 1),
            'missing_skills': missing
        })

    return results
