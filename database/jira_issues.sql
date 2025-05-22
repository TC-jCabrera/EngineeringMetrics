-- Issues table - Core issue information
CREATE TABLE jira_issues (
    id INTEGER PRIMARY KEY,
    key VARCHAR(50) NOT NULL,
    summary TEXT,
    resolution_date TIMESTAMP,
    story_points NUMERIC, -- customfield_10004
    issue_type VARCHAR(100) NOT NULL,
    assignee_id VARCHAR(100) NOT NULL,
    subtask_count INTEGER DEFAULT 0
);

-- Sprint table - Basic sprint information
CREATE TABLE sprints (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    state VARCHAR(50) NOT NULL,
    board_id INTEGER NOT NULL,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    complete_date TIMESTAMP
);

-- Issue-Sprint relationship table (many-to-many)
CREATE TABLE issue_sprints (
    issue_id INTEGER NOT NULL,
    sprint_id INTEGER NOT NULL,
    PRIMARY KEY (issue_id, sprint_id),
    FOREIGN KEY (issue_id) REFERENCES jira_issues(id) ON DELETE CASCADE,
    FOREIGN KEY (sprint_id) REFERENCES sprints(id) ON DELETE CASCADE
);

-- Subtasks table for parent-child relationships
CREATE TABLE subtasks (
    id INTEGER PRIMARY KEY,
    parent_issue_id INTEGER NOT NULL,
    key VARCHAR(50) NOT NULL,
    FOREIGN KEY (parent_issue_id) REFERENCES jira_issues(id) ON DELETE CASCADE
);

-- Add basic indexes for performance
CREATE INDEX idx_jira_issues_key ON jira_issues(key);
CREATE INDEX idx_jira_issues_resolution_date ON jira_issues(resolution_date);
CREATE INDEX idx_issue_sprints_sprint_id ON issue_sprints(sprint_id);

-- Drop columns if they exist
ALTER TABLE jira_issues DROP COLUMN IF EXISTS parent_key;
ALTER TABLE jira_issues DROP COLUMN IF EXISTS parent_story_points;

-- Add email field to jira_issues table
ALTER TABLE jira_issues ADD COLUMN email VARCHAR(255);

-- Add subtask_count column
ALTER TABLE jira_issues ADD COLUMN IF NOT EXISTS subtask_count INTEGER DEFAULT 0;