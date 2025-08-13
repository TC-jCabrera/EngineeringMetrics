import logging
from common.metrics_util import parse_datetime
from .db_connection import DatabaseConnection


def storeTeamMembers(config, data):
    """
    Persists team members data from JSON into PostgreSQL tables.
    
    Args:
        json_data: The JSON data containing team members information
        db_config: Database connection configuration dictionary
    """
    email_list = []
    cursor = None
    try:
        conn = DatabaseConnection.get_instance().get_connection(config)
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



def updateJiraAliases(config, data):    
    cursor = None
    try:
        conn = DatabaseConnection.get_instance().get_connection(config)
        cursor = conn.cursor()
        returnExternalId = ""
        logging.info(f"Processing {len(data['results'])} team members")
        
        """Update external_ids in the database based on email matches."""
        for user in data['results']:
            email = user.get('email')
            external_id = user.get('external_id')
           
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


def storeJiraIssues(config, data): 
    cursor = None
    try:
        conn = DatabaseConnection.get_instance().get_connection(config)
        cursor = conn.cursor()
        
        # Access the issues array from the response
        for issue in data['issues']:
            fields = issue['fields']
            
            # Get story points, default to 0 if empty
            story_points = 0 if fields.get('customfield_10004') is None else fields['customfield_10004']
            
          
            
            # Insert into jira_issues table
            cursor.execute("""
                INSERT INTO jira_issues (
                    id, key, summary, resolution_date, story_points, 
                    issue_type, assignee_id, email, subtask_count
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET  
                    key = EXCLUDED.key,
                    summary = EXCLUDED.summary,
                    resolution_date = EXCLUDED.resolution_date,
                    story_points = EXCLUDED.story_points,
                    issue_type = EXCLUDED.issue_type,
                    assignee_id = EXCLUDED.assignee_id,
                    email = EXCLUDED.email,
                    subtask_count = EXCLUDED.subtask_count
            """, (
                int(issue['id']),
                issue['key'],
                fields.get('summary'),
                parse_datetime(fields.get('resolutiondate')),
                story_points,
                fields['issuetype']['name'],
                fields.get('assignee', {}).get('accountId'),
                fields.get('assignee', {}).get('emailAddress'),
                len(fields.get('subtasks', []))
            ))
            
            # Handle sprints
            if 'customfield_10007' in fields and fields['customfield_10007']:
                for sprint in fields['customfield_10007']:
                    # Insert into sprints table
                    cursor.execute("""
                        INSERT INTO sprints (
                            id, name, state, board_id, start_date, 
                            end_date, complete_date
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            name = EXCLUDED.name,
                            state = EXCLUDED.state,
                            board_id = EXCLUDED.board_id,
                            start_date = EXCLUDED.start_date,
                            end_date = EXCLUDED.end_date,
                            complete_date = EXCLUDED.complete_date
                    """, (
                        sprint['id'],
                        sprint['name'],
                        sprint['state'],
                        sprint['boardId'],
                        parse_datetime(sprint.get('startDate')),
                        parse_datetime(sprint.get('endDate')),
                        parse_datetime(sprint.get('completeDate'))
                    ))
                    
                    # Insert into issue_sprints table
                    cursor.execute("""
                        INSERT INTO issue_sprints (
                            issue_id, sprint_id
                        ) VALUES (%s, %s)
                        ON CONFLICT (issue_id, sprint_id) DO NOTHING
                    """, (int(issue['id']), sprint['id']))
            
            # Handle subtasks
            if 'subtasks' in fields and fields['subtasks']:
                for subtask in fields['subtasks']:
                    cursor.execute("""
                        INSERT INTO subtasks (
                            id, parent_issue_id, key
                        ) VALUES (%s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            parent_issue_id = EXCLUDED.parent_issue_id,
                            key = EXCLUDED.key
                    """, (
                        int(subtask['id']),
                        int(issue['id']),
                        subtask['key']
                    ))
        
        conn.commit()
        logging.info("Successfully stored Jira Issues")
    except Exception as e:
        logging.error(f"Error persisting data: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()


def updateSubtasksStoryPoints(config, start_date, end_date):
    """
    Updates story points for subtasks that have 0 points by distributing parent's story points.
    Only updates subtasks within the specified date range.
    """
    cursor = None
    try:
        conn = DatabaseConnection.get_instance().get_connection(config)
        cursor = conn.cursor()
        
        # Update subtasks with 0 story points within date range
        # First, update subtasks' story points based on their parent's story points
        cursor.execute("""
            WITH parent_info AS (
            SELECT 
                j.id as parent_id,
                j.key as parent_key,
                j.story_points as parent_story_points,
                j.subtask_count
            FROM jira_issues j
            WHERE j.subtask_count > 0
            AND j.resolution_date BETWEEN %s AND %s
            )
            UPDATE jira_issues j
            SET story_points = CASE 
            WHEN p.parent_story_points > 0 AND p.subtask_count > 0 
            THEN ROUND(CAST(p.parent_story_points AS NUMERIC) / p.subtask_count, 2)
            ELSE 0 
            END
            FROM parent_info p
            JOIN subtasks s ON s.parent_issue_id = p.parent_id
            WHERE j.id = s.id
            AND j.issue_type = 'Sub-task'
            AND j.story_points = 0
            AND j.resolution_date BETWEEN %s AND %s
        """, (start_date, end_date, start_date, end_date))

        # (Removed code that sets story_points to 0 for issues with subtasks)
        
        updated_count = cursor.rowcount
        conn.commit()
        logging.info(f"Updated story points for {updated_count} subtasks between {start_date} and {end_date}")

        #TODO: If the issue has subtasks, update the story points to zero
        
    except Exception as e:
        logging.error(f"Error updating subtask story points: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()