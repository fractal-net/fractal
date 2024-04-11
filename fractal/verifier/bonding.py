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
from dataclasses import dataclass


@dataclass
class Miner:
    """
    Represents a miner's statistics in the homogenous inference grid
    """

    inference_attempts: int
    inference_successes: int
    challenge_attempts: int
    challenge_successes: int
    total_attempts: int
    total_successes: int
    average_response_time: float
    average_throughput: float
    first_seen: int = 0

    def to_dict(self):
        return {
            "inference_attempts": self.inference_attempts,
            "inference_successes": self.inference_successes,
            "challenge_attempts": self.challenge_attempts,
            "challenge_successes": self.challenge_successes,
            "total_interval_attempts": self.total_attempts,
            "total_interval_successes": self.total_successes,
            "average_response_time": self.average_response_time,
            "average_throughput": self.average_throughput,
            "first_seen": self.first_seen,
        }

    @staticmethod
    def from_dict(data):
        return Miner(
            inference_attempts=data["inference_attempts"],
            inference_successes=data["inference_successes"],
            challenge_attempts=data["challenge_attempts"],
            challenge_successes=data["challenge_successes"],
            total_attempts=data["total_attempts"],
            total_successes=data["total_successes"],
            average_response_time=data["average_response_time"],
            average_throughput=data["average_throughput"],
            first_seen=data.get("first_seen", 0),
        )


async def reset_request_stats(stats_key: str, database: aioredis.Redis):
    await database.hset(
        stats_key,
        mapping={
            "inference_attempts": 0,
            "inference_successes": 0,
            "challenge_attempts": 0,
            "challenge_successes": 0,
            "total_attempts": 0,
            "total_successes": 0,
            "average_response_time": ESTIMATED_AVERAGE_RESPONSE_TIME,
            "average_throughput": ESTIMATED_AVERAGE_THROUGHPUT,
        },
    )


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


async def register_miner(
    ss58_address: str, database: aioredis.Redis, current_block: int
):
    """
    Registers a new miner in the local copy of the homogeneous inference grid, initializing their statistics.

    Args:
        ss58_address (str): The unique address (hotkey) of the miner to be registered.
        database (redis.Redis): The Redis client instance for database operations.
    """
    # Initialize statistics for a new miner in a separate hash
    await database.hset(
        f"stats:{ss58_address}",
        mapping={
            "inference_attempts": 0,
            "inference_successes": 0,
            "challenge_attempts": 0,
            "challenge_successes": 0,
            "total_attempts": 0,
            "total_successes": 0,
            "average_response_time": ESTIMATED_AVERAGE_RESPONSE_TIME,
            "average_throughput": ESTIMATED_AVERAGE_THROUGHPUT,
            "first_seen": current_block,
        },
    )


async def update_statistics(
    ss58_address: str,
    success: bool,
    task_type: str,
    database: aioredis.Redis,
    current_block: int,
    response_time: float,
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
    print("do we even get here 1 ?")
    stats_key = f"stats:{ss58_address}"

    print("do we even get here 2 ?")
    total_attempts = await database.hincrby(stats_key, f"total_attempts", 1)

    if task_type in ["inference", "challenge"]:
        await database.hincrby(stats_key, f"{task_type}_attempts", 1)
        if success:
            # mark increase total success count
            await database.hincrby(stats_key, "total_successes", 1)
            # mark increase query type success count
            await database.hincrby(stats_key, f"{task_type}_successes", 1)

    print("do we even get here 3 ?")
    # set the updated response time
    previous_response_time = await get_previous_average_response_time(
        ss58_address, database
    )

    print("do we even get here 4 ?")
    

    if total_attempts == 1:
        updated_response_time = response_time
    else:
        updated_response_time = (
            previous_response_time * (total_attempts - 1) + response_time
        ) / total_attempts

    
    print("do we even get here 4.1 ?")
    await database.hset(
        stats_key, "average_response_time", updated_response_time
    )

    # set the updated throughput
    print("do we even get here 5 ?")
    success_count = int(await database.hget(stats_key, f"total_successes"))
    print("do we even get here 5.1 ?")
    print("success_count", success_count)
    print("total_attempts", total_attempts)
    accuracy_rate = success_count / total_attempts
    print("do we even get here 5.2 ?")
    new_throughput = accuracy_rate / updated_response_time
    print("do we even get here 5.3 ?")

    await database.hset(stats_key, "average_throughput", new_throughput)

    print("do we even get here 6?")

    miner_stats = await database.hgetall(stats_key)
    print("do we even get here 7 ?")
    print("000000000000")
    print(miner_stats)
    print("000000000000")

    # TODO: fix to resonable values as defaults

    miner = Miner.from_dict(
        {
            "inference_attempts": int(miner_stats.get(b"inference_attempts", b"0")),
            "inference_successes": int(miner_stats.get(b"inference_successes", b"0")),
            "challenge_attempts": int(miner_stats.get(b"challenge_attempts", b"0")),
            "challenge_successes": int(miner_stats.get(b"challenge_successes", b"0")),
            "total_attempts": int(miner_stats.get(b"total_attempts", b"0")),
            "total_successes": int(miner_stats.get(b"total_successes", b"0")),
            "average_response_time": float(
                miner_stats.get(b"average_response_time", b"0.0")
            ),
            "average_throughput": float(miner_stats.get(b"average_throughput", b"0.0")),
            "first_seen": int(miner_stats.get(b"first_seen", b"0")),
        }
    )
    print("do we even get here 8 ?")

    return miner


async def get_previous_average_response_time(
    ss58_address: str, database: aioredis.Redis
):
    """
    Retrieves the previous average response time of a miner from the database.

    Args:
        ss58_address (str): The unique address (hotkey) of the miner.
        database (redis.Redis): The Redis client instance for database operations.

    Returns:
        The previous average response time of the miner.
    """
    return float(await database.hget(f"stats:{ss58_address}", "average_response_time"))
