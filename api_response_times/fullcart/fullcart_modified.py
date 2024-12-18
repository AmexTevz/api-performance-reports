import requests
import time
from statistics import median


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
        response_time = (end_time - start_time) * 1000

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
            'url': url,
            'response_body': response_json
        }
    except Exception as e:
        print(f"Error in {name}: {str(e)}")
        return None


def calculate_statistics(differences):
    if not differences:
        return None

    return {
        'min': min(differences),
        'max': max(differences),
        'median': median(differences)
    }


def print_run_statistics(stats, endpoint_type):
    if stats:
        print(f"\n=== {endpoint_type} Statistics (10 runs) ===")
        print(f"Smallest difference: {stats['min']:.2f}ms")
        print(f"Biggest difference: {stats['max']:.2f}ms")
        print(f"Median difference: {stats['median']:.2f}ms")


def print_comparison_results(original_result, new_result, endpoint_type, run_number=None):
    if original_result and new_result:
        difference = new_result['response_time'] - original_result['response_time']
        if run_number is None:
            print(f"=== {endpoint_type} Comparison (Run) ===")
            print(f"ENDPOINT 1 ({original_result['url']})")
            print("-" * 73)
            print(f"ENDPOINT 2 ({new_result['url']})")
        else:
            if run_number == 1:  # Print header before first run
                print(f"\n=== {endpoint_type} Comparison (Run) ===")
                print(f"ENDPOINT 1 ({original_result['url']})")
                print("-" * 73)
                print(f"ENDPOINT 2 ({new_result['url']})")
                print("\nRun\tENDPOINT 1 time\tENDPOINT 2 time\tDIFFERENCE time")
                print("-" * 73)
            print(
                f"{run_number}\t{original_result['response_time']:.2f}ms\t\t{new_result['response_time']:.2f}ms\t\t{difference:.2f}ms")
        return difference
    return None


def create_payload(session_id, is_original_endpoint, is_submit=False):
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

    base_payload = {
        "PropertyID": "142",
        "RevenueCenterID": "208",
        "ClientID": "3289FE1A-A4CA-49DC-9CDF-C2831781E850",
        "SessionID": session_id,
        "OrderTypeIdRef": 2,
        "GuestCheckRef": "",
        "cart": cart_payload
    }

    if is_submit:
        base_payload.update({
            "Tip": 0,
            "payment": {
                "authCode": "Test Check",
                "cardNumber": "XXXXXXX1234",
                "tenderType": "2001002",
                "amount": 0.000 if is_original_endpoint else 3.1500
            }
        })

    return base_payload


def compare_totals_endpoints(session_id, headers, endpoints):
    totals_differences = []

    for i in range(10):
        original_totals_payload = create_payload(session_id, True)
        new_totals_payload = create_payload(session_id, False)

        original_totals = measure_response_time(
            endpoints['totals']['original'],
            original_totals_payload,
            headers,
            "Totals Original"
        )
        new_totals = measure_response_time(
            endpoints['totals']['changed'],
            new_totals_payload,
            headers,
            "Totals Changed"
        )
        difference = print_comparison_results(original_totals, new_totals, "Totals", i + 1)
        if difference is not None:
            totals_differences.append(difference)

        time.sleep(1)

    totals_stats = calculate_statistics(totals_differences)
    print_run_statistics(totals_stats, "Totals")
    return totals_differences


def compare_submit_endpoints(session_id, headers, endpoints):
    submit_differences = []

    for i in range(10):
        original_submit_payload = create_payload(session_id, True, True)
        new_submit_payload = create_payload(session_id, False, True)

        original_submit = measure_response_time(
            endpoints['submit']['original'],
            original_submit_payload,
            headers,
            "Submit Original"
        )
        new_submit = measure_response_time(
            endpoints['submit']['changed'],
            new_submit_payload,
            headers,
            "Submit Changed"
        )
        difference = print_comparison_results(original_submit, new_submit, "Submit", i + 1)
        if difference is not None:
            submit_differences.append(difference)

        time.sleep(1)

    submit_stats = calculate_statistics(submit_differences)
    print_run_statistics(submit_stats, "Submit")
    return submit_differences


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

    print("\n=== ENVIRONMENT => DEV/CI ====\n")


    compare_totals_endpoints(session_id, headers, endpoints)

    print("\n")

    compare_submit_endpoints(session_id, headers, endpoints)


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