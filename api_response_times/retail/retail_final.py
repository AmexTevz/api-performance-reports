# import requests
# import time
# import copy
# from statistics import median
#
#
# def authenticate():
#     # Authentication code remains the same
#     auth_url = 'https://catalogservice-ci-v2-3.digital-middleware-ase-dev.p.azurewebsites.net/v2/session/begin'
#     headers = {
#         'Content-Type': 'application/json',
#         'Ocp-Apim-Subscription-Key': 'dec176b71bc447e99c42cc5ccef98d59'
#     }
#
#     auth_payload = {
#         "ClientID": "3289FE1A-A4CA-49DC-9CDF-C2831781E850",
#         "username": "internal",
#         "passkey": "P455w0rd"
#     }
#
#     try:
#         auth_response = requests.post(auth_url, json=auth_payload, headers=headers)
#         auth_response.raise_for_status()
#         session_id = auth_response.json().get('SessionID')
#         if not session_id:
#             raise Exception("No SessionID in response")
#         return session_id
#     except Exception as e:
#         print(f"Authentication failed: {e}")
#         return None
#
#
# def measure_response_time(url, payload, headers, name):
#     try:
#         start_time = time.time()
#         response = requests.post(url, json=payload, headers=headers)
#         end_time = time.time()
#         response_time = (end_time - start_time) * 1000
#
#         response_json = response.json()
#         is_successful = response_json.get('Status') == 'SUCCESS'
#         if not is_successful:
#             print(f"Warning: {name} request did not return Status=SUCCESS")
#             print(f"Response body: {response_json}")
#
#         return {
#             'name': name,
#             'status_code': response.status_code,
#             'response_time': response_time,
#             'success': is_successful,
#             'url': url,
#             'response_body': response_json
#         }
#     except Exception as e:
#         print(f"Error in {name}: {str(e)}")
#         return None
#
#
# def calculate_statistics(differences):
#     if not differences:
#         return None
#
#     return {
#         'min': min(differences),
#         'max': max(differences),
#         'median': median(differences)
#     }
#
#
# def print_run_statistics(stats, endpoint_type):
#     if stats:
#         print(f"\n=== {endpoint_type} Statistics (10 runs) ===")
#         print(f"Smallest difference: {stats['min']:.2f}ms")
#         print(f"Biggest difference: {stats['max']:.2f}ms")
#         print(f"Median difference: {stats['median']:.2f}ms")
#
#
# def print_comparison_results(fullcart_result, staging_result, endpoint_type):
#     if fullcart_result and staging_result:
#         difference = staging_result['response_time'] - fullcart_result['response_time']
#         print(f"=== {endpoint_type} Comparison (Run) ===")
#         print(f"ENDPOINT ({fullcart_result['url']}):")
#         print(f"Response time: {fullcart_result['response_time']:.2f}ms")
#         print(f"ENDPOINT ({staging_result['url']}):")
#         print(f"Response time: {staging_result['response_time']:.2f}ms")
#         print(f"Difference: {difference:.2f}ms")
#         return difference
#     return None
#
#
# def create_payload(session_id, is_fullcart_endpoint, is_submit=False):
#     # Base cart items
#     cart_payload = {
#         "items": [
#             {
#                 "ID": "1050002-1",
#                 "Price": 3.00,
#                 "Quantity": 1,
#                 "Freetext": None,
#                 "Condiments": [],
#                 "Modifiers": []
#             }
#         ],
#         "Discounts": [
#             {
#                 "Code": "4",
#                 "AmountOrPercent": 0 if is_fullcart_endpoint else 3.1500
#             }
#         ]
#     }
#
#     # Base payload for both totals and submit
#     base_payload = {
#         "PropertyID": "142",
#         "RevenueCenterID": "208",
#         "ClientID": "3289FE1A-A4CA-49DC-9CDF-C2831781E850",
#         "SessionID": session_id,
#         "OrderTypeIdRef": 2,
#         "GuestCheckRef": "",
#         "cart": cart_payload
#     }
#
#     if is_submit:
#         base_payload.update({
#             "Tip": 0,
#             "payment": {
#                 "authCode": "Test Check",
#                 "cardNumber": "XXXXXXX1234",
#                 "tenderType": "2001002",
#                 "amount": 0.000 if is_fullcart_endpoint else 3.1500
#             }
#         })
#
#     return base_payload
#
#
# def compare_endpoints(session_id):
#     headers = {
#         'Content-Type': 'application/json',
#         'Ocp-Apim-Subscription-Key': 'dec176b71bc447e99c42cc5ccef98d59'
#     }
#
#     endpoints = {
#         'totals': {
#             'fullcart': 'https://orderservice-ci-v2-3.digital-middleware-ase-dev.p.azurewebsites.net/v2/pos/totals',
#             'staging': 'https://orderservice-ci-v2-3-staging.digital-middleware-ase-dev.p.azurewebsites.net/v2/pos/totals'
#         },
#         'submit': {
#             'fullcart': 'https://orderservice-ci-v2-3.digital-middleware-ase-dev.p.azurewebsites.net/v2/pos/submit',
#             'staging': 'https://orderservice-ci-v2-3-staging.digital-middleware-ase-dev.p.azurewebsites.net/v2/pos/submit'
#         }
#     }
#
#     print("\n=== ENVIRONMENT => RETAIL DEV PRIVATE ====\n")
#
#     totals_differences = []
#     submit_differences = []
#
#     for i in range(10):
#         print(f"\nRun {i + 1}/10")
#
#         # Test totals endpoints
#         fullcart_totals_payload = create_payload(session_id, True)
#         staging_totals_payload = create_payload(session_id, False)
#
#         fullcart_totals = measure_response_time(
#             endpoints['totals']['fullcart'],
#             fullcart_totals_payload,
#             headers,
#             "Totals Fullcart"
#         )
#         staging_totals = measure_response_time(
#             endpoints['totals']['staging'],
#             staging_totals_payload,
#             headers,
#             "Totals Staging"
#         )
#         difference = print_comparison_results(fullcart_totals, staging_totals, "Totals")
#         if difference is not None:
#             totals_differences.append(difference)
#
#         # Test submit endpoints
#         fullcart_submit_payload = create_payload(session_id, True, True)
#         staging_submit_payload = create_payload(session_id, False, True)
#
#         fullcart_submit = measure_response_time(
#             endpoints['submit']['fullcart'],
#             fullcart_submit_payload,
#             headers,
#             "Submit Fullcart"
#         )
#         staging_submit = measure_response_time(
#             endpoints['submit']['staging'],
#             staging_submit_payload,
#             headers,
#             "Submit Staging"
#         )
#         difference = print_comparison_results(fullcart_submit, staging_submit, "Submit")
#         if difference is not None:
#             submit_differences.append(difference)
#
#         # Add a small delay between runs to avoid overwhelming the server
#         time.sleep(1)
#
#     # Print statistics after all runs
#     totals_stats = calculate_statistics(totals_differences)
#     submit_stats = calculate_statistics(submit_differences)
#
#     print_run_statistics(totals_stats, "Totals")
#     print_run_statistics(submit_stats, "Submit")
#
#
# def main():
#     print("Authenticating...")
#     session_id = authenticate()
#     if not session_id:
#         print("Failed to authenticate. Exiting.")
#         return
#
#     print(f"Successfully authenticated. SessionID: {session_id}")
#     compare_endpoints(session_id)
#
#
# if __name__ == "__main__":
#     main()


