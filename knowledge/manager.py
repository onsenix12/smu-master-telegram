import json
import os
from db.database import get_connection

def load_courses_to_db():
    """Load course data from JSON to database"""
    # Path to the courses JSON file
    file_path = os.path.join('knowledge', 'data', 'courses.json')
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} not found")
        return
    
    # Read JSON file
    with open(file_path, 'r') as file:
        courses = json.load(file)
    
    # Connect to database
    conn = get_connection()
    cursor = conn.cursor()
    
    # Insert courses into database
    for course in courses:
        cursor.execute('''
        INSERT OR REPLACE INTO courses (course_code, title, description, instructor)
        VALUES (?, ?, ?, ?)
        ''', (
            course['course_code'],
            course['title'], 
            course['description'],
            course['instructor']
        ))
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"Loaded {len(courses)} courses into the database")

def get_course_info(course_code):
    """Get information about a specific course"""
    # Standardize course code format
    course_code = course_code.upper()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT * FROM courses WHERE course_code = ?
    ''', (course_code,))
    
    course = cursor.fetchone()
    conn.close()
    
    if not course:
        return None
    
    # Convert to dictionary
    return dict(course)

def search_courses(query):
    """Search for courses by keyword"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Search in title and description
    cursor.execute('''
    SELECT * FROM courses 
    WHERE title LIKE ? OR description LIKE ?
    ''', (f'%{query}%', f'%{query}%'))
    
    courses = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    return [dict(course) for course in courses]

def get_all_faqs():
    """Get all FAQs from the database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM faqs ORDER BY created_at DESC')
    
    faqs = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    return [dict(faq) for faq in faqs]

def add_faq(question, answer, added_by):
    """Add a new FAQ to the database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO faqs (question, answer, added_by)
    VALUES (?, ?, ?)
    ''', (question, answer, added_by))
    
    conn.commit()
    conn.close()
    
    return True