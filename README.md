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

### What I'd Do With More Time

- **TODO Items:** Tackle the remaining #TODO comments in main.py.
- **Improved Logging:** Color and prettify output. Enhancing logging to include more detailed information.
- **Error Handling:** Improving error handling, especially around the http call block.
- **Orchestrate with NX:** Use NX.dev to orchestrate the operations of the repo, set up for a single command.
- **Docker Support:** Create a Dockerfile to run the script in a container.
- **Enhanced Validation:** Add more validation for the input YAML configuration file.
- **Configuration Options:** Allow more configuration options for the health checks.

## Prerequisites

Before you begin, ensure you have the following:

- **Local Machine:** A *nix machine or Windows with WSL. Anything that can run ASDF. 
- **ASDF:** Installed. Follow the instructions on the [ASDF GitHub page](https://github.com/asdf-vm/asdf) to install it. Using homebrew, you can run `brew install asdf`. 

## How To Use

### Basic Setup

1. **Clone the repository**

   Use your preferred method to clone the repository to your local machine.

2. Run `asdf install`.

3. Run `poetry install`.

4. Run the script with the following command. Exit with `Ctrl+C` to see results.

   ```bash
   poetry run python src/main.py --endpoints "src/sample_input.yaml"

5. (Optional) Run the script with custom input arguments.

    - Update the `src/sample_input.yaml` file with your endpoints to monitor, or create your own file. Note that each entry will need to include both "name" and "url" field values, like the template. 
    - Use the `--test-interval`, `--info-logs` flags to customize your command. See table below for details.

    ```bash
    poetry run python src/main.py --endpoints "/home/user/projects/didactic-giggle/src/sample_input.yaml" --test-interval 5 --info-logs

### Input Argument Options

| Argument         | Type   | Description                                                                 | Default Value               |
|------------------|--------|-----------------------------------------------------------------------------|-----------------------------|
| `--endpoints`    | `str`  | Path to YAML file with endpoints to monitor                                  | Required                    |
| `--test-interval`| `int`  | Interval between health checks in seconds                                    | `15`     |
| `--info-logs`    | `bool` | Enable output of info logs during program run                                         | `False`                     |

### Contributing

#### Commands

- `poetry run black .` Lint the Python files.
- `poetry run pytest` Run the tests in the tests/ directory.