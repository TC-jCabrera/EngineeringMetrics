import logging
import psycopg2


def storeTeamMembers(config, data):
    """
    Persists team members data from JSON into PostgreSQL tables.
    
    Args:
        json_data: The JSON data containing team members information
        db_config: Database connection configuration dictionary
    """
    email_list = []
    try:
       
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=config["db_connection"]["dbname"],
            user=config["db_connection"]["user"],
            password=config["db_connection"]["password"],
            host=config["db_connection"]["host"],
            port=config["db_connection"]["port"],
        )
        cursor = conn.cursor()
        
        logging.info(f"Processing {len(data['results'])} team members")

       
        # Process each team member in the results
        for member in data['results']:
            # Extract team data
            team = member['team']
            
            # Insert team if it doesn't exist
            cursor.execute("""
                INSERT INTO teams (id, name, org, parent, path)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    org = EXCLUDED.org,
                    parent = EXCLUDED.parent,
                    path = EXCLUDED.path
            """, (
                team['id'],
                team['name'],
                team['org'],
                team['parent'],
                team['path']
            ))
            
            # Extract user data
            user = member['apex_user']
            
            # Insert user if doesn't exist
            cursor.execute("""
                INSERT INTO users (id, name, email, external_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    email = EXCLUDED.email,
                    external_id = EXCLUDED.external_id
            """, (
                user['id'],
                user['name'],
                user['email'],
                str(user['id'])  # Using user id as external_id for simplicity
            ))
            
            email_list.append(user['email'])

            # Insert team membership
            cursor.execute("""
                INSERT INTO team_members (id, user_id, team_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    team_id = EXCLUDED.team_id
            """, (
                member['id'],
                user['id'],
                team['id']
            ))
        
        # Commit the transaction
        conn.commit()
        logging.info("Successfully persisted team members data")
        return email_list
    except Exception as e:
        logging.error(f"Error persisting data: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



def updateJiraAliases(config, data):    
    try:
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=config["db_connection"]["dbname"],
            user=config["db_connection"]["user"],
            password=config["db_connection"]["password"],
            host=config["db_connection"]["host"],
            port=config["db_connection"]["port"],
        )
        cursor = conn.cursor()
        returnExternalId = ""
        logging.info(f"Processing {len(data['results'])} team members")
        
        """Update external_ids in the database based on email matches."""
        cursor = conn.cursor()
        
        for user in data['results']:
            email = user.get('email')
            external_id = user.get('external_id')
            print(email,external_id)
            if email and external_id:
                # Update the external_id where email matches
                cursor.execute(
                    "UPDATE users SET external_id = %s WHERE email = %s",
                    (external_id, email)
                )
                
                if cursor.rowcount > 0:
                    print(f"Updated external_id for user with email: {email}")
                else:
                    print(f"No user found with email: {email}")

                returnExternalId = external_id
        # Commit the transaction
        conn.commit()
        logging.info("Successfully updated Jira Aliases")
        return returnExternalId
    except Exception as e:
        logging.error(f"Error persisting data: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
