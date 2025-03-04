import os
import sys
import argparse
import time
import logging
import requests
import yaml

class HealthCheck:
    def __init__(self, input_file, test_interval):
        self.input_file = input_file
        self.test_interval = test_interval
        self.endpoints = self.collect_endpoints()

    def validate_input(self):
        print("Validating input...")
        print(f"Config file: {self.input_file}")
        print(f"Test interval: {self.test_interval}")

    def collect_endpoints(self):
        print("Collecting endpoints...")
        try:
            with open(self.input_file, "r") as endpoints_file:
                # load yaml
                endpoints_yaml = yaml.safe_load(endpoints_file)
                print(endpoints_yaml)
        except Exception as e:
            logging.error(f"error: {e}")
            sys.exit(1)


    def begin_health_check(self):
        print("OK I'm checking")


def main():
    parser = argparse.ArgumentParser(description="Process my inputs!")
    parser.add_argument(
        "--endpoints",
        type=str,
        required=True,
        # TODO print dynnamic path for sample_input.yaml?
        help=f"Path to YAML file with endpoints. See sample_input.yaml for format details.",
    )
    parser.add_argument(
        "--test-interval",
        type=int,
        help="How often the health check should run in seconds.",
        default=15,
    )

    args = parser.parse_args()

    # Create the health check object
    health_check = HealthCheck(args.endpoints, args.test_interval)
    health_check.begin_health_check()


if __name__ == "__main__":
    sys.exit(main())