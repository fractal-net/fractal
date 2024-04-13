import asyncio
import bittensor as bt
from fractal.protocol import PromptRequest, PromptRequestSamplingParams
import random

def get_seed():
    return random.randint(0, 2**32 - 1)



async def main():
    # setup wallet and subtensor connection
    wallet = bt.wallet()
    subtensor = bt.subtensor("test")
    dendrite = bt.dendrite(wallet=wallet)
    axon_info = bt.AxonInfo(
        ip="127.0.0.1",
        port=8091,
        ip_type=4,
        version=bt.__version_as_int__,
        hotkey="5Cex1UGEN6GZBcSBkWXtrerQ6Zb7h8eD7oSe9eDyZmj4doWu",
        coldkey="5GgKzgB84ywpBH2uZYaPuh99HK5DUGkfkHiRzxn2D8cYhf2v",
    )

    # Store some data and retrieve it
    prompt = b"Generate a video of a cat playing the piano."

    sampling_params = PromptRequestSamplingParams(seed=get_seed())
    synapse = PromptRequest(
        query=prompt,
        sampling_params=sampling_params
    )

    reppy = await dendrite.call(target_axon=axon_info, synapse=synapse, timeout=100.0, deserialize=True)
    print(reppy.axon.status_code)
    print(reppy.completion)


if __name__ == "__main__":
    asyncio.run(main())

