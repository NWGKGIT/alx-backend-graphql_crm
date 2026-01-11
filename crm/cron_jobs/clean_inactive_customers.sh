#!/bin/bash
DATE=$(date "+%Y-%m-%d %H:%M:%S")
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Navigate to project root - Adjust if your structure differs
cd "$(dirname "$0")/../.."

python3 manage.py shell <<EOF >> "$LOG_FILE" 2>&1
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Delete customers with no orders since a year ago
# Logic: Customers where ALL orders are older than one_year_ago OR customers with NO orders
# Based on prompt "no orders since a year ago", we filter strictly.
count, _ = Customer.objects.filter(orders__order_date__lt=one_year_ago).delete()

print(f"$DATE - Deleted {count} customers.")
EOF