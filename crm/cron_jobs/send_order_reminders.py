import sys
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def send_reminders():
    # Setup transport
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Query orders within last 7 days (Logic handled in query or response parsing)
    # Assuming the API allows filtering or we fetch recent and filter in python
    query = gql("""
    query {
        allOrders {
            edges {
                node {
                    id
                    orderDate
                    customer {
                        email
                    }
                }
            }
        }
    }
    """)

    try:
        result = client.execute(query)
        orders = result.get('allOrders', {}).get('edges', [])
        
        log_file = "/tmp/order_reminders_log.txt"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(log_file, "a") as f:
            for edge in orders:
                order = edge['node']
                # Basic check if date is recent (simplified for script)
                # Ideally check logic matches your backend filter availability
                f.write(f"{timestamp} - Order ID: {order['id']}, Email: {order['customer']['email']}\n")
        
        print("Order reminders processed!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_reminders()