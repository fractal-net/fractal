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

import time
import sys 
import os
import typing
import bittensor as bt

from fractal.base.prover import BaseProverNeuron
from fractal.base.client import HttpClient
from fractal.protocol import Inference, Challenge

class Prover(BaseProverNeuron):
    """
    Your prover neuron class. You should use this class to define your prover's behavior. In particular, you should replace the forward function with your own logic. You may also want to override the blacklist and priority functions according to your needs.

    This class inherits from the BaseProverNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a prover such as blacklisting unrecognized hotkeys, prioritizing requests based on stake, and forwarding requests to the forward function. If you need to define custom
    """

    def __init__(self, config=None):
        super(Prover, self).__init__(config=config)
        self.client = HttpClient(self.config.neuron.model_endpoint)

    async def inference_request(
            self, synapse: Inference
    ):
        """
        Sends an inference request to the prover's model endpoint.

        Args:
            synapse (typing.Union[Challenge, Inference]): The synapse object containing the request data.

        Returns:
            typing.Tuple[bool, str]: A tuple containing a boolean indicating whether the request was successful,
                                    and a string containing the response from the prover's model endpoint.

        This function is a placeholder and should be replaced with a call to your prover's model endpoint.
        """
        output = await self.client.generate(synapse.query, synapse.sampling_params.seed)
        await self.client.close_session()

        synapse.completion = output

        return synapse


    async def challenge_request(
            self, synapse: Challenge
    ):
        """
        Sends an inference request to the prover's model endpoint.

        Args:
            synapse (typing.Union[Challenge, Inference]): The synapse object containing the request data.

        Returns:
            typing.Tuple[bool, str]: A tuple containing a boolean indicating whether the request was successful,
                                    and a string containing the response from the prover's model endpoint.

        This function is a placeholder and should be replaced with a call to your prover's model endpoint.
        """

        output = await self.client.generate(synapse.query, synapse.sampling_params.seed)
        await self.client.close_session()

        synapse.completion = output

        return synapse

    async def forward(
        self, synapse: Challenge
    ) -> Challenge:
        """
        Processes the incoming synapse by performing a predefined operation on the input data.

        Args:
            synapse (typing.Union[Challenge, Inference]): The synapse object containing the 'dummy_input' data.

        Returns:
            typing.Union[Challenge, Inference]: The synapse object with the 'dummy_output' field set to twice the 'dummy_input' value.

        The 'forward' function is a placeholder and should be overridden with logic that is appropriate for
        the prover's intended operation. This method demonstrates a basic transformation of input data.
        """
        if isinstance(synapse, Inference):
            return await self.inference_request(synapse)
    
        return await self.challenge_request(synapse)

    async def blacklist(
        self, synapse: Challenge
    ) -> typing.Tuple[bool, str]:
        """
        Determines whether an incoming request should be blacklisted and thus ignored. Your implementation should
        define the logic for blacklisting requests based on your needs and desired security parameters.

        Blacklist runs before the synapse data has been deserialized (i.e. before synapse.data is available).
        The synapse is instead contructed via the headers of the request. It is important to blacklist
        requests before they are deserialized to avoid wasting resources on requests that will be ignored.

        Args:
            synapse (PromptingSynapse): A synapse object constructed from the headers of the incoming request.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating whether the synapse's hotkey is blacklisted,
                            and a string providing the reason for the decision.

        This function is a security measure to prevent resource wastage on undesired requests. It should be enhanced
        to include checks against the metagraph for entity registration, validator status, and sufficient stake
        before deserialization of synapse data to minimize processing overhead.

        Example blacklist logic:
        - Reject if the hotkey is not a registered entity within the metagraph.
        - Consider blacklisting entities that are not validators or have insufficient stake.

        In practice it would be wise to blacklist requests from entities that are not validators, or do not have
        enough stake. This can be checked via metagraph.S and metagraph.validator_permit. You can always attain
        the uid of the sender via a metagraph.hotkeys.index( synapse.dendrite.hotkey ) call.

        Otherwise, allow the request to be processed further.
        """
        if synapse.dendrite.hotkey not in self.metagraph.hotkeys:
            # Ignore requests from unrecognized entities.
            bt.logging.trace(
                f"Blacklisting unrecognized hotkey {synapse.dendrite.hotkey}"
            )
            return True, "Unrecognized hotkey"

        bt.logging.trace(
            f"Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}"
        )
        return False, "Hotkey recognized!"

    async def priority(self, synapse: Challenge) -> float:
        """
        The priority function determines the order in which requests are handled. More valuable or higher-priority
        requests are processed before others. You should design your own priority mechanism with care.

        This implementation assigns priority to incoming requests based on the calling entity's stake in the metagraph.

        Args:
            synapse (PromptingSynapse): The synapse object that contains metadata about the incoming request.

        Returns:
            float: A priority score derived from the stake of the calling entity.

        Provers may recieve messages from multiple entities at once. This function determines which request should be
        processed first. Higher values indicate that the request should be processed first. Lower values indicate
        that the request should be processed later.

        Example priority logic:
        - A higher stake results in a higher priority value.
        """
        # TODO(developer): Define how miners should prioritize requests.
        caller_uid = self.metagraph.hotkeys.index(
            synapse.dendrite.hotkey
        )  # Get the caller index.
        prirority = float(
            self.metagraph.S[caller_uid]
        )  # Return the stake as the priority.
        bt.logging.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: ", prirority
        )
        return prirority


# This is the main function, which runs the prover.
if __name__ == "__main__":
    with Prover() as prover:
        while True:
            if prover.restart_required:
                os.execv(sys.executable, [sys.executable] + sys.argv)
            bt.logging.info("Prover running...", time.time())
            time.sleep(5)
