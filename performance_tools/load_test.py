"""
Load testing script for Astrologer API performance validation
"""

import asyncio
import aiohttp
import time
import statistics
import json
from typing import List, Dict, Any
from dataclasses import dataclass
import argparse


@dataclass
class LoadTestResult:
    """Results from load testing"""
    endpoint: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float


class APILoadTester:
    """Load tester for API endpoints"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"X-API-Key": self.api_key},
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _make_request(self, method: str, endpoint: str, data: Dict | None = None) -> Dict[str, Any]:
        """Make a single request and measure response time"""
        start_time = time.time()
        success = False
        status_code = 0
        response_data = {}

        try:
            url = f"{self.base_url}{endpoint}"

            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    status_code = response.status
                    response_data = await response.json()
                    success = response.status == 200
            else:
                async with self.session.post(url, json=data) as response:
                    status_code = response.status
                    response_data = await response.json()
                    success = response.status == 200

        except Exception as e:
            response_data = {"error": str(e)}

        end_time = time.time()
        response_time = end_time - start_time

        return {
            "success": success,
            "response_time": response_time,
            "status_code": status_code,
            "data": response_data
        }

    async def _load_test_endpoint(self, method: str, endpoint: str, concurrent_requests: int,
                                total_requests: int, request_data: Dict | None = None) -> LoadTestResult:
        """Load test a specific endpoint"""
        print(f"Load testing {method} {endpoint} with {concurrent_requests} concurrent requests...")

        semaphore = asyncio.Semaphore(concurrent_requests)
        results = []

        async def make_request_with_semaphore():
            async with semaphore:
                return await self._make_request(method, endpoint, request_data)

        start_time = time.time()

        # Create all tasks
        tasks = [make_request_with_semaphore() for _ in range(total_requests)]

        # Execute tasks and collect results
        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        total_time = end_time - start_time

        # Process results
        response_times = []
        successful_requests = 0
        failed_requests = 0

        for result in results:
            if isinstance(result, Exception):
                failed_requests += 1
                continue

            if isinstance(result, dict):
                response_times.append(result["response_time"])
                if result["success"]:
                    successful_requests += 1
                else:
                    failed_requests += 1

        # Calculate statistics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            p99_response_time = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
        else:
            avg_response_time = median_response_time = p95_response_time = p99_response_time = 0

        requests_per_second = total_requests / total_time if total_time > 0 else 0
        error_rate = (failed_requests / total_requests) * 100 if total_requests > 0 else 0

        return LoadTestResult(
            endpoint=endpoint,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            median_response_time=median_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate
        )

    def _get_test_data(self) -> Dict[str, Any]:
        """Get sample test data for API requests"""
        return {
            "birth_chart": {
                "subject": {
                    "name": "Test User",
                    "year": 1990,
                    "month": 6,
                    "day": 15,
                    "hour": 12,
                    "minute": 30,
                    "city": "New York",
                    "nation": "US",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "timezone": "America/New_York"
                },
                "theme": "classic",
                "language": "EN"
            },
            "synastry_chart": {
                "first_subject": {
                    "name": "Person 1",
                    "year": 1990,
                    "month": 6,
                    "day": 15,
                    "hour": 12,
                    "minute": 30,
                    "city": "New York",
                    "nation": "US",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "timezone": "America/New_York"
                },
                "second_subject": {
                    "name": "Person 2",
                    "year": 1995,
                    "month": 3,
                    "day": 22,
                    "hour": 8,
                    "minute": 45,
                    "city": "Los Angeles",
                    "nation": "US",
                    "latitude": 34.0522,
                    "longitude": -118.2437,
                    "timezone": "America/Los_Angeles"
                },
                "theme": "classic",
                "language": "EN"
            }
        }

    async def run_comprehensive_load_test(self, concurrent_requests: int = 10,
                                        requests_per_endpoint: int = 100) -> List[LoadTestResult]:
        """Run comprehensive load test on all endpoints"""
        test_data = self._get_test_data()

        test_scenarios = [
            ("GET", "/api/v4/health", None),
            ("GET", "/", None),
            ("POST", "/api/v4/birth-data", test_data["birth_chart"]),
            ("POST", "/api/v4/birth-chart", test_data["birth_chart"]),
            ("POST", "/api/v4/synastry-chart", test_data["synastry_chart"]),
            ("POST", "/api/v4/relationship-score", test_data["synastry_chart"]),
        ]

        results = []

        for method, endpoint, data in test_scenarios:
            try:
                result = await self._load_test_endpoint(
                    method, endpoint, concurrent_requests, requests_per_endpoint, data
                )
                results.append(result)

                # Print immediate results
                print(f"\n{method} {endpoint} Results:")
                print(f"  Success Rate: {((result.successful_requests / result.total_requests) * 100):.1f}%")
                print(f"  Avg Response Time: {result.avg_response_time:.3f}s")
                print(f"  Requests/sec: {result.requests_per_second:.1f}")
                print(f"  95th Percentile: {result.p95_response_time:.3f}s")

            except Exception as e:
                print(f"Error testing {method} {endpoint}: {e}")

        return results

    def print_summary_report(self, results: List[LoadTestResult]):
        """Print comprehensive summary report"""
        print("\n" + "="*80)
        print("LOAD TEST SUMMARY REPORT")
        print("="*80)

        total_requests = sum(r.total_requests for r in results)
        total_successful = sum(r.successful_requests for r in results)
        overall_success_rate = (total_successful / total_requests * 100) if total_requests > 0 else 0

        print(f"\nOverall Statistics:")
        print(f"  Total Requests: {total_requests}")
        print(f"  Successful Requests: {total_successful}")
        print(f"  Overall Success Rate: {overall_success_rate:.1f}%")

        print(f"\nDetailed Results per Endpoint:")
        print("-" * 80)

        for result in results:
            print(f"\nEndpoint: {result.endpoint}")
            print(f"  Total Requests: {result.total_requests}")
            print(f"  Success Rate: {((result.successful_requests / result.total_requests) * 100):.1f}%")
            print(f"  Error Rate: {result.error_rate:.1f}%")
            print(f"  Avg Response Time: {result.avg_response_time:.3f}s")
            print(f"  Median Response Time: {result.median_response_time:.3f}s")
            print(f"  95th Percentile: {result.p95_response_time:.3f}s")
            print(f"  99th Percentile: {result.p99_response_time:.3f}s")
            print(f"  Requests/sec: {result.requests_per_second:.1f}")

        # Performance recommendations
        print(f"\nPerformance Analysis:")
        print("-" * 80)

        slow_endpoints = [r for r in results if r.avg_response_time > 2.0]
        if slow_endpoints:
            print(f"⚠️  Slow endpoints (>2s avg):")
            for endpoint in slow_endpoints:
                print(f"   - {endpoint.endpoint}: {endpoint.avg_response_time:.3f}s")

        high_error_endpoints = [r for r in results if r.error_rate > 5.0]
        if high_error_endpoints:
            print(f"🔴 High error rate endpoints (>5%):")
            for endpoint in high_error_endpoints:
                print(f"   - {endpoint.endpoint}: {endpoint.error_rate:.1f}%")

        if not slow_endpoints and not high_error_endpoints:
            print("✅ All endpoints performing within acceptable limits!")

        # Throughput analysis
        avg_throughput = statistics.mean([r.requests_per_second for r in results])
        print(f"\nThroughput Analysis:")
        print(f"  Average Throughput: {avg_throughput:.1f} requests/sec")

        if avg_throughput > 50:
            print("✅ Good throughput performance")
        elif avg_throughput > 20:
            print("⚠️  Moderate throughput - consider optimization")
        else:
            print("🔴 Low throughput - optimization needed")


async def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="Load test the Astrologer API")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--api-key", required=True, help="API key for authentication")
    parser.add_argument("--concurrent", type=int, default=10, help="Concurrent requests")
    parser.add_argument("--requests", type=int, default=100, help="Total requests per endpoint")

    args = parser.parse_args()

    async with APILoadTester(args.url, args.api_key) as tester:
        print(f"Starting load test against {args.url}")
        print(f"Concurrent requests: {args.concurrent}")
        print(f"Requests per endpoint: {args.requests}")
        print("-" * 50)

        results = await tester.run_comprehensive_load_test(
            concurrent_requests=args.concurrent,
            requests_per_endpoint=args.requests
        )

        tester.print_summary_report(results)


if __name__ == "__main__":
    asyncio.run(main())