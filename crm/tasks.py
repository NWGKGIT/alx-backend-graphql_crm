from datetime import datetime
import requests
from celery import shared_task

@shared_task
def generate_crm_report():
    url = "http://localhost:8000/graphql"
    query = """
    query {
      allCustomers { edges { node { id } } }
      allOrders { edges { node { totalAmount } } }
    }
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "/tmp/crm_report_log.txt"

    try:
        response = requests.post(url, json={'query': query})
        result = response.json()
        
        customers = len(result['data']['allCustomers']['edges'])
        orders_data = result['data']['allOrders']['edges']
        orders_count = len(orders_data)
        total_revenue = sum(float(o['node']['totalAmount']) for o in orders_data)

        log_entry = f"{timestamp} - Report: {customers} customers, {orders_count} orders, {total_revenue} revenue\n"
        with open(log_file, "a") as f:
            f.write(log_entry)
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - Error: {str(e)}\n")