# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2023 philanthrope <-- Main Author
# Copyright © 2024 Manifold Labs
# Copyright © 2024 Fractal

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

import asyncio
import bittensor as bt
from redis import asyncio as aioredis
from fractal.constants import *

# TODO: update
async def reset_request_stats(stats_key: str, database: aioredis.Redis):
    await database.hmset(
        stats_key,
        {
            "inference_attempts": 0,
            "inference_successes": 0,
            "challenge_successes": 0,
            "challenge_attempts": 0,
            "total_interval_successes": 0,
        },
    )


# TODO: update
async def rollover_request_stats(database: aioredis.Redis):
    """
    Asynchronously resets the request statistics for all miners.
    This function should be called periodically to reset the statistics for all miners.
    Args:
        database (redis.Redis): The Redis client instance for database operations.
    """
    miner_stats_keys = [stats_key async for stats_key in database.scan_iter("stats:*")]
    tasks = [reset_request_stats(stats_key, database) for stats_key in miner_stats_keys]
    await asyncio.gather(*tasks)


# TODO: update
async def miner_is_registered(ss58_address: str, database: aioredis.Redis):
    """
    Checks if a miner is registered in the database.

    Parameters:
        ss58_address (str): The key representing the hotkey.
        database (redis.Redis): The Redis client instance.

    Returns:
        True if the miner is registered, False otherwise.
    """
    return await database.exists(f"stats:{ss58_address}")


# TODO: update
async def register_miner(ss58_address: str, database: aioredis.Redis, current_block: int):
    """
    Registers a new miner in the local copy of the homogeneous inference grid, initializing their statistics.

    Args:
        ss58_address (str): The unique address (hotkey) of the miner to be registered.
        database (redis.Redis): The Redis client instance for database operations.
    """
    # Initialize statistics for a new miner in a separate hash
    await database.hmset(
        f"stats:{ss58_address}",
        {
            "inference_attempts": 0,
            "inference_successes": 0,
            "challenge_successes": 0,
            "challenge_attempts": 0,
            "total_attempts": 0,
            "total_successes": 0,
            "last_interval_block": current_block, 
        },
    )


# TODO: update
async def update_statistics(
    ss58_address: str, success: bool, task_type: str, database: aioredis.Redis, current_block: int
):
    """
    Updates the statistics of a miner in the decentralized storage system.
    If the miner is not already registered, they are registered first. This function updates
    the miner's statistics based on the task performed (store, challenge, retrieve) and whether
    it was successful.
    Args:
        ss58_address (str): The unique address (hotkey) of the miner.
        success (bool): Indicates whether the task was successful or not.
        task_type (str): The type of task performed ('store', 'challenge', 'retrieve').
        database (redis.Redis): The Redis client instance for database operations.
    """
    # Check and see if this miner is registered.
    if not await miner_is_registered(ss58_address, database):
        bt.logging.debug(f"Registering new miner {ss58_address}...")
        await register_miner(ss58_address, database, current_block)

    # Update statistics in the stats hash
    stats_key = f"stats:{ss58_address}"

    if task_type in ["inference", "challenge"]:
        await database.hincrby(stats_key, f"{task_type}_attempts", 1)
        if success:
            await database.hincrby(stats_key, f"{task_type}_successes", 1)

            # --- add to total_interval_successes
            await database.hincrby(stats_key, "total_interval_successes", 1)


    # Update the total successes that we rollover every epoch
    if await database.hget(stats_key, "total_successes") == None:
        inference_successes = int(await database.hget(stats_key, "inference_successes"))
        challenge_successes = int(await database.hget(stats_key, "challenge_successes"))
        total_successes = inference_successes + challenge_successes
        await database.hset(stats_key, "total_successes", total_successes)
    if success:
        await database.hincrby(stats_key, "total_successes", 1)

