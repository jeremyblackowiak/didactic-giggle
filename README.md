# # didactic-giggle

Welcome to `didactic-giggle`! This project is is a take home exercise with a goal of creating an HTTP endpoint "health checker," with various conditions included. Right now this is just my boilerplate README stuff, plus what I think I'll include. 

scratch pad
- python
- poetry? 
- library for parsing yaml
- input validation for various fields?
    - prompt points out "you may assume" it's valid. don't worry for now. 
    - assume GET if no method
- tests / linting

- flow
    - parse yaml into objects, endpoints / domains classes?
    - every 15 seconds, perform requests against each endpoint
    - Process responses into 2 categories, UP or DOWN.
        - UP is 
            - 2xx
            - latency < 500ms 
        - store in what data structure? 
            - elaboration of the "internal program state" 
    - exit is manual
    - results calculation 
        - percentage of UP requests per DOMAIN, not endpoint
        - results need to be collated per DOMAIN. 
    - log results to console after every test cycle, 15 seconds
        - follow prompts template for the log messages
        - log test cycle time start/end?
        - round floats to whole percentage

- what should timeout be? 
- stretch goal -- on exit, print the combined results? might hit a memory issue
- probably put in docker container 


## Overview

### Tools Used

- **ASDF:** Toolchain installation management.


### Things I'm Still Figuring Out


### What I'd Do With More Time


## Prerequisites

Before you begin, ensure you have the following:

- **Local Machine:** A *nix machine with Docker for Desktop or Rancher installed, if running locally.

- **ASDF:** Installed. Follow the instructions on the [ASDF GitHub page](https://github.com/asdf-vm/asdf) to install it.


## First Time Setup, Metadata and Infrastructure

### Basic Setup

1. **Clone the repository**

   Use your preferred method to clone the repository to your local machine.

2. Run `asdf install`.



### Local App Deployment


