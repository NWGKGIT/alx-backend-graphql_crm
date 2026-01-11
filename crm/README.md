# CRM Setup and Task Automation

This project uses Celery and Celery Beat to automate CRM reports.

## Setup Instructions

1. **Install Redis and dependencies**:
   - Install Redis: `sudo apt install redis-server`
   - Install dependencies: `pip install celery redis django-celery-beat`

2. **Run migrations**:
   - `python manage.py migrate`

3. **Start Celery worker**:
   - `celery -A crm worker -l info`

4. **Start Celery Beat**:
   - `celery -A crm beat -l info`

5. **Verify logs**:
   - Check the generated report at: `/tmp/crm_report_log.txt`

## Tasks Documentation
- The `generate_crm_report` task runs every Monday at 6:00 AM.
- It queries the GraphQL endpoint for customers, orders, and revenue.
- Outputs results to the log file with a timestamp.