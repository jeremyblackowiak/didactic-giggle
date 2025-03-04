import os
import sys
import argparse
import time
import logging
import requests


class HealthCheck:
    def __init__(self, config_file):
        self.config_file = config_file
        self.endpoints = self.validate_input()

    def validate_input(self):
        print("Validating input...")
        print(f"Config file: {self.config_file}")

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
    # parser.add_argument(
    #     "--test-interval",
    #     type=int,
    #     help="How often the health check should run in seconds.",
    #     default=15,
    # )

    args = parser.parse_args()

    # Create the health check object
    health_check = HealthCheck(args.endpoints)
    health_check.begin_health_check()


if __name__ == "__main__":
    sys.exit(main())