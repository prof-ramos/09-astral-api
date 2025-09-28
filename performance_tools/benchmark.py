"""
Benchmark script for comparing API performance before/after optimizations
"""

import asyncio
import time
import statistics
import json
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import httpx


@dataclass
class BenchmarkResult:
    """Single benchmark result"""
    endpoint: str
    method: str
    response_time: float
    status_code: int
    success: bool
    cache_hit: bool = False


@dataclass
class EndpointBenchmark:
    """Benchmark results for an endpoint"""
    endpoint: str
    method: str
    total_requests: int
    avg_response_time: float
    median_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    success_rate: float
    cache_hit_rate: float
    requests_per_second: float


class APIBenchmark:
    """Benchmark utility for API performance testing"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            headers={"X-API-Key": self.api_key},
            timeout=30.0
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def _single_request(self, method: str, endpoint: str, data: Dict | None = None) -> BenchmarkResult:
        """Execute a single request and measure performance"""
        start_time = time.time()

        try:
            url = f"{self.base_url}{endpoint}"

            if method.upper() == "GET":
                response = await self.client.get(url)
            else:
                response = await self.client.post(url, json=data)

            end_time = time.time()
            response_time = end_time - start_time

            # Check for cache hit
            cache_hit = response.headers.get("X-Cache") == "HIT"

            return BenchmarkResult(
                endpoint=endpoint,
                method=method,
                response_time=response_time,
                status_code=response.status_code,
                success=response.status_code == 200,
                cache_hit=cache_hit
            )

        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time

            return BenchmarkResult(
                endpoint=endpoint,
                method=method,
                response_time=response_time,
                status_code=0,
                success=False,
                cache_hit=False
            )

    async def benchmark_endpoint(self, method: str, endpoint: str,
                                num_requests: int = 50, data: Dict | None = None) -> EndpointBenchmark:
        """Benchmark a specific endpoint"""
        print(f"Benchmarking {method} {endpoint} ({num_requests} requests)...")

        results = []

        # Warm up request
        await self._single_request(method, endpoint, data)

        # Benchmark requests
        start_time = time.time()
        for i in range(num_requests):
            result = await self._single_request(method, endpoint, data)
            results.append(result)

            # Small delay to avoid overwhelming the server
            if i % 10 == 0:
                await asyncio.sleep(0.1)

        end_time = time.time()
        total_time = end_time - start_time

        # Calculate statistics
        response_times = [r.response_time for r in results]
        successful_requests = [r for r in results if r.success]
        cache_hits = [r for r in results if r.cache_hit]

        avg_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)

        if len(response_times) >= 20:
            p95_response_time = statistics.quantiles(response_times, n=20)[18]
        else:
            p95_response_time = max_response_time

        success_rate = (len(successful_requests) / num_requests) * 100
        cache_hit_rate = (len(cache_hits) / num_requests) * 100
        requests_per_second = num_requests / total_time

        return EndpointBenchmark(
            endpoint=endpoint,
            method=method,
            total_requests=num_requests,
            avg_response_time=avg_response_time,
            median_response_time=median_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            success_rate=success_rate,
            cache_hit_rate=cache_hit_rate,
            requests_per_second=requests_per_second
        )

    def get_sample_data(self) -> Dict[str, Any]:
        """Get sample test data"""
        return {
            "birth_chart": {
                "subject": {
                    "name": "Benchmark Test",
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
            "synastry": {
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

    async def run_comprehensive_benchmark(self, num_requests: int = 50) -> List[EndpointBenchmark]:
        """Run comprehensive benchmark on all endpoints"""
        sample_data = self.get_sample_data()

        test_cases = [
            ("GET", "/api/v4/health", None),
            ("GET", "/", None),
            ("POST", "/api/v4/birth-data", sample_data["birth_chart"]),
            ("POST", "/api/v4/birth-chart", sample_data["birth_chart"]),
            ("POST", "/api/v4/synastry-chart", sample_data["synastry"]),
            ("POST", "/api/v4/synastry-aspects-data", sample_data["synastry"]),
            ("POST", "/api/v4/relationship-score", sample_data["synastry"]),
            ("POST", "/api/v4/composite-chart", sample_data["synastry"]),
        ]

        results = []

        for method, endpoint, data in test_cases:
            try:
                benchmark = await self.benchmark_endpoint(method, endpoint, num_requests, data)
                results.append(benchmark)
            except Exception as e:
                print(f"Error benchmarking {method} {endpoint}: {e}")

        return results

    def print_benchmark_report(self, results: List[EndpointBenchmark]):
        """Print comprehensive benchmark report"""
        print("\n" + "="*100)
        print("API PERFORMANCE BENCHMARK REPORT")
        print("="*100)

        # Overall statistics
        all_response_times = []
        total_requests = 0
        total_successful = 0

        for result in results:
            all_response_times.extend([result.avg_response_time] * result.total_requests)
            total_requests += result.total_requests
            total_successful += int(result.total_requests * result.success_rate / 100)

        overall_avg = statistics.mean(all_response_times) if all_response_times else 0
        overall_success_rate = (total_successful / total_requests * 100) if total_requests > 0 else 0

        print(f"\nOverall Performance:")
        print(f"  Total Requests: {total_requests}")
        print(f"  Success Rate: {overall_success_rate:.1f}%")
        print(f"  Average Response Time: {overall_avg:.3f}s")

        # Detailed results
        print(f"\nDetailed Results:")
        print("-" * 100)
        print(f"{'Endpoint':<35} {'Method':<6} {'Avg(s)':<8} {'P95(s)':<8} {'RPS':<8} {'Success%':<9} {'Cache%':<8}")
        print("-" * 100)

        for result in results:
            print(f"{result.endpoint:<35} {result.method:<6} {result.avg_response_time:<8.3f} "
                  f"{result.p95_response_time:<8.3f} {result.requests_per_second:<8.1f} "
                  f"{result.success_rate:<9.1f} {result.cache_hit_rate:<8.1f}")

        # Performance analysis
        print(f"\nPerformance Analysis:")
        print("-" * 100)

        # Identify fastest and slowest endpoints
        sorted_by_speed = sorted(results, key=lambda x: x.avg_response_time)
        fastest = sorted_by_speed[0]
        slowest = sorted_by_speed[-1]

        print(f"🚀 Fastest endpoint: {fastest.endpoint} ({fastest.avg_response_time:.3f}s avg)")
        print(f"🐌 Slowest endpoint: {slowest.endpoint} ({slowest.avg_response_time:.3f}s avg)")

        # Cache performance
        cached_endpoints = [r for r in results if r.cache_hit_rate > 0]
        if cached_endpoints:
            avg_cache_rate = statistics.mean([r.cache_hit_rate for r in cached_endpoints])
            print(f"💾 Average cache hit rate: {avg_cache_rate:.1f}%")

        # Throughput analysis
        total_rps = sum(r.requests_per_second for r in results)
        print(f"⚡ Total throughput: {total_rps:.1f} requests/sec")

        # Performance recommendations
        print(f"\nRecommendations:")
        print("-" * 100)

        slow_endpoints = [r for r in results if r.avg_response_time > 1.0]
        if slow_endpoints:
            print("⚠️  Consider optimizing these slow endpoints (>1s):")
            for endpoint in slow_endpoints:
                print(f"   - {endpoint.endpoint}: {endpoint.avg_response_time:.3f}s")

        low_cache_endpoints = [r for r in results if r.cache_hit_rate < 10 and "chart" in r.endpoint]
        if low_cache_endpoints:
            print("💾 Consider improving caching for these endpoints:")
            for endpoint in low_cache_endpoints:
                print(f"   - {endpoint.endpoint}: {endpoint.cache_hit_rate:.1f}% cache hit rate")

        if not slow_endpoints:
            print("✅ All endpoints performing well!")

    def save_benchmark_results(self, results: List[EndpointBenchmark], filename: str):
        """Save benchmark results to JSON file"""
        data = {
            "timestamp": time.time(),
            "results": [asdict(result) for result in results]
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"📊 Benchmark results saved to {filename}")


async def main():
    """Main benchmark execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark the Astrologer API")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--api-key", required=True, help="API key for authentication")
    parser.add_argument("--requests", type=int, default=50, help="Requests per endpoint")
    parser.add_argument("--output", help="Output file for results (JSON)")

    args = parser.parse_args()

    async with APIBenchmark(args.url, args.api_key) as benchmark:
        print(f"Starting benchmark against {args.url}")
        print(f"Requests per endpoint: {args.requests}")
        print("-" * 50)

        results = await benchmark.run_comprehensive_benchmark(args.requests)
        benchmark.print_benchmark_report(results)

        if args.output:
            benchmark.save_benchmark_results(results, args.output)


if __name__ == "__main__":
    asyncio.run(main())