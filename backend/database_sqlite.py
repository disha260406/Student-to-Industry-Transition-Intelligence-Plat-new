import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'students.db')

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            branch TEXT NOT NULL,
            cgpa REAL NOT NULL,
            skills TEXT,
            github_url TEXT,
            internships_count INTEGER DEFAULT 0,
            projects_count INTEGER DEFAULT 0,
            certifications_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Portfolio tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            name TEXT,
            file_name TEXT,
            has_file INTEGER DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_internships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            company TEXT,
            role TEXT,
            duration TEXT,
            has_certificate INTEGER DEFAULT 0,
            cert_name TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            name TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')
    
    # Create job_roles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            branch TEXT,
            description TEXT,
            required_skills TEXT NOT NULL,
            preferred_skills TEXT,
            min_cgpa REAL DEFAULT 0,
            experience_required TEXT,
            salary_range TEXT,
            location TEXT,
            job_type TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')
    # Add any missing columns to existing SQLite table if created earlier
    existing_cols = [col[1] for col in cursor.execute("PRAGMA table_info(job_roles)").fetchall()]
    for col_name, col_type in [
        ('description', 'TEXT'),
        ('experience_required', 'TEXT'),
        ('salary_range', 'TEXT'),
        ('location', 'TEXT'),
        ('job_type', 'TEXT')
    ]:
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE job_roles ADD COLUMN {col_name} {col_type}")

    
    # Insert jobs from CSV if table is empty
    cursor.execute('SELECT COUNT(*) FROM job_roles')
    if cursor.fetchone()[0] == 0:
        import csv
        csv_path = os.path.join(os.path.dirname(__file__), 'jobs_dataset.csv')
        if os.path.exists(csv_path):
            with open(csv_path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    job_role = (row.get('job_role') or '').strip()
                    company  = (row.get('company_name') or '').strip()
                    field    = (row.get('field') or '').strip()
                    req      = (row.get('required_skills') or '').strip()
                    extra    = row.get(None, [])
                    extra_skills = ', '.join([s.strip() for s in extra if s.strip()]) if isinstance(extra, list) else str(extra).strip()
                    all_skills = ', '.join(filter(None, [req, extra_skills]))
                    if job_role and company:
                        cursor.execute(
                            'INSERT INTO job_roles (title, company, branch, required_skills, preferred_skills, min_cgpa, is_active) VALUES (?,?,?,?,?,?,1)',
                            (job_role, company, field, all_skills, '', 0)
                        )
    
    # Create applications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            job_role TEXT NOT NULL,
            company TEXT NOT NULL,
            field TEXT,
            match_percentage REAL DEFAULT 0,
            status TEXT DEFAULT 'Applied',
            applied_date TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')

    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH, timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=None):
    """Execute SELECT query"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        results = [dict(row) for row in cursor.fetchall()]
        return results
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()

def execute_update(query, params=None):
    """Execute INSERT/UPDATE/DELETE query"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        last_id = cursor.lastrowid
        return last_id
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

# Initialize database on import
init_db()
