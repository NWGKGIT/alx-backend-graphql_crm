# CRM Project Setup

### Setup Instructions
1. **Install Redis**: Install redis-server on your machine.
2. **Install dependencies**: Run `pip install -r requirements.txt`.
3. **Run migrations**: Run `python manage.py migrate`.
4. **Start Celery worker**: Run `celery -A crm worker -l info`.
5. **Start Celery Beat**: Run `celery -A crm beat -l info`.
6. **Verify logs**: Check `/tmp/crm_report_log.txt` for the generated report.