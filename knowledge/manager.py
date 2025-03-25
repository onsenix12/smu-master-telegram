import json
import os
from db.database import get_connection

def load_courses_to_db():
    """Load course data from JSON to database"""
    # Path to the expanded courses JSON file
    file_path = os.path.join('knowledge', 'data', 'expanded_courses.json')
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} not found")
        # Try the regular courses file as fallback
        file_path = os.path.join('knowledge', 'data', 'courses.json')
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
        
        # Add course FAQs to the faqs table if they exist
        if 'faqs' in course:
            for faq in course['faqs']:
                cursor.execute('''
                INSERT OR REPLACE INTO faqs (question, answer, added_by)
                VALUES (?, ?, ?)
                ''', (
                    faq['question'],
                    faq['answer'],
                    f"System (from course {course['course_code']})"
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
    
    if not course:
        conn.close()
        return None
    
    # Get expanded course info from file
    expanded_data = get_expanded_course_data(course_code)
    
    # Convert basic course to dictionary
    course_dict = dict(course)
    
    # Add expanded data if available
    if expanded_data:
        course_dict['credits'] = expanded_data.get('credits')
        course_dict['prerequisites'] = expanded_data.get('prerequisites')
        course_dict['syllabus'] = expanded_data.get('syllabus')
        course_dict['course_faqs'] = expanded_data.get('faqs')
    
    conn.close()
    return course_dict

def get_expanded_course_data(course_code):
    """Get expanded course data from the JSON file"""
    file_path = os.path.join('knowledge', 'data', 'expanded_courses.json')
    
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r') as file:
            courses = json.load(file)
            
        for course in courses:
            if course['course_code'] == course_code:
                return course
                
    except Exception as e:
        print(f"Error reading expanded course data: {str(e)}")
        
    return None

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