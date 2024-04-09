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
import typing
import asyncio

from fractal import protocol
from fractal.utils.uids import get_tiered_uids
from fractal.verifier.event import EventSchema

async def handle_inference(
        self, 
        private_input: typing.Dict[str,str], 
        sampling_params: protocol.InferenceeSamplingParams, 
        uid: int
    ):
    synapse = protocol.Challenge(
        sources = [private_input["sources"]],
        query = private_input["query"],
        sampling_params=sampling_params,
    )

    async for token in await self.dendrite(
        self.metagraph.axons[uid],
        synapse,
        deserialize=False,
        timeout=self.config.neuron.timeout,
    ):
        print(token)


    return None

async def inference_data(
        self
)-> typing.Tuple[bytes, typing.Callable]:
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

    start_time = time.time()

    uids, _ = await get_tiered_uids(self, k=10)

    tasks = []
    for uid in uids:
        tasks.append(asyncio.create_task(handle_inference(self, uid)))
    response_tuples = await asyncio.gather(*tasks)
    return event



