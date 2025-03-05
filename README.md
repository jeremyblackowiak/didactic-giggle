# didactic-giggle

Welcome to `didactic-giggle`! This project is a take-home exercise with a goal of creating an HTTP endpoint "health checker," with various conditions included.

## Overview

### Tools Used

- **ASDF:** Toolchain installation management.
- **Poetry:** Package and virtual environment management.
- **Python:** Everyone's best friend.
- **Python Libraries:** 
    - **Requests:** For making HTTP requests.
    - **PyYAML:** For parsing YAML configuration files.
    - **Schedule:** For scheduling health checks.
    - **Logbook:** For logging.
    - **Pytest** For unit tests. 

### Things I'm Still Figuring Out

- **Edge Cases:** Handling various edge cases such as bad URLs, slow endpoints, and down endpoints.
- **Improved Logging:** Enhancing logging to include more detailed information.
- **Error Handling:** Improving error handling to ensure the script is robust.

### What I'd Do With More Time

- **Docker Support:** Create a Dockerfile to run the script in a container.
- **Enhanced Validation:** Add more validation for the input YAML configuration file.
- **Configuration Options:** Allow more configuration options for the health checks.

## Prerequisites

Before you begin, ensure you have the following:

- **Local Machine:** A *nix machine with Docker for Desktop or Rancher installed, if running locally.
- **ASDF:** Installed. Follow the instructions on the [ASDF GitHub page](https://github.com/asdf-vm/asdf) to install it. Using homebrew, you can run `brew install asdf`. 

## First Time Setup, Metadata and Infrastructure

### Basic Setup

1. **Clone the repository**

   Use your preferred method to clone the repository to your local machine.

2. Run `asdf install`.

3. Run `poetry install`.

4. Update the `src/sample_input.yaml` file with your endpoints to monitor.

5. Run the script with the following command:

   ```bash
   poetry run python src/main.py --endpoints src/sample_input.yaml