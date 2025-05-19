import json
import sqlite3
from typing import Dict, List

def load_alias_data(file_path: str) -> List[Dict]:
    """Load and parse the alias.json file."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data['results']

def update_external_ids(db_path: str, alias_data: List[Dict]):
    """Update external_ids in the teams table based on matching emails."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create a mapping of email to external_id from alias data
    email_to_external_id = {item['email']: item['external_id'] for item in alias_data}
    
    # Update the teams table by joining with users table
    for email, external_id in email_to_external_id.items():
        cursor.execute("""
            UPDATE teams 
            SET external_id = ? 
            WHERE id IN (
                SELECT t.id 
                FROM teams t
                JOIN team_members tm ON t.id = tm.team_id
                JOIN users u ON tm.user_id = u.id
                WHERE u.email = ?
            )
        """, (external_id, email))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

def main():
    # File paths
    alias_file = 'alias.json'
    db_file = 'database/teams.sql'
    
    try:
        # Load alias data
        alias_data = load_alias_data(alias_file)
        
        # Update external IDs
        update_external_ids(db_file, alias_data)
        print("Successfully updated external IDs in the teams table.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 