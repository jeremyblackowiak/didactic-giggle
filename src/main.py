import os
import sys
import argparse
from datetime import datetime
import logging
import requests
import yaml
from tld import get_tld

test_mode = True

class HealthCheck:
    def __init__(self, input_file, test_interval):
        self.input_file = input_file
        self.test_interval = test_interval
        self.endpoints = self.collect_endpoints()
        self.results = {}

    def validate_input(self, endpoint_config_item):
        # check format of input file
        print("Validating input...")
        if "name" not in endpoint_config_item:
            raise ValueError("Endpoint name is required")
        if "url" not in endpoint_config_item:
            raise ValueError("Endpoint URL is required")
        
    def get_domain(self, url):
        # extract domain from URL
        domain = get_tld(url, as_object=True).domain
        # TODO this should probably be separated out into another function. Not clear as is. 
        self.results.setdefault(domain, {"requests": 0, "UP": 0})
        
        return domain

    def collect_endpoints(self):
        print("Collecting endpoints...")
        try:
            with open(self.input_file, "r") as endpoints_file:
                # load yaml
                endpoints_yaml = yaml.safe_load(endpoints_file)

                # now need to parse it into something useful
                for endpoint_config_item in endpoints_yaml:
                    self.validate_input(endpoint_config_item)

                # endpoints_list = endpoints_yaml
                # print(endpoints_list)
                return endpoints_yaml

        except Exception as e:
            logging.error(f"error: {e}")
            sys.exit(1)



    def begin_health_check(self):
        print(f"OK I'm checking {self.endpoints}")

        for endpoint in self.endpoints:
            name = endpoint["name"]
            url = endpoint["url"]
            domain = self.get_domain(url)

            try:
                response = requests.get(url)
                latency = response.elapsed.total_seconds() * 1000
                # TODO all 2xx codes
                if (response.status_code == 200) and (latency < 500):
                    self.results[domain]["requests"] += 1
                    self.results[domain]["UP"] += 1
                else:
                    self.results[domain]["requests"] += 1
                    self.results[domain]["UP"] += 1

            # TODO couldn't an error in request be considered a "DOWN" in some cases? Need to consider. 
            except Exception as e:
                print(f"Error: {e}")

        # print(f"Results: {self.results}")

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