import requests
import time
import copy
from statistics import median


def authenticate():

    auth_url = 'https://catalogservice-ci-v2-3.digital-middleware-ase-dev.p.azurewebsites.net/v2/session/begin'
    headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': 'dec176b71bc447e99c42cc5ccef98d59'
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


def print_comparison_results(fullcart_result, staging_result, endpoint_type, run_number=None):
    if fullcart_result and staging_result:
        difference = staging_result['response_time'] - fullcart_result['response_time']
        if run_number is None:
            print(f"=== {endpoint_type} Comparison (Run) ===")
            print(f"ENDPOINT 1 ({fullcart_result['url']})")
            print("-" * 73)
            print(f"ENDPOINT 2 ({staging_result['url']})")
        else:
            if run_number == 1:  # Print header before first run
                print(f"\n=== {endpoint_type} Comparison (Run) ===")
                print(f"ENDPOINT 1 ({fullcart_result['url']})")
                print("-" * 73)
                print(f"ENDPOINT 2 ({staging_result['url']})")
                print("\nRun\tENDPOINT 1 time\tENDPOINT 2 time\tDIFFERENCE time")
                print("-" * 73)
            print(f"{run_number}\t{fullcart_result['response_time']:.2f}ms\t\t{staging_result['response_time']:.2f}ms\t\t{difference:.2f}ms")
        return difference
    return None


