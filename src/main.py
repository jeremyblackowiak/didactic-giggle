import sys
import signal
import argparse
from datetime import datetime
import logging
import requests
import yaml
from urllib.parse import urlparse
import schedule


# TODO improve error handling - still need more cleanup, logging too.
# TODO comments for functions
# TODO test
# TODO cool ASCII art on start/finish

test_mode = True

# TODO use this to toggle between the exercise's required output and one I think is prettier
info_logs = False

should_exit = False


def exit_handler(sig, frame):
    print("Canceling after interval run...")
    global should_exit
    should_exit = True


class HealthCheck:
    def __init__(self, input_file, test_interval):
        self.input_file = input_file
        self.test_interval = test_interval
        self.endpoints = self.collect_endpoints()
        self.results = {}
        self.run_count = 0

    def validate_input(self, endpoint_config_item):
        if "name" not in endpoint_config_item:
            raise ValueError("Endpoint name is required")
        if "url" not in endpoint_config_item:
            raise ValueError("Endpoint URL is required")

    def get_domain(self, url):
        # extract domain from URL
        # domain_object = get_tld(url, as_object=True)
        # domain = domain_object.subdomain + "." + domain_object.fld

        domain_object = urlparse(url)
        domain = domain_object.netloc
        # TODO this should probably be separated out into another function. Not clear that this function is also creating the dict entry.
        self.results.setdefault(domain, {"requests": 0, "UP": 0})

        return domain

    def collect_endpoints(self):
        logging.info(f"Collecting endpoints from {self.input_file}")
        try:
            with open(self.input_file, "r") as endpoints_file:
                # load yaml
                endpoints_yaml = yaml.safe_load(endpoints_file)

                # now need to parse it into something useful
                for endpoint_config_item in endpoints_yaml:
                    self.validate_input(endpoint_config_item)

                return endpoints_yaml

        except Exception as e:
            logging.error(f"error: {e}")
            sys.exit(1)

    def prepare_results(self):
        for domain in self.results:
            total_requests = self.results[domain]["requests"]
            up_requests = self.results[domain]["UP"]
            percentage = (up_requests / total_requests) * 100
            print(f"{domain} has {round(percentage)}% availability percentage")

    def begin_schedule(self):

        schedule.every(self.test_interval).seconds.do(self.begin_health_check)

        while not should_exit:
            try:
                schedule.run_pending()
            except Exception as e:
                raise Exception(f"{e}")

        print("Here's what you ordered")
        self.prepare_results()
        print(self.run_count)

    def begin_health_check(self):
        logging.info(f"Starting health check run {(self.run_count + 1)}")

        for endpoint in self.endpoints:
            url = endpoint["url"]
            method = endpoint.get("method", "GET")
            headers = endpoint.get("headers")
            body = endpoint.get("body")
            domain = self.get_domain(url)

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

            # TODO couldn't an error in request be considered a "DOWN" in some cases? Need to consider.

        self.run_count += 1


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
    parser.add_argument(
        "--info-logs",
        type=bool,
        help="More output for the curious.",
        default=False,
    )

    args = parser.parse_args()

    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

    # Logging setup borrowed from Google
    logger = logging.getLogger(__name__)
    ch = logging.StreamHandler()

    if args.info_logs:
        print("INFO LOGS ENABLED")
        logging.basicConfig(level=logging.INFO)
        ch.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Create the health check object
    health_check = HealthCheck(args.endpoints, args.test_interval)
    health_check.begin_schedule()


if __name__ == "__main__":
    sys.exit(main())
