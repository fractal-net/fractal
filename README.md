# Fractal: Text-to-Video Generation Grid for Edge-Node Inference

Fractal, taking inspiration from Manifold Labs' Deterministic Verification Network, is utilizing deterministic verification to create a grid of decentralized nodes to perform inference for video generation. By incentivizing users to host text-to-image models, this subnet allows Fractal to develop a mechanism that optimizes how end-user inference requests are handled to minimize latency. Additionally, the subnet is incredibly gamification-resistant, as a random seed is generated for each inference request, and if the Verifier and Prover seeds do not match, the Prover will be penalized.


Currently supporting python>=3.9,<3.11.

> Note: The storage subnet is in an alpha stage and is subject to rapid development.


# Table of Contents
1. [Compute Requirements](#compute-requirements)
1. [Roadmap](#roadmap)
1. [Installation](#installation)
    - [Install Docker](#install-docker)
    - [Install PM2](#install-pm2)
    - [Install TARGON](#install-targon)
1. [What is a Redundant Deterministic Verification Network?](#what-is-a-redundant-deterministic-verification-network)
   - [Role of a Prover](#role-of-a-prover)
   - [Role of a Verifier](#role-of-a-verifier)
1. [Features of TARGON](#features-of-targon)
    - [Challenge Request](#challenge-request)
    - [Inference Request (IN PROGRESS) ](#inference-request-(IN-PROGRESS))
1. [How to Run TARGON](#how-to-run-targon)
    - [Run a Prover](#run-a-prover)
    - [Run a Verifier](#run-a-verifier)
1. [Reward System](#reward-system)
    - [Tier System](#tier-system)
    - [Promotion/Relegation](#promotion/relegation)
1. [How to Contribute](#how-to-contribute)


# Compute Requirements
The following table shows the VRAM, Storage, RAM, and CPU minimum requirements for running a verifier or prover.


# Required: RTX 3090
| Role | VRAM | Storage | RAM | CPU |
| Prover   | 24GB | 32GB | 8GB | 8 Cores  |
| Verifier | 24GB | 64GB | 16GB | 8 Cores |

# Roadmap

<details open>
<summary>Completed</summary>

- [x] Challenge Request
- [x] Reward System
- [x] Bonding
- [x] Database
- [x] Auto Update
- [x] Forwarding

</details>

<details>
<summary>In Progress</summary>

- [] Tiered Requests to match throughput
- [] Inference Request
- [] Metapool
- [] flashbots' style block space for verifier bandwidth
- [] metrics dashboard
</details>

# Installation

## Overview
In order to run Fractal, you need to install Docker, PM2, and Fractal package. The following instructions apply only to Ubuntu OSes. For your specific OS, please refer to the official documentation.

<details>
<summary>Install Docker</summary>

Install docker on your machine. Follow the instructions [here](https://docs.docker.com/engine/install/). The following instructions apply only to Ubuntu OSes.

### Set up Docker's apt repository.
Before you install Docker Engine for the first time on a new host machine, you need to set up the Docker repository. Afterward, you can install and update Docker from the repository.x
```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

### Install Docker Engine
To install the latest version, run:
```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Post Installation Steps
To run docker commands without sudo, create a docker group and add your user.
```bash
sudo groupadd docker
sudo usermod -aG docker $USER
exit
```
Log back in and run the following command to verify that you can run docker commands without sudo.
```bash
docker ps
```
You have now installed Docker.
</details>

<details>

<summary>Install PM2</summary>

Install PM2 on your machine.

### Download NVM
To install or update nvm, you should run the install script. To do that, you may either download and run the script manually, or use the following cURL or Wget command:
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```
### Add NVM to bash profile
Running either of the above commands downloads a script and runs it. The script clones the nvm repository to ~/.nvm, and attempts to add the source lines from the snippet below to the correct profile file (~/.bash_profile, ~/.zshrc, ~/.profile, or ~/.bashrc).
```bash
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm
```
### Install Node
```bash
nvm install node
```

### Install PM2
```bash
npm install pm2@latest -g
```
You have now installed PM2.

</details>

### Install Fractal

### Clone the repository
```bash
git clone https://github.com/fractal-net/fractal.git
cd fractal
```

### Install dependencies
```bash
pip install -e .
```

You have now installed Fractal. You can now run a prover or verifier.


# Why use a Homogeneous Inference Network?
Inspiration for Homogeneous Inference Networks came from Manifold Labs' TARGON and can be read about here: (https://github.com/manifold-inc/targon/tree/main). Fractal is adopting the framework of Provers and Verifiers and implementing text-to-video generation. Redundant verification networks are gamification-resistant-- a critical start to improving the resiliency of the Bittensor network. By solving gamification, these networks allow for optimizations to be built around real compute-- starting with edge-node inference. Fractal is working to develop and implement routing mechanisms that optimize inference response speeds. This will be critical to gaining end-user adoption in a scalable way on the Bittensor network. In a world where hundreds of apps are being built on Bittensor, and hundreds of thousands (or millions) of user requests are being sent to subnets, the network must minimize response times. 

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
To get started running a prover, you will need to be running the docker containers for the requirements of the prover. To do this, run the following command:
```bash
cp neurons/prover/docker-compose.example.yml neurons/prover/docker-compose.yml
docker compose -f neurons/prover/docker-compose.yml up -d
```

this includes the following containers:
- TGI Inference Node
- Subtensor
- Prover (optional)


**experimental** optionally, you can edit the docker-compose.yml file to include the proving container, but you will need to edit the docker-compose.yml file and uncomment out the prover container. Otherwise you can run the prover with PM2.


### Docker

<details>
<summary>Run with Docker</summary>

```docker
  prover:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8091:8091"
    command: ./entrypoint.sh
    volumes:
      - ~/.bittensor/wallets:/root/.bittensor/wallets

```
and then edit the entrypoint.sh file to include the args specific for your prover.

```bash
python app.py --wallet.name WALLET_NAME --wallet.hotkey WALLET_HOTKEY --logging.debug --logging.trace --subtensor.chain_endpoint 0.0.0.0:9944
```

replace the wallet name and wallet hotkey with your wallet name and wallet hotkey. You can also change the subtensor chain endpoint to your own chain endpoint if you perfer.

</details>

### PM2

<details>
<summary> Run with PM2</summary>

```bash
cd neurons/prover
pm2 start app.py --name prover -- --wallet.name WALLET_NAME --wallet.hotkey WALLET_HOTKEY --logging.debug --logging.trace --subtensor.chain_endpoint 0.0.0.0:9944
```

replace the wallet name and wallet hotkey with your wallet name and wallet hotkey. You can also change the subtensor chain endpoint to your own chain endpoint if you perfer.

</details>

### Options
The add_prover_args function in the targon/utils/config.py file is used to add command-line arguments specific to the prover. Here are the options it provides:

1. --neuron.name: This is a string argument that specifies the name of the neuron. The default value is 'prover'.

2. --blacklist.force_verifier_permit: This is a boolean argument that, if set, forces incoming requests to have a permit. The default value is False.

3. --blacklist.allow_non_registered: This is a boolean argument that, if set, allows provers to accept queries from non-registered entities. This is considered dangerous and its default value is False.

4. --neuron.tgi_endpoint: This is a string argument that specifies the endpoint to use for the TGI client. The default value is "http://0.0.0.0:8080".



## Run a Verifier
To get started running a verifier, you will need to be running the docker containers for the requirements of the verifier. To do this, run the following command:
```bash
cp neurons/verifier/docker-compose.example.yml neurons/verifier/docker-compose.yml
./scripts/generate_redis_password.sh
vim neurons/verifier/docker-compose.yml # replace YOUR_PASSWORD_HERE with the password generated by the script
docker compose -f neurons/verifier/docker-compose.yml up -d
```

this includes the following containers:
- Redis
- TGI Inference Node
- Subtensor
- Verifier (optional)

> **IMPORTANT:** You will need to edit the docker-compose.yml file with your new password. You can do this by:
```bash
./scripts/generate_redis_password.sh
```
this will output a secure password for you to use. You will then need to edit the docker-compose.yml file and replace the password with your new password.

first use vim to edit the docker-compose.yml file:
```bash
vim neurons/verifier/docker-compose.yml
```
then replace the password with your new password:

```docker
  redis:
    image: redis:latest
    command: redis-server --requirepass YOUR_PASSWORD_HERE
    ports:
      - "6379:6379"
```

**experimental** optionally, you can edit the docker-compose.yml file to include the verifier container, but you will need to edit the docker-compose.yml file and uncomment out the verifier container. Otherwise you can run the verifier with PM2.


### Docker

<details>
<summary>Run with Docker</summary>

```docker
  verifier:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8091:8091"
    command: ./entrypoint.sh
    volumes:
      - ~/.bittensor/wallets:/root/.bittensor/wallets

```
and then edit the entrypoint.sh file to include the args specific for your prover.

```bash
python app.py --wallet.name WALLET_NAME --wallet.hotkey WALLET_HOTKEY --logging.debug --logging.trace --subtensor.chain_endpoint 0.0.0.0:9944 --database.password YOUR_PASSWORD_HERE
```

replace the wallet name, wallet hotkey, and db pass with your wallet name, wallet hotkey and pass. You can also change the subtensor chain endpoint to your own chain endpoint if you perfer.

</details>

### PM2

<details>
<summary>Run with PM2</summary

Run the following command to start the verifier with PM2:

```bash
cd neurons/verifier

pm2 start app.py --name verifier -- --wallet.name WALLET_NAME --wallet.hotkey WALLET_HOTKEY --logging.debug --logging.trace --subtensor.chain_endpoint
0.0.0.0:9944 --database.password YOUR_PASSWORD_HERE
```

### Options
The add_verifier_args function in the targon/utils/config.py file is used to add command-line arguments specific to the verifier. Here are the options it provides:

1. --neuron.sample_size: The number of provers to query in a single step. Default is 10.

2. --neuron.disable_set_weights: A flag that disables setting weights. Default is False.

3. --neuron.moving_average_alpha: Moving average alpha parameter, how much to add of the new observation. Default is 0.05.

4. --neuron.axon_off or --axon_off: A flag to not attempt to serve an Axon. Default is False.

5. --neuron.vpermit_tao_limit: The maximum number of TAO allowed to query a verifier with a vpermit. Default is 4096.

6. --neuron.tgi_endpoint: The endpoint to use for the TGI client. Default is "http://0.0.0.0:8080".

7. --database.host: The path to write debug logs to. Default is "127.0.0.1".

8. --database.port: The path to write debug logs to. Default is 6379.

9. --database.index: The path to write debug logs to. Default is 1.

10. --database.password: The password to use for the redis database. Default is None.

11. --neuron.compute_stats_interval: The interval at which to compute statistics. Default is 360.

These options can be used to customize the behavior of the verifier when it is run.

Refer to the code here:


replace the wallet name and wallet hotkey with your wallet name and wallet hotkey. You can also change the subtensor chain endpoint to your own chain endpoint if you perfer.

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
# fractal
