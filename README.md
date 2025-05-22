# Engineering Metrics

A Python application that collects and processes engineering metrics from Jira, focusing on team performance and sprint analytics.

## Features

- Collects team member data from Flow
- Syncs Jira aliases with team members
- Processes Jira issues and their relationships
- Calculates story points for subtasks
- Maintains sprint information
- Tracks parent-child relationships between issues

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Jira API access
- Flow API access

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/EngineeringMetrics.git
cd EngineeringMetrics
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   Create a `.env` file with the following variables:

```env
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=your_database_port
JIRA_API_TOKEN=your_jira_token
FLOW_API_TOKEN=your_flow_token
```

## Database Setup

1. Create the database tables:

```bash
psql -U your_user -d your_database -f database/jira_issues.sql
```

## Usage

Run the application with a date range:

```bash
python application/app.py 2024-04-01 2024-04-30
```

The script will:

1. Fetch team members from Flow
2. Update Jira aliases
3. Collect Jira issues for the specified date range
4. Process and store the data in the database
5. Calculate story points for subtasks

## Project Structure

```
EngineeringMetrics/
├── application/
│   ├── app.py                 # Main application entry point
│   ├── repository/
│   │   ├── db_connection.py   # Database connection manager
│   │   └── rds_repository.py  # Database operations
│   └── API/
│       ├── Flow_data.py       # Flow API integration
│       └── Jira_data.py       # Jira API integration
├── database/
│   └── jira_issues.sql        # Database schema
├── common/
│   └── metrics_util.py        # Utility functions
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## Database Schema

### Main Tables

- `jira_issues`: Core issue information
- `sprints`: Sprint details
- `issue_sprints`: Issue-sprint relationships
- `subtasks`: Parent-child relationships

### Key Features

- Story points tracking
- Sprint management
- Team member associations
- Subtask relationships

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.