def create_payload(session_id, is_fullcart_endpoint, is_submit=False):
    # Base cart items
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
                "AmountOrPercent": 0 if is_fullcart_endpoint else 3.1500
            }
        ]
    }

    # Base payload for both totals and submit
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
                "amount": 0.000 if is_fullcart_endpoint else 3.1500
            }
        })

    return base_payload


def compare_totals_endpoints(session_id, headers, endpoints):
    totals_differences = []

    # Test totals endpoints first
    for i in range(10):
        fullcart_totals_payload = create_payload(session_id, True)
        staging_totals_payload = create_payload(session_id, False)

        fullcart_totals = measure_response_time(
            endpoints['totals']['fullcart'],
            fullcart_totals_payload,
            headers,
            "Totals Fullcart"
        )
        staging_totals = measure_response_time(
            endpoints['totals']['staging'],
            staging_totals_payload,
            headers,
            "Totals Staging"
        )
        difference = print_comparison_results(fullcart_totals, staging_totals, "Totals", i + 1)
        if difference is not None:
            totals_differences.append(difference)

        # Add a small delay between runs
        time.sleep(1)

    # Print totals statistics
    totals_stats = calculate_statistics(totals_differences)
    print_run_statistics(totals_stats, "Totals")
    return totals_differences


def compare_submit_endpoints(session_id, headers, endpoints):
    submit_differences = []

    # Now test submit endpoints
    for i in range(10):
        fullcart_submit_payload = create_payload(session_id, True, True)
        staging_submit_payload = create_payload(session_id, False, True)

        fullcart_submit = measure_response_time(
            endpoints['submit']['fullcart'],
            fullcart_submit_payload,
            headers,
            "Submit Fullcart"
        )
        staging_submit = measure_response_time(
            endpoints['submit']['staging'],
            staging_submit_payload,
            headers,
            "Submit Staging"
        )
        difference = print_comparison_results(fullcart_submit, staging_submit, "Submit", i + 1)
        if difference is not None:
            submit_differences.append(difference)

        # Add a small delay between runs
        time.sleep(1)

    # Print submit statistics
    submit_stats = calculate_statistics(submit_differences)
    print_run_statistics(submit_stats, "Submit")
    return submit_differences


def compare_endpoints(session_id):
    headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': 'dec176b71bc447e99c42cc5ccef98d59'
    }

    endpoints = {
        'totals': {
            'fullcart': 'https://orderservice-ci-v2-3.digital-middleware-ase-dev.p.azurewebsites.net/v2/pos/totals',
            'staging': 'https://orderservice-ci-v2-3-staging.digital-middleware-ase-dev.p.azurewebsites.net/v2/pos/totals'
        },
        'submit': {
            'fullcart': 'https://orderservice-ci-v2-3.digital-middleware-ase-dev.p.azurewebsites.net/v2/pos/submit',
            'staging': 'https://orderservice-ci-v2-3-staging.digital-middleware-ase-dev.p.azurewebsites.net/v2/pos/submit'
        }
    }

    print("\n=== ENVIRONMENT => RETAIL DEV PRIVATE ====\n")

    # Run all totals endpoint comparisons first
    totals_differences = compare_totals_endpoints(session_id, headers, endpoints)

    print("\n")  # Add spacing between totals and submit results

    # Only after totals are complete, run submit endpoint comparisons
    submit_differences = compare_submit_endpoints(session_id, headers, endpoints)


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