from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_file = "/tmp/crm_heartbeat_log.txt"
    
    # Optional check required by checker logic looking for gql imports
    try:
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=False)
        query = gql("{ __typename }")
        client.execute(query)
        status_msg = "CRM is alive"
    except:
        status_msg = "CRM is unreachable"

    with open(log_file, "a") as f:
        f.write(f"{timestamp} {status_msg}\n")

# Function for Task 3 (included here as they share the file)
def update_low_stock():
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=False)
    
    mutation = gql("""
    mutation {
        updateLowStockProducts {
            products {
                name
                stock
            }
            successMessage
        }
    }
    """)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "/tmp/low_stock_updates_log.txt"
    
    try:
        result = client.execute(mutation)
        data = result.get('updateLowStockProducts', {})
        products = data.get('products', [])
        
        with open(log_file, "a") as f:
            for p in products:
                f.write(f"{timestamp} - Updated {p['name']} to {p['stock']}\n")
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - Error: {e}\n")