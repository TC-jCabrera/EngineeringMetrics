select * from teams;


select * from team_members tm ;

select * from users
where external_id = '60778d4fb5dffc006f4653c9'

select email, sum(story_points ) from jira_issues ji
where resolution_date between '2025-04-01' and '2025-05-01'
group by email 
order by ji.email 


select * from jira_issues ji
where resolution_date between '2025-04-01' and '2025-05-01'
and email = 'tcrook@tigerconnect.com'

where story_points = 0
and issue_type = 'Sub-task'

select * from subtasks s 

where parent_issue_id = 186905

select * from sprints




