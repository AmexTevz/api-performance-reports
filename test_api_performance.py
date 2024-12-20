import pytest
import allure
import time
from conftest import create_payload, measure_response_time, calculate_statistics


@allure.epic("API Performance Testing")
@allure.feature("Endpoint Comparison")
class TestEndpointPerformance:
    totals_differences = []
    submit_differences = []

    @allure.story("Totals Endpoint Comparison")
    @allure.description("Compare response times between original and new totals endpoints")
    @pytest.mark.parametrize("run_number", range(1, 11))
    def test_totals_endpoints(self, session_id, headers, endpoints, run_number):
        with allure.step(f"Compare Totals Endpoints - Run {run_number}"):
            original_totals_payload = create_payload(session_id, True)
            new_totals_payload = create_payload(session_id, False)

            # Measure original endpoint
            original_totals = measure_response_time(
                endpoints['totals']['original'],
                original_totals_payload,
                headers,
                "Totals Original"
            )

            # Measure new endpoint
            new_totals = measure_response_time(
                endpoints['totals']['changed'],
                new_totals_payload,
                headers,
                "Totals Changed"
            )

            # Calculate and store difference
            difference = new_totals['response_time'] - original_totals['response_time']
            self.totals_differences.append(difference)

            # Add result details to Allure report
            allure.attach(
                f"""
                Run: {run_number}
                Original Endpoint Response Time: {original_totals['response_time']:.2f}ms
                New Endpoint Response Time: {new_totals['response_time']:.2f}ms
                Difference: {difference:.2f}ms
                """,
                f"Run {run_number} Details",
                allure.attachment_type.TEXT
            )

            time.sleep(1)  # Delay between runs

    @allure.story("Submit Endpoint Comparison")
    @allure.description("Compare response times between original and new submit endpoints")
    @pytest.mark.parametrize("run_number", range(1, 11))
    def test_submit_endpoints(self, session_id, headers, endpoints, run_number):
        with allure.step(f"Compare Submit Endpoints - Run {run_number}"):
            original_submit_payload = create_payload(session_id, True, True)
            new_submit_payload = create_payload(session_id, False, True)

            # Measure original endpoint
            original_submit = measure_response_time(
                endpoints['submit']['original'],
                original_submit_payload,
                headers,
                "Submit Original"
            )

            # Measure new endpoint
            new_submit = measure_response_time(
                endpoints['submit']['changed'],
                new_submit_payload,
                headers,
                "Submit Changed"
            )

            # Calculate and store difference
            difference = new_submit['response_time'] - original_submit['response_time']
            self.submit_differences.append(difference)

            # Add result details to Allure report
            allure.attach(
                f"""
                Run: {run_number}
                Original Endpoint Response Time: {original_submit['response_time']:.2f}ms
                New Endpoint Response Time: {new_submit['response_time']:.2f}ms
                Difference: {difference:.2f}ms
                """,
                f"Run {run_number} Details",
                allure.attachment_type.TEXT
            )

            time.sleep(1)  # Delay between runs

    @allure.story("Statistics Calculation")
    @allure.description("Calculate and report statistics for all endpoint comparisons")
    def test_statistics(self):
        with allure.step("Calculate Totals Statistics"):
            totals_stats = calculate_statistics(self.totals_differences)
            allure.attach(
                f"""
                Smallest difference: {totals_stats['min']:.2f}ms
                Biggest difference: {totals_stats['max']:.2f}ms
                Median difference: {totals_stats['median']:.2f}ms
                """,
                "Totals Statistics",
                allure.attachment_type.TEXT
            )

        with allure.step("Calculate Submit Statistics"):
            submit_stats = calculate_statistics(self.submit_differences)
            allure.attach(
                f"""
                Smallest difference: {submit_stats['min']:.2f}ms
                Biggest difference: {submit_stats['max']:.2f}ms
                Median difference: {submit_stats['median']:.2f}ms
                """,
                "Submit Statistics",
                allure.attachment_type.TEXT
            )