# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
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

import os
import time
import typing
import torch
import asyncio
import random
import bittensor as bt
import base64
import skvideo.io
import numpy
numpy.float = numpy.float64
numpy.int = numpy.int_


from fractal import protocol
from fractal.utils.uids import get_random_uids
from fractal.verifier.event import EventSchema
from fractal.verifier.bonding import update_statistics, get_tier_factor
from fractal.constants import INFERENCE_FAILURE_REWARD
from fractal.verifier.reward import apply_reward_scores



def _filter_verified_responses(uids, responses):
    not_none_responses = [
        (uid, response[0])
        for (uid, (verified, response)) in zip(uids, responses)
        if verified != None
    ]

    if len(not_none_responses) == 0:
        return (), ()

    uids, responses = zip(*not_none_responses)
    return uids, responses


def verify(output):
    """
    Verifies the output of a prover.
    """
    if output is None:
        return False

    try: 
        binary_video = base64.b64decode(output)
        return is_video_valid(binary_video)

    except Exception as e:
        print(f"Error decoding base64 video: {e}")
        return False

def is_video_valid(binary_video):
    try:
        with open('temp_video.mp4', 'wb') as temp_file:
            temp_file.write(binary_video)
        video = skvideo.io.vread('temp_video.mp4')
        return video.shape[0] > 0
    except Exception as e:
        print(f"Error validating video: {e}")
        return False
    finally:
        # Delete the temporary file if it exists
        if os.path.exists('temp_video.mp4'):
            os.remove('temp_video.mp4')


async def handle_inference(
        self, 
        uid: int,
        private_input: typing.Dict,
        sampling_params: protocol.PromptRequestSamplingParams
    ):
    """ 
    Handles an inference sent to a prover and verifies the response.
    parameters:
    - uid (int): The UID of the prover being challenged.
    - private_input (typing.Dict[str,str]): The private input to the prover.
    - sampling_params (protocol.InferenceeSamplingParams): The sampling parameters for the inference.
    """

    hotkey = self.metagraph.hotkeys[uid]
    keys = await self.database.hkeys(f"hotkey:{hotkey}")
    bt.logging.trace(f"{len(keys)} stats pulled for hotkey {hotkey}")
    prompt = private_input["query"]

    if not self.config.mock: 
        synapse = protocol.PromptRequest(
            query = private_input["query"],
            sampling_params=sampling_params,
        )

        response = await self.dendrite(
            self.metagraph.axons[uid],
            synapse,
            deserialize=False,
            timeout=self.config.neuron.timeout,
        )

        output = response.completion
        
        verified = verify(output)

        output_tup = (
            synapse,
            uid
        )

        return verified, output_tup

    else:
        synapse = protocol.PromptRequest(
            query = private_input["query"],
            sampling_params=sampling_params,
        )

        response = await self.client.generate(prompt, sampling_params.seed)
        await self.client.close_session()

        synapse.completion = response

        verified = verify( response )

        output_tup = (
            synapse,
            uid
        )
        return verified, output_tup

async def inference_provers(
        self, 
        prompt: str,
    ):
    """ Returns the data and a callback to be used for inference. """

    event = EventSchema(
        task_name="inference",
        successful=[],
        completion_times=[],
        task_status_messages=[],
        task_status_codes=[],
        block=self.subtensor.get_current_block(),
        uids=[],
        step_length=0.0,
        best_uid=-1,
        best_hotkey="",
        rewards=[],
        set_weights=[],
    )

    print("do we get here")
    private_input = {'query': prompt}
    print(f"do we get here 2 {prompt}")
    seed = random.randint(1, 2**32 - 1)

    inference_params = protocol.PromptRequestSamplingParams(
        seed=seed,
    )

    start_time = time.time()
    uids = get_random_uids(self, k=3)

    print(f"uids: {uids}")
    print("do we get here 3")

    tasks = []
    for uid in uids:
        tasks.append(asyncio.create_task(handle_inference(self, uid, private_input, inference_params)))
    responses = await asyncio.gather(*tasks)

    rewards: torch.FloatTensor = torch.zeros(len(responses), dtype=torch.float32).to(
        self.device
    )

    print(f"responses: {responses}")
    print("do we get here 4")


    remove_reward_idxs = []
    for i, (verified, (response, uid)) in enumerate(responses):
        bt.logging.trace(
            f"Inference iteration {i} uid {uid}"
        )

        hotkey = self.metagraph.hotkeys[uid]

        await update_statistics(
            ss58_address=hotkey,
            success=verified,
            task_type="inference",
            database=self.database,
            current_block=self.block,
        )

        tier_factor = await get_tier_factor(hotkey, self.database)
        rewards[i] = 1.0 * tier_factor if verified else INFERENCE_FAILURE_REWARD

        if self.config.mock:
            event.uids.append(uid)
            event.successful.append(verified)        
            event.completion_times.append(0.0) # What is this
            event.task_status_messages.append("mock")
            event.task_status_codes.append(0)
            event.rewards.append(rewards[i].item())
        else: 
            event.uids.append(uid)
            event.successful.append(verified)
            event.completion_times.append(response.dendrite.process_time)
            event.task_status_messages.append(response.dendrite.status_message)
            event.task_status_codes.append(response.dendrite.status_code)
            event.rewards.append(rewards[i].item())

    bt.logging.debug(
        f"inference_provers() rewards: {rewards} | uids {uids} hotkeys {[self.metagraph.hotkeys[uid] for uid in uids]}"
    )

    event.step_length = time.time() - start_time

    if len(responses) == 0:
        bt.logging.debug(f"Received responses from provers, returning event early.")
        error_synapse = protocol.PromptRequest(
            query = private_input["query"],
            sampling_params=sampling_params,
        )
        error_synapse.completion = "No valid responses received from any provers."
        error_synapse.axon.status_code = 404  # Example status code for "Not Found" or similar
        return event, error_synapse

    # Remove UIDs without hashes (don't punish new miners that have no challenges yet)
    uids, responses = _filter_verified_responses(uids, responses)
    rewards = remove_indices_from_tensor(rewards, remove_reward_idxs)

    bt.logging.trace("Applying inference rewards")

    apply_reward_scores(
        self,
        uids,
        responses,
        rewards,
        timeout=self.config.neuron.timeout,
        mode=self.config.neuron.reward_mode,
    )

    if event.rewards:
        best_index = max(range(len(event.rewards)), key=event.rewards.__getitem__)
        event.best_uid = event.uids[best_index]
        event.best_hotkey = self.metagraph.hotkeys[event.best_uid]

    verified_responses = [(resp, uid) for (verified, resp), uid in zip(responses, uids) if verified and resp is not None]

    if verified_responses: 

        responses_by_tier = torch.tensor([await get_tier_factor(self.metagraph.hotkeys[uid], self.database) for _, uid in verified_responses])

        # Find the index of the highest reward
        best_index = torch.argmax(responses_by_tier).item()
        best_response, best_uid = verified_responses[best_index]
        
        # Log and return the best response
        bt.logging.debug(f"Best response UID: {best_uid} with reward: {rewards[best_index]}")
        return event, best_response

    else:
        # Return an error response or default response if no valid responses exist
        error_synapse = protocol.PromptRequest(
            query = private_input["query"],
            sampling_params=sampling_params,
        )
        error_synapse.completion = "No valid responses received from any provers."
        error_synapse.axon.status_code = 404  # Example status code for "Not Found" or similar
        return event, error_synapse
    
