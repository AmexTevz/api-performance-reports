import requests
import time


def authenticate():
    """Perform authentication and get session info"""
    auth_url = 'https://digitalmwdev.azure-api.net/v2/catalog/session/begin'
    headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': 'ff9271bf1ffc4da9957c20c12b34cf17'
    }

    auth_payload = {
        "ClientID": "3289FE1A-A4CA-49DC-9CDF-C2831781E850",
        "username": "internal",
        "passkey": "P455w0rd"
    }

    try:
        auth_response = requests.post(auth_url, json=auth_payload, headers=headers)
        auth_response.raise_for_status()
        session_id = auth_response.json().get('SessionID')
        if not session_id:
            raise Exception("No SessionID in response")
        return session_id
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None


def measure_response_time(url, payload, headers, name):
    """Measure response time for a single request"""
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers)
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds

        # Check for success in response body
        response_json = response.json()
        is_successful = response_json.get('Status') == 'SUCCESS'
        if not is_successful:
            print(f"Warning: {name} request did not return Status=SUCCESS")
            print(f"Response body: {response_json}")

        return {
            'name': name,
            'status_code': response.status_code,
            'response_time': response_time,
            'success': is_successful
        }
    except Exception as e:
        print(f"Error in {name}: {str(e)}")
        return None



def compare_endpoints(session_id):
    headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': 'ff9271bf1ffc4da9957c20c12b34cf17'
    }

    # Endpoints
    totals_original = 'https://digitalmwdev.azure-api.net/v2/order/fullcart/totals'
    totals_changed = 'https://orderservice-ci-v2-3-staging.digital-middleware-ase-dev.p.azurewebsites.net/v2/pos/totals'
    submit_original = 'https://digitalmwdev.azure-api.net/v2/order/fullcart/submit'
    submit_changed = 'https://orderservice-ci-v2-3-staging.digital-middleware-ase-dev.p.azurewebsites.net/v2/pos/submit'

    # Base payload
    cart_payload = {
        "items": [
            {
                "ID": "1050002-1",
                "Price": 3.00,
                "Quantity": 1,
                "Freetext": None,
                "Condiments": [],
                "Modifiers": []
            }
        ]
    }

    # Common payload fields
    base_payload = {
        "PropertyID": "142",
        "RevenueCenterID": "208",
        "ClientID": "3289FE1A-A4CA-49DC-9CDF-C2831781E850",
        "SessionID": session_id,
        "OrderTypeIdRef": 2,
        "GuestCheckRef": "",
        "cart": cart_payload
    }

    # Create submit payload with payment info
    submit_payload = base_payload.copy()
    submit_payload.update({
        "Tip": 0,
        "payment": {
            "authCode": "Test Check",
            "cardNumber": "XXXXXXX1234",
            "tenderType": "2001002",
            "amount": 3.1500
        }
    })
    print("\n==== DEV/CI ENVIRONMENT =====\n")
    print("\n=== Testing Totals Endpoints ===")
    totals_orig = measure_response_time(totals_original, base_payload, headers, "Totals Original")
    totals_new = measure_response_time(totals_changed, base_payload, headers, "Totals Changed")

    if totals_orig and totals_new:
        difference = totals_new['response_time'] - totals_orig['response_time']
        print(f"\nTotals Comparison:")
        print(f"ENDPOINT - {totals_original}")
        print(f"fullcart/totals: {totals_orig['response_time']:.2f}ms")
        print(f"ENDPOINT - {totals_changed}")
        print(f"staging/pos/totals:  {totals_new['response_time']:.2f}ms")
        print(f"Difference: {difference:.2f}ms")

    print("\n=== Testing Submit Endpoints ===")
    submit_orig = measure_response_time(submit_original, submit_payload, headers, "Submit Original")
    submit_new = measure_response_time(submit_changed, submit_payload, headers, "Submit Changed")

    if submit_orig and submit_new:
        difference = submit_new['response_time'] - submit_orig['response_time']
        print(f"\nSubmit Comparison:")
        print(f"ENDPOINT - {submit_original}")
        print(f"fullcart/totals: {submit_orig['response_time']:.2f}ms")
        print(f"ENDPOINT - {submit_changed}")
        print(f"staging/pos/totals:  {submit_new['response_time']:.2f}ms")
        print(f"Difference: {difference:.2f}ms")


def main():
    print("Authenticating...")
    session_id = authenticate()
    if not session_id:
        print("Failed to authenticate. Exiting.")
        return

    print(f"Successfully authenticated. SessionID: {session_id}")
    compare_endpoints(session_id)


if __name__ == "__main__":
    main()