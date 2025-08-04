<!-- # Log File Analyzer CLI

This is a command-line tool that parses Apache web server logs, stores structured data in MySQL, and generates analytical traffic reports.

## Features

- Parses Apache Common Log Format
- Extracts IPs, timestamps, HTTP methods, status codes, user agents
- Stores data in normalized MySQL tables
- Generates reports:
  - Top N IPs by request count
  - HTTP status code distribution
  - Hourly traffic volume

## Setup

```bash
python -m venv venv
source venv/bin/activate  
pip install -r requirements.txt
```

### MySQL Setup

1. Install MySQL and start the server
2. Open MySQL Workbench and execute the script in `sql/create_tables.sql`:

```sql
CREATE DATABASE IF NOT EXISTS weblogs_db;
USE weblogs_db;
-- Create user_agents and log_entries tables
```

3. Update `config.ini` with your MySQL credentials:

```ini
[mysql]
host = localhost
user = root
password = your_password
database = weblogs_db
```

## Log Format Assumed

The application expects logs in Apache Common Log Format, like:

```
127.0.0.1 - - [10/Oct/2023:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326 "-" "Mozilla/5.0"
```

Format breakdown:
- IP address
- Timestamp
- Request method and path
- Status code
- Bytes sent
- Referrer
- User agent string

## CLI Usage Guide

Process a log file:
```bash
python main.py process_logs sample_logs/access.log
```

Generate reports:
```bash
python main.py process_logs sample_logs/access.log --batch_size 500
python main.py generate_report top_n_ips --n 5
python main.py generate_report status_code_distribution
python main.py generate_report hourly_traffic




```

## Database Schema Description

- user_agents:
  - id (PK)
  - user_agent_string
  - os
  - browser
  - device_type

- log_entries:
  - id (PK)
  - ip_address
  - timestamp
  - method
  - path
  - status_code
  - bytes_sent
  - referrer
  - user_agent_id (FK)

## Regex Pattern Explanation

Log lines are parsed using this regex:

```python
r' 
r'(?P<ip>\S+)\s+'                        
        r'\S+\s+\S+\s+'                           
        r'\[(?P<timestamp>[^\]]+)\]\s+'           
        r'"(?P<request>[^"]+)"\s+'                
        r'(?P<status>\d{3})\s+'                   
        r'(?P<size>\S+)\s+'                       
        r'"(?P<referrer>[^"]*)"\s+'               
        r'"(?P<user_agent>[^"]*)"'  '

```

This extracts:
- IP address
- Timestamp
- Request method/path
- HTTP status
- Bytes
- Referrer
- User Agent

## Known Limitations and Future Improvements

- Currently assumes Apache-style log format only
- Limited user-agent parsing (basic OS/Browser extraction)
- No support for NGINX or JSON logs
- Could integrate visualization/reporting via web dashboard
- Log file errors are skipped silently (can enhance logging)

## Project Structure

- main.py: CLI entry point
- log_parser.py: Log parsing logic
- mysql_handler.py: MySQL insert/query logic
- config.ini: Database configuration
- sql/create_tables.sql: SQL schema
- sample_logs/: Example logs for testing
 -->
