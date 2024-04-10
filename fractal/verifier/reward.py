# The MIT License (MIT)
# Copyright © 2024 Manifold Labs

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import torch
import hashlib
import numpy as np
import bittensor as bt

def hashing_function(input):
    if input is None:
        return '0000000000000000000000000000000000000000000000000000000000000000'
    hashed_input = hashlib.sha256(input.encode('utf-8')).hexdigest()
    return hashed_input

    

def response_time_sigmoid(response_time):
    """
    Sigmoid function to normalize response time.
    """
    b = 1.0
    h = 1.0
    numerator = 1 - np.exp(-1 * b * response_time)
    denominator = 1 + (np.exp(b * h) - 2) * np.exp(-1 * b * response_time)
    return 1 - (numerator / denominator)

def throughput_sigmoid(throughput):
    """
    Sigmoid function to normalize throughput.
    """
    b = 1.0
    h = 1.0
    numerator = 1 - np.exp(-1 * b * throughput)
    denominator = 1 + (np.exp(b * h) - 2) * np.exp(-1 * b * throughput)
    return 1 - (numerator / denominator)

def envelope(known_blocks, ramp_up_blocks): 
    """
    Envelope function to ramp up new miners
    """
    if known_blocks > ramp_up_blocks:
        return 1

    return np.sqrt(known_blocks / ramp_up_blocks)

def weighted_sum(
        challenge_success_rate, 
        inference_success_rate, 
        normalized_avg_response_time, 
        normalized_avg_throughput):
    """ 
    Computes the weighted sum of the normalized values.
    """
    challenge_weight = 0.25
    inference_weight = 0.25
    response_time_weight = 0.10
    throughput_weight = 0.40

    challenge_component = challenge_weight * challenge_success_rate
    inference_component = inference_weight * inference_success_rate
    response_time_component = response_time_weight * normalized_avg_response_time
    throughput_component = throughput_weight * normalized_avg_throughput

    return challenge_component + inference_component + response_time_component + throughput_component



def compute_reward(miner_stats):
    """ 
    Computes the reward value for a given inference or challenge.  
    Takes miner stats, normalizes where necessary, and returns the weighted sum of the normalized values.
    """

    # TODO: is necessary? or too punitive?
    # if not verified:
    #     return 0.0
    
    challenge_success_rate = miner_stats.challenge_successes / miner_stats.challenge_attempts
    inference_success_rate = miner_stats.inference_successes / miner_stats.inference_attempts
    response_time = response_time_sigmoid(miner_stats.average_response_time)
    throughput = throughput_sigmoid(miner_stats.average_throughput)
    
    return weighted_sum(challenge_success_rate, inference_success_rate, response_time, throughput)



def apply_reward_scores(
    self, uids, rewards
):
    """
    Adjusts the moving average scores for a set of UIDs based on their response times and reward values.

    This should reflect the distribution of axon response times (minmax norm)

    Parameters:
        uids (List[int]): A list of UIDs for which rewards are being applied.
        responses (List[Response]): A list of response objects received from the nodes.
        rewards (torch.FloatTensor): A tensor containing the computed reward values.
    """
    if self.config.neuron.verbose:
        bt.logging.debug(f"Applying rewards: {rewards}")
        bt.logging.debug(f"Reward shape: {rewards.shape}")
        bt.logging.debug(f"UIDs: {uids}")

    # Compute forward pass rewards
    # shape: [ metagraph.n ]
    scattered_rewards: torch.FloatTensor = self.scores.scatter(
        0, torch.tensor(uids).to(self.device), rewards
    ).to(self.device)
    bt.logging.trace(f"Scattered rewards: {scattered_rewards}")

    # Update moving_averaged_scores with rewards produced by this step.
    # shape: [ metagraph.n ]
    alpha: float = self.config.neuron.moving_average_alpha
    self.scores: torch.FloatTensor = alpha * scattered_rewards + (
        1 - alpha
    ) * self.scores.to(self.device)

    self.scores = (self.scores - self.config.neuron.decay_alpha).clamp(min=0)

    bt.logging.trace(f"Updated moving avg scores: {self.scores}")

