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
    # Basically, a user attempt to exit will not exit immediately, instead just updates a flag to trigger the discontinuation of the check loop.
    print("Canceling after current interval run completes...")
    global should_exit
    should_exit = True

@contextlib.contextmanager
def monitor_session():
    """Context manager for clean setup and teardown of monitoring. New feature for me."""
    # Capture exit signals and route to handler.
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

        # TODO The exercise was generous in not asking for a lot of validation, but it would be good to add more.
        if "name" not in endpoint_config_item:
            raise ValueError("Endpoint name is required")
        if "url" not in endpoint_config_item:
            raise ValueError("Endpoint URL is required")

    def get_domain(self, url):
        """
        Extract domain from URL.
        """
        
        # TODO The exercise's example output includes the subdomain, but the prompt only asks for the domain. Need to make a decision here. 
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
        
        # For each domain we saw, calculate the percentage of successful requests.
        for domain in self.results:
            total_requests = self.results[domain]["requests"]
            up_requests = self.results[domain]["UP"]
            percentage = (up_requests / total_requests) * 100
            # Exercise asked for this specific output format. 
            print(f"{domain} has {round(percentage)}% availability percentage")

    def begin_schedule(self):
        """
        Start the health check and run every configured interval until stopped.
        """
        
        logging.info(f"Starting health checks every {self.test_interval} seconds")

        # Schedule library is new to me, very cool. Handles the queueing/timing. 
        schedule.every(self.test_interval).seconds.do(self.begin_health_check)

        # Runs the "schedule" until my should_exit condition is met. 
        # Right, should_exit is only set to True on SIGINT or SIGTERM, so it will run indefinitely.
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

        # For each endpoint, grab the relevant field values and make an HTTP request.
        for endpoint in self.endpoints:
            url = endpoint["url"]
            method = endpoint.get("method", "GET")
            headers = endpoint.get("headers")
            body = endpoint.get("body")
            # Grab the domain from the URL, since we're tracking availability by domain.
            domain = self.get_domain(url)

            try:
                # Perform the request, capture response for analysis.
                response = requests.request(method, url, headers=headers, data=body)
                # The latency property comes as a timedelta object, so I have to convert it to milliseconds.
                latency = response.elapsed.total_seconds() * 1000

                # If it's a 2xx and latency under 500ms, we call that a success. 
                if (200 <= response.status_code <= 299) and (latency < 500):
                    # We're counting total requests so we can do the percentage math later.
                    self.results[domain]["requests"] += 1
                    self.results[domain]["UP"] += 1
                    logging.debug(f"UP: {url} - {response.status_code} - {latency}ms")
                    logging.debug(f"Request sent: {response.request}")
                    logging.debug(f"Response received: {response.json}")
                    logging.debug(response.json)
                # Anything else is a failure, an implied "DOWN".
                else:
                    # Only bump the total requests, no need to track a "DOWN" count.
                    self.results[domain]["requests"] += 1
                    logging.debug(f"DOWN: {url} - {response.status_code} - {latency}ms")
                    logging.debug(f"Request sent: {response.request}")
                    logging.debug(f"Response received: {response.json}")
                    logging.debug(response.json)

            # TODO Registering any exception as a "DOWN" request means absolute faith that my code isn't the failure point. Should be reworked. 
            except Exception as e:
                self.results[domain]["requests"] += 1
                logging.error(f"ERROR: {url} - {str(e)}")

        logging.info(f"Completed health check cycle {self.run_count + 1}")
        self.run_count += 1

def parse_args():
    """
    Parse command line arguments.
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

    # Use context manager for setup/cleanup. New to me! Very cool. 
    with monitor_session():
        
        # Init the health check class, which parses the YAML file input and does further setup.
        health_check = HealthCheck(args.endpoints, args.test_interval)
        # The beating heart (pun intended) of the script.
        health_check.begin_schedule()

if __name__ == "__main__":
    sys.exit(main())
