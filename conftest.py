import pytest
import allure
import requests
import time
from statistics import median


@pytest.fixture(scope="session")
def session_id():
    """Fixture to get authentication session ID"""
    with allure.step("Authenticate to get session ID"):
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
            allure.attach(str(session_id), "Session ID", allure.attachment_type.TEXT)
            return session_id
        except Exception as e:
            allure.attach(str(e), "Authentication Error", allure.attachment_type.TEXT)
            pytest.fail(f"Authentication failed: {e}")


@pytest.fixture(scope="session")
def headers():
    """Common headers for API requests"""
    return {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': 'ff9271bf1ffc4da9957c20c12b34cf17'
    }


@pytest.fixture(scope="session")
def endpoints():
    """API endpoints configuration"""
    return {
        'totals': {
            'original': 'https://digitalmwdev.azure-api.net/v2/order/fullcart/totals',
            'changed': 'https://orderservice-ci-v2-3-staging.digital-middleware-ase-dev.p.azurewebsites.net/v2/pos/totals'
        },
        'submit': {
            'original': 'https://digitalmwdev.azure-api.net/v2/order/fullcart/submit',
            'changed': 'https://orderservice-ci-v2-3-staging.digital-middleware-ase-dev.p.azurewebsites.net/v2/pos/submit'
        }
    }


def create_payload(session_id, is_original_endpoint, is_submit=False):
    """Create payload for API requests"""
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


def measure_response_time(url, payload, headers, name):
    """Measure API response time"""
    try:
        with allure.step(f"Make request to {name}"):
            start_time = time.time()
            response = requests.post(url, json=payload, headers=headers)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            response_json = response.json()
            is_successful = response_json.get('Status') == 'SUCCESS'

            allure.attach(
                str(response_json),
                f"{name} Response",
                allure.attachment_type.JSON
            )

            if not is_successful:
                allure.attach(
                    str(response_json),
                    f"{name} Error Response",
                    allure.attachment_type.TEXT
                )

            return {
                'name': name,
                'status_code': response.status_code,
                'response_time': response_time,
                'success': is_successful,
                'url': url,
                'response_body': response_json
            }
    except Exception as e:
        allure.attach(str(e), f"{name} Error", allure.attachment_type.TEXT)
        pytest.fail(f"Error in {name}: {str(e)}")


def calculate_statistics(differences):
    """Calculate statistics from a list of differences"""
    if not differences:
        return None

    return {
        'min': min(differences),
        'max': max(differences),
        'median': median(differences)
    }