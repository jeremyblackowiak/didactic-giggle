#!/usr/bin/env python3
"""
HTTP Heartbeat Monitor

A tool for monitoring the health of HTTP endpoints defined in a YAML file.
Performs health checks at regular intervals and tracks availability percentages by domain.
"""
import sys
import signal
import argparse
from datetime import datetime
import logging
import requests
import yaml
from urllib.parse import urlparse
import schedule
import contextlib
from collections import defaultdict
from typing import Dict, Optional, Any, List
from config import DEFAULT_TEST_INTERVAL, setup_logging


# TODO improve error handling - still need more cleanup, logging too.
# TODO comments for functions
# TODO use config.py? 
# TODO split some stuff out into separate files, potentially
# TODO test
# TODO run via Docker container
# TODO cool ASCII art on start/finish
# TODO edge cases. What if the URL is bad? What if the endpoint is down? What if the endpoint is slow? What if it has 0 entries?

test_mode = True

# TODO use this to toggle between the exercise's required output and one I think is prettier
info_logs = False

should_exit = False


def exit_handler(sig, frame):
    """Handle exit signals (SIGINT, SIGTERM) gracefully."""
    print("Canceling after current interval run completes...")
    global should_exit
    should_exit = True

@contextlib.contextmanager
def monitor_session():
    """Context manager for clean setup and teardown of monitoring. New feature for me."""
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    try:
        print_banner()
        yield
    finally:
        print("Monitoring session ended")

def print_banner():
    """Displays a welcome banner for the script."""
    banner = """
╔═══════════════════════════════════════════════════╗
║                                                   ║
║       HTTP Endpoint Health Monitor v1.0           ║
║       Press Ctrl+C to exit                        ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
    """
    print(banner)

class HealthCheck:
    """
    Monitors health of HTTP endpoints and tracks their availability.
    """

    def __init__(self, input_file: str, test_interval: int):
        """
        Init the health check monitor.
        
        Args:
            input_file: Path to YAML configuration file with endpoints
            test_interval: Interval between health checks in seconds
        """
        self.input_file = input_file
        self.test_interval = test_interval
        self.endpoints = self.collect_endpoints()
        self.results = defaultdict(lambda: {"requests": 0, "UP": 0})
        self.run_count = 0

    def validate_input(self, endpoint_config_item):
        """
        Validate required fields are present in the endpoint configuration.
        """

        if "name" not in endpoint_config_item:
            raise ValueError("Endpoint name is required")
        if "url" not in endpoint_config_item:
            raise ValueError("Endpoint URL is required")

    def get_domain(self, url):
        """
        Extract domain from URL.
        """
        domain_object = urlparse(url)
        return domain_object.netloc

    def collect_endpoints(self):
        """
        Load and validate endpoint configurations from YAML file.
        """
        logging.info(f"Collecting endpoints from {self.input_file}")
        try:
            with open(self.input_file, "r") as endpoints_file:
                # Load the YAML file.
                endpoints_object = yaml.safe_load(endpoints_file)

                # Check for required fields.
                for endpoint_config_item in endpoints_object:
                    self.validate_input(endpoint_config_item)

                domains = set(self.get_domain(item["url"]) for item in endpoints_object)
                logging.info(f"Loaded {len(endpoints_object)} endpoints across {len(domains)} domains")
                
                return endpoints_object

        except Exception as e:
            logging.error(f"Error loading YAML file: {e}")
            sys.exit(1)

    def prepare_results(self):
        """
        Calculate and display availability percentages for all domains on exit.
        """
        for domain in self.results:
            total_requests = self.results[domain]["requests"]
            up_requests = self.results[domain]["UP"]
            percentage = (up_requests / total_requests) * 100
            print(f"{domain} has {round(percentage)}% availability percentage")

    def begin_schedule(self):
        """
        Start the health check and run every configured interval until stopped.
        """
        
        logging.info(f"Starting health checks every {self.test_interval} seconds")

        # Schedule library is new to me, very cool. Handles the queueing/timing. 
        schedule.every(self.test_interval).seconds.do(self.begin_health_check)

        # Runs the "schedule" until my should_exit condition is met. 
        while not should_exit:
            try:
                schedule.run_pending()
            except Exception as e:
                raise Exception(f"{e}")

        # Prepare results and print to terminal.
        self.prepare_results()
        logging.info(f"Completed {self.run_count} health check cycles")

    def begin_health_check(self):
        """
        Perform one cycle of health checks on all endpoints.
        """
        logging.info(f"Starting health check run {(self.run_count + 1)}")

        for endpoint in self.endpoints:
            url = endpoint["url"]
            method = endpoint.get("method", "GET")
            headers = endpoint.get("headers")
            body = endpoint.get("body")
            domain = self.get_domain(url)

            try:
                response = requests.request(method, url, headers=headers, data=body)
                latency = response.elapsed.total_seconds() * 1000

                if (200 <= response.status_code <= 299) and (latency < 500):
                    self.results[domain]["requests"] += 1
                    self.results[domain]["UP"] += 1
                else:
                    self.results[domain]["requests"] += 1
                    logging.warning(
                        f"DOWN because {url} returned {response.status_code} with latency {latency}ms"
                    )

            # TODO I feel like this could fail in some kind of way that I might not want to record as a request. 
            except Exception as e:
                self.results[domain]["requests"] += 1
                logging.error(f"ERROR: {url} - {str(e)}")

        logging.info(f"Completed health check cycle {self.run_count + 1}")
        self.run_count += 1

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="HTTP Endpoint Health Monitor")
    parser.add_argument(
        "--endpoints",
        type=str,
        required=True,
        help="Path to YAML file with endpoints to monitor",
    )
    parser.add_argument(
        "--test-interval",
        type=int,
        help=f"Interval between health checks in seconds (default: {DEFAULT_TEST_INTERVAL})",
        default=DEFAULT_TEST_INTERVAL,
    )
    parser.add_argument(
        "--info-logs",
        action="store_true",
        help="Enable verbose informational logging",
        default=False,
    )
    
    return parser.parse_args()

def main():
    """Main entry point for the endpoint health monitor."""
    
    # Parse command line arguments
    args = parse_args()

    # Setup logging
    setup_logging(args.info_logs)

    with monitor_session():
        # Create and run health check monitor
        health_check = HealthCheck(args.endpoints, args.test_interval)
        health_check.begin_schedule()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
