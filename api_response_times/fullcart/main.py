import requests
import time


def authenticate():
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
            'success': is_successful,
            'url': url
        }
    except Exception as e:
        print(f"Error in {name}: {str(e)}")
        return None


def print_comparison_results(original_result, new_result, endpoint_type):
    if original_result and new_result:
        difference = new_result['response_time'] - original_result['response_time']

        print(f"ENDPOINT - {original_result['url']}")
        print(f"Response time: {original_result['response_time']:.2f}ms")
        print(f"ENDPOINT - {new_result['url']}")
        print(f"Response time: {new_result['response_time']:.2f}ms")
        print(f"Difference: {difference:.2f}ms")


def compare_endpoints(session_id):
    headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': 'ff9271bf1ffc4da9957c20c12b34cf17'
    }

    endpoints = {
        'totals': {
            'original': 'https://digitalmwdev.azure-api.net/v2/order/fullcart/totals',
            'changed': 'https://orderservice-ci-v2-3-staging.digital-middleware-ase-dev.p.azurewebsites.net/v2/pos/totals'
        },
        'submit': {
            'original': 'https://digitalmwdev.azure-api.net/v2/order/fullcart/submit',
            'changed': 'https://orderservice-ci-v2-3-staging.digital-middleware-ase-dev.p.azurewebsites.net/v2/pos/submit'
        }
    }

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
        ],
        "Discounts": [
            {
                "Code": "4",
                "AmountOrPercent": 0
            }
        ]
    }

    fullcart_totals_payload = {
        "PropertyID": "142",
        "RevenueCenterID": "208",
        "ClientID": "3289FE1A-A4CA-49DC-9CDF-C2831781E850",
        "SessionID": session_id,
        "OrderTypeIdRef": 2,
        "GuestCheckRef": "",
        "cart": cart_payload
    }

    fullcart_submit_payload = fullcart_totals_payload.copy()
    fullcart_submit_payload.update({
        "Tip": 0,
        "payment": {
            "authCode": "Test Check",
            "cardNumber": "XXXXXXX1234",
            "tenderType": "2001002",
            "amount": 3.1500
        }
    })

    print("\n=== ENVIRONMENT => DEV/CI ====\n")


    print("=== Totals Endpoints ===")
    fullcart_totals = measure_response_time(endpoints['totals']['original'], fullcart_totals_payload, headers, "Totals Original")
    staging_totals = measure_response_time(endpoints['totals']['changed'], fullcart_totals_payload, headers, "Totals Changed")
    print_comparison_results(fullcart_totals, staging_totals, "Totals")


    print("\n=== Submit Endpoints ===")
    fullcart_submit = measure_response_time(endpoints['submit']['original'], fullcart_submit_payload, headers, "Submit Original")
    staging_submit = measure_response_time(endpoints['submit']['changed'], fullcart_submit_payload, headers, "Submit Changed")
    print_comparison_results(fullcart_submit, staging_submit, "Submit")


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