import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

@pytest.fixture
def test_db():
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Save original database path
    old_db_path = os.environ.get('DATABASE_PATH')
    os.environ['DATABASE_PATH'] = db_path
    
    # Initialize the test database
    from db.database import init_database
    init_database()
    
    yield db_path
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)
    if old_db_path:
        os.environ['DATABASE_PATH'] = old_db_path
    else:
        del os.environ['DATABASE_PATH']