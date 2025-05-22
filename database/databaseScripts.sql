select * from teams;


select * from team_members tm ;

select * from users
where external_id = '60778d4fb5dffc006f4653c9'

select * from jira_issues ji
where key = 'ORG-57'

select * from subtasks s 

where parent_issue_id = 186905

select * from sprints

delete from jira_issues ji 


delete from subtasks s;

delete from sprints;

delete from issue_sprints;

ALTER TABLE jira_issues ADD COLUMN IF NOT EXISTS parent_key VARCHAR(50);
ALTER TABLE jira_issues ADD COLUMN IF NOT EXISTS parent_story_points NUMERIC;


ALTER TABLE jira_issues DROP COLUMN IF EXISTS parent_key;
ALTER TABLE jira_issues DROP COLUMN IF EXISTS parent_story_points;


select * from subtasks s
where key = 'ORG-57'

select * from subtasks s
where parent_issue_id  = 186905

ALTER TABLE jira_issues ADD COLUMN IF NOT EXISTS subtask_count INTEGER DEFAULT 0;


WITH parent_info AS (
                SELECT 
                    j.id as parent_id,
                    j.key as parent_key,
                    j.story_points as parent_story_points,
                    j.subtask_count
                FROM jira_issues j
                WHERE j.subtask_count > 0
            )
            UPDATE jira_issues j
            SET story_points = CASE 
                WHEN p.parent_story_points > 0 AND p.subtask_count > 0 
                THEN p.parent_story_points / p.subtask_count 
                ELSE 0 
            END
            FROM parent_info p
            JOIN subtasks s ON s.parent_issue_id = p.parent_id
            WHERE j.id = s.id
            AND j.issue_type = 'Sub-task'
            AND j.story_points = 0




