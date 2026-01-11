import datetime
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

@shared_task
def generate_crm_report():
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # GraphQL Query for report data
    query = gql("""
    query {
      allCustomers { edges { node { id } } }
      allOrders {
        edges {
          node {
            totalAmount
          }
        }
      }
    }
    """)

    try:
        result = client.execute(query)
        
        customers_count = len(result['allCustomers']['edges'])
        orders = result['allOrders']['edges']
        orders_count = len(orders)
        total_revenue = sum(float(o['node']['totalAmount']) for o in orders)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{timestamp} - Report: {customers_count} customers, {orders_count} orders, {total_revenue} revenue\n"

        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(log_message)
            
    except Exception as e:
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(f"Error generating report: {str(e)}\n")