# Fractal: Text-to-Video Generation Grid for Edge-Node Inference

Fractal, taking inspiration from Manifold Labs' Deterministic Verification Network, is utilizing deterministic verification to create a grid of decentralized nodes to perform inference for video generation. By incentivizing users to host text-to-video models, this subnet allows Fractal to develop a mechanism that optimizes how end-user inference requests are handled to minimize latency. Additionally, the subnet is incredibly gamification-resistant, as a random seed is generated for each inference request, and if the Verifier and Prover seeds do not match, the Prover will be penalized.

Currently supporting python>=3.9,<3.11.

1. [Compute Requirements](#compute-requirements)
1. [Installation](#installation)
    - [Install Redis](#install-redis)
    - [Install PM2](#install-pm2)
    - [Install Fractal](#install-fractal)
1. [Why use a Homogeneous Inference Grid?](#why-use-a-homogeneous-inference-grid)
   - [Role of a Prover](#role-of-a-prover)
   - [Role of a Verifier](#role-of-a-verifier)
1. [Features of Fractal](#features-of-fractal)
    - [Challenge Request](#challenge-request)
    - [Inference Request](#inference-request)
1. [How to Run Fractal](#how-to-run-fractal)
    - [Run a Prover](#run-a-prover)
    - [Run a Verifier](#run-a-verifier)
1. [Reward System](#reward-system)
    - [Tier System](#tier-system)
    - [Promotion/Relegation](#promotionrelegation)
1. [How to Contribute](#how-to-contribute)


# Compute Requirements
The following table shows the VRAM, Storage, RAM, and CPU minimum requirements for running a verifier or prover.


## Required: RTX 3090 -- for verification purposes, if anything other than an RTX 3090 is used, the node will be scored poorly.
| Role     | GPU        | Storage | RAM  | CPU     |
|----------|------------|---------|------|---------|
| Prover   | 24GB  3090 | 32GB    | 8GB  | 8 Cores |
| Verifier | 24GB  3090 | 64GB    | 16GB | 8 Cores |
*NOTE: ensure provers have a port open for TCP (on runpod, this will be TCP not HTTP)

# Installation

## Overview
In order to run Fractal, you need to install PM2 and the Fractal package. The following instructions apply only to Ubuntu OSes. For your specific OS, please refer to the official documentation.


### Install Redis and server packages

```
sudo apt-get update && sudo apt-get install redis-server
sudo apt-get install libgl1-mesa-glx
sudo apt-get install libglib2.0-0
```

### Install pm2

To install pm2, download nvm, node, and finally pm2

#### Download NVM
To install or update nvm, you should run the install script. To do that, you may either download and run the script manually, or use the following cURL or Wget command:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```

#### Install Node

```bash
nvm install 18 && nvm use 18
```

#### Install PM2

```bash
npm install pm2@latest -g
```
You have now installed PM2.


### Install Fractal

#### Clone the repository

```bash
git clone https://github.com/fractal-net/fractal.git
cd fractal
```

#### Install dependencies

```bash
pip install -e .
pip install -r requirements.txt
```

You have now installed Fractal. You can now run a prover or verifier.


# Why use a Homogeneous Inference Grid?
Inspiration for Homogeneous Inference Grids came from Manifold Labs' TARGON and can be read about here: (https://github.com/manifold-inc/fractal/tree/main). Fractal is adopting the framework of Provers and Verifiers and implementing text-to-video generation. Redundant verification networks are gamification-resistant-- a critical start to improving the resiliency of the Bittensor network. By solving gamification, these networks allow for optimizations to be built around real compute-- starting with edge-node inference. Fractal is working to develop and implement routing mechanisms that optimize inference response speeds. This will be critical to gaining end-user adoption in a scalable way on the Bittensor network. In a world where hundreds of apps are being built on Bittensor, and hundreds of thousands (or millions) of user requests are being sent to subnets, the network must minimize response times. 

## Role of a Prover
A prover is a node that is responsible for generating a output from a query, private input, and a deterministic sampling params. 

## Role of a Verifier
A verifier is a node that is responsible for verifying a prover's output. The verifier will send a request to a prover with a query, private input, and deterministic sampling params. The miner will then send back a response with the output. The verifier will then compare the output to the ground truth output. If the outputs are equal, then the prover has completed the challenge.

# Features of Fractal

## Challenge Request
A challenge request is a request sent by a verifier to a prover. The challenge request contains a query, private input, and deterministic sampling params. The prover will then generate an output from the query, private input, and deterministic sampling params. The prover will then send the output back to the verifier.

## Inference Request (IN PROGRESS)
An inference request is a request sent by a verifier to a prover. The inference request contains a query, private input, and inference sampling params. The prover will then generate an output from the query, private input, and deterministic sampling params. The prover will then stream the output back to the verifier.
> *CAVEAT:* Every Interval (360 blocks) there will be a random amount of inference samples by the verifier. The verifier will then compare the outputs to the ground truth outputs. The cosine similarity of the outputs will be used to determine the reward for the prover. Failing to do an inference request will result in a 5x penalty.


# How to Run Fractal

## Run a Prover

### Run with PM2


```bash
pm2 start ecosystem.config.js
```

Inside ecosystem.config.js you need to replace all entries like <YOUR_WALLET_HERE> with the correspoinding values. 

<SERVER_PORT_HERE> - replace this with the port your model server is running on (you can configure this in model/server.py)

<YOUR_INTERNAL_PORT> - replace this with the internal port your server is running on 

<YOUR_EXTERNAL_PORT> - replace this with the external port your server is running on (this entire flag is not needed if it's the same as internal port-- but with runpod it is often different)

<YOUR_WALLET_NAME> - replace this with the name of your coldkey

<YOUR_WALLET_HOTKEY> - replace this with the name of your hotkey

### Options
The add_prover_args function in the fractal/utils/config.py file is used to add command-line arguments specific to the prover. Here are the options it provides:

1. --neuron.name: This is a string argument that specifies the name of the neuron. The default value is 'prover'.

2. --blacklist.force_verifier_permit: This is a boolean argument that, if set, forces incoming requests to have a permit. The default value is False.

3. --blacklist.allow_non_registered: This is a boolean argument that, if set, allows provers to accept queries from non-registered entities. This is considered dangerous and its default value is False.

4. --neuron.model_endpoint: This is a string argument that specifies the endpoint to use for the server that hosts your model. The default value is "http://0.0.0.0:5005".



## Run a Verifier

### Run with PM2

#### Generate Redis DB Password:

```
cd /fractal/
./scripts/generate_redis_password.sh
```

#### Copy the Redis Password and add it to Redis conf:

```
vim /etc/redis/redis.conf
```

You need to uncomment out the line that begins with "requirepass" and set your password

```
requirepass <YOUR_PASSWORD_HERE>
```

If you are running on runpod, you may also need to set the logfile line to a file that actually exists on your machine. 

```
logfile <PATH_TO_YOUR_LOGFILE>
```

Run the following command to start the verifier with PM2:

```bash
pm2 start ecosystem.config.js
```


<SERVER_PORT_HERE> - replace this with the port your model server is running on (you can configure this in model/server.py)

<YOUR_PASSWORD_HERE> - replace this with the password you generated (it must be the same as the one in /etc/redis/redis.conf)

<YOUR_INTERNAL_PORT> - replace this with the internal port your server is running on 

<YOUR_EXTERNAL_PORT> - replace this with the external port your server is running on (this entire flag is not needed if it's the same as internal port)

<YOUR_WALLET_NAME> - replace this with the name of your coldkey

<YOUR_WALLET_HOTKEY> - replace this with the name of your hotkey

### Options
The add_verifier_args function in the fractal/utils/config.py file is used to add command-line arguments specific to the verifier. Here are the options it provides:

1. --neuron.sample_size: The number of provers to query in a single step. Default is 3. (Can cause problems if this is larger than the number of provers on the network)

2. --neuron.disable_set_weights: A flag that disables setting weights. Default is False.

3. --neuron.moving_average_alpha: Moving average alpha parameter, how much to add of the new observation. Default is 0.05.

4. --neuron.axon_off or --axon_off: A flag to not attempt to serve an Axon. Default is False.

5. --neuron.vpermit_tao_limit: The maximum number of TAO allowed to query a verifier with a vpermit. Default is 4096.

6. --neuron.model_endpoint: The endpoint to use for the server that hosts your model. Default is "http://0.0.0.0:5005".

7. --database.host: The path to write debug logs to. Default is "127.0.0.1".

8. --database.port: The path to write debug logs to. Default is 6379.

9. --database.index: The path to write debug logs to. Default is 1.

10. --database.password: The password to use for the redis database. Default is None.

11. --neuron.compute_stats_interval: The interval at which to compute statistics. Default is 360.

These options can be used to customize the behavior of the verifier when it is run.


# Reward System
Inspired by [FileTAO](https://github.com/ifrit98/storage-subnet)'s reputation system, the reward system is based on the complete correct answer being responded consistently over time. If a ground truth hash and the prover output hash are equal, then the reward is 1. Performing these challenges and inference requests over time will result in a multiplication of your reward based off the tier.

## Tier System
The tier system classifies miners into five distinct categories, each with specific requirements and request limits. These tiers are designed to reward miners based on their performance, reliability, and the total volume of requests they can fulfill.


**1.) Challenger Tier** 
- **Request Success Rate:** 99.9% (1/1000 chance of failure)
- **Validation Success Rate:** 99.9% (1/1000 chance of failure)
**- Minimum Successful Requests Required:** 2,000,000 Required
- **Reward Factor:** 1.0 (100% rewards)
- **Requests Limit (per interval):** 100,000 per interval

**2.) Grandmaster Tier** 
- **Request Success Rate:** 99.9% (1/1000 chance of failure)
- **Validation Success Rate:** 99.9% (1/1000 chance of failure)
**- Minimum Successful Requests Required:** 700,000 Required
- **Reward Factor:** 0.85 (85% rewards)
- **Requests Limit (per interval):** 25,000 per interval


**3.) Gold Tier** 
- **Request Success Rate:** 94.9% 
- **Validation Success Rate:** 94.9% 
**- Minimum Successful Requests Required:** 14,000 Required
- **Reward Factor:** 0.72 (70% rewards)
- **Requests Limit (per interval):** 14,000 per interval


**4.) Silver Tier** 
- **Request Success Rate:** 94.9%
- **Validation Success Rate:** 94.9% 
**- Minimum Successful Requests Required:** 3,500 Required
- **Reward Factor:** 0.55 (95% rewards)
- **Requests Limit (per interval):** 3,500 per interval

5.**) Bronze Tier** 
- **Request Success Rate:** Not defined
- **Validation Success Rate:** Not defined
**- Minimum Successful Requests Required:** Not defined
- **Reward Factor:** 0.45 (33% rewards)
- **Requests Limit (per interval):** 500 per interval


## Promotion/Relegation
Miners will be promoted or relegated based on their performance over the last 360 blocks. The promotion/relegation computation will be done every 360 blocks. In order to be promoted to a tier, you must satisfy the tier success rate requirements and the minimum successful requests required. In order to be relegated to a tier, you must fail to satisfy the tier success rate requirements, leading to a demotion to the lower tier. 

If you experience downtime as a challenger UID, you will be demoted down, however you will not have to satisfy the minimum successful requests required. You will be instantly promoted back to the tier if you satisfy the tier success rate requirements.

## Periodic Statistics Rollover
Statistics for inference_attempts/attempts, challenge_attempts/successes are reset every interval, while the total_successes are carried over for accurate tier computation. This "sliding window" of the previous 360 blocks of N successes vs M attempts effectively resets the N / Mratio. This facilitates a less punishing tier calculation for early failures that then have to be "outpaced", while simultaneously discouraging grandfathering in of older miners who were able to succeed early and cement their status in a higher tier. The net effect is greater mobility across the tiers, keeping the network competitive while incentivizing reliability and consistency.


# How to Contribute

## Code Review
Project maintainers reserve the right to weigh the opinions of peer reviewers using common sense judgement and may also weigh based on merit. Reviewers that have demonstrated a deeper commitment and understanding of the project over time or who have clear domain expertise may naturally have more weight, as one would expect in all walks of life.

Where a patch set affects consensus-critical code, the bar will be much higher in terms of discussion and peer review requirements, keeping in mind that mistakes could be very costly to the wider community. This includes refactoring of consensus-critical code.

Where a patch set proposes to change the TARGON subnet, it must have been discussed extensively on the discord server and other channels, be accompanied by a widely discussed BIP and have a generally widely perceived technical consensus of being a worthwhile change based on the judgement of the maintainers.

## Finding Reviewers
As most reviewers are themselves developers with their own projects, the review process can be quite lengthy, and some amount of patience is required. If you find that you've been waiting for a pull request to be given attention for several months, there may be a number of reasons for this, some of which you can do something about:
