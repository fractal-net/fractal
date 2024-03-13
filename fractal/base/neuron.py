# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2023 Opentensor Foundation
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
import sys
import copy
import torch
import bittensor as bt
import requests

from abc import ABC, abstractmethod

# Sync calls set weights and also resyncs the metagraph.
import fractal
from fractal.utils.misc import ttl_get_block
from fractal import __spec_version__ as spec_version
from fractal.mock import MockSubtensor, MockMetagraph
from fractal.utils.config import check_config, add_args, config


class BaseNeuron(ABC):
    """
    Base class for Bittensor provers. This class is abstract and should be inherited by a subclass. It contains the core logic for all neurons; verifiers and provers.

    In addition to creating a wallet, subtensor, and metagraph, this class also handles the synchronization of the network state via a basic checkpointing mechanism based on epoch length.
    """

    @classmethod
    def check_config(cls, config: "bt.Config"):
        check_config(cls, config)

    @classmethod
    def add_args(cls, parser):
        add_args(cls, parser)

    @classmethod
    def _config(cls):
        return config(cls)

    subtensor: "bt.subtensor"
    wallet: "bt.wallet"
    metagraph: "bt.metagraph"
    spec_version: int = spec_version

    @property
    def block(self):
        return ttl_get_block(self)
    def autoupdate(self, branch: str = "main"):
        '''
        Automatically updates the Fractal codebase to the latest version available.

        This function checks the remote repository for the latest version of Fractal by fetching the VERSION file from the main branch.
        If the local version is older than the remote version, it performs a git pull to update the local codebase to the latest version.
        After successfully updating, it restarts the application with the updated code.

        Note:
        - The function assumes that the local codebase is a git repository and has the same structure as the remote repository.
        - It requires git to be installed and accessible from the command line.
        - The function will restart the application using the same command-line arguments it was originally started with.
        - If the update fails, manual intervention is required to resolve the issue and restart the application.
        '''
        bt.logging.info("Checking for updates...")
        try:
            response = requests.get(
                "https://raw.githubusercontent.com/fractal-net/fractal/main/VERSION",
                headers={'Cache-Control': 'no-cache'}
            )
            response.raise_for_status()
            repo_version = response.content.decode().strip()  # Remove trailing newline characters
            latest_version = [int(v) for v in repo_version.split(".")]
            local_version = [int(v) for v in fractal.__version__.split(".")]

            bt.logging.info(f"Local version: {fractal.__version__}")
            bt.logging.info(f"Latest version: {repo_version}")

            if latest_version > local_version:
                bt.logging.info("A newer version of Fractal is available. Updating...")
                base_path = os.path.abspath(__file__)
                while os.path.basename(base_path) != "fractal":
                    base_path = os.path.dirname(base_path)
                base_path = os.path.dirname(base_path)
                os.system(f"cd {base_path} && git checkout main && git pull")

                with open(os.path.join(base_path, "VERSION")) as f:
                    new_version = f.read().strip()
                    new_version = [int(v) for v in new_version.split(".")]

                    if new_version == latest_version:
                        bt.logging.info("Fractal updated successfully. Restarting...")
                        self.restart_required = True
                    else:
                        bt.logging.error("Update failed. Manual update required.")

        except Exception as e:
            bt.logging.error(f"Update check failed: {e}")




    def __init__(self, config=None):
        base_config = copy.deepcopy(config or BaseNeuron._config())
        self.config = self._config()
        self.config.merge(base_config)
        self.check_config(self.config)

        # Set up logging with the provided configuration and directory.
        bt.logging(config=self.config, logging_dir=self.config.full_path)


        # Log the configuration for reference.
        bt.logging.info(self.config)
        
        self.device = torch.device(self.config.neuron.device)

        self.restart_required = False

        if not self.config.disable_autoupdate:
            self.autoupdate(self.config.autoupdate.branch)


        # Build Bittensor objects
        # These are core Bittensor classes to interact with the network.
        bt.logging.info("Setting up bittensor objects.")

        # The wallet holds the cryptographic key pairs for the prover.
        if self.config.mock:
            self.wallet = bt.MockWallet(config=self.config)
            self.subtensor = MockSubtensor(
                self.config.netuid, wallet=self.wallet
            )
            self.metagraph = MockMetagraph(
                self.config.netuid, subtensor=self.subtensor
            )
        else:
            self.wallet = bt.wallet(config=self.config)
            self.subtensor = bt.subtensor(config=self.config)
            self.metagraph = self.subtensor.metagraph(self.config.netuid)

        bt.logging.info(f"Wallet: {self.wallet}")
        bt.logging.info(f"Subtensor: {self.subtensor}")
        bt.logging.info(f"Metagraph: {self.metagraph}")

        # Check if the prover is registered on the Bittensor network before proceeding further.
        self.check_registered()

        # Each prover gets a unique identity (UID) in the network for differentiation.
        self.uid = self.metagraph.hotkeys.index(self.wallet.hotkey.ss58_address)
        bt.logging.info(
            f"Running neuron on subnet: {self.config.netuid} with uid {self.uid} using network: {self.subtensor.chain_endpoint}"
        )
        self.step = 0
        

    @abstractmethod
    async def forward(self, synapse: bt.Synapse) -> bt.Synapse:
        ...

    @abstractmethod
    def run(self):
        ...


    def get_last_adjustment_block(self) -> int:
        with self.subtensor.substrate as substrate:
            return substrate.query('SubtensorModule', 'LastAdjustmentBlock', [self.config.netuid]).value
    
    def get_adjustment_interval(self) -> int:
        with self.subtensor.substrate as substrate:
            return substrate.query('SubtensorModule', 'AdjustmentInterval', [self.config.netuid]).value


    def sync(self):
        """
        Wrapper for synchronizing the state of the network for the given prover or verifier.
        """
        # Ensure prover or verifier hotkey is still registered on the network.
        self.check_registered()

        if self.should_sync_metagraph():
            self.resync_metagraph()

        if self.should_set_weights():
            self.set_weights()

        # Always save state.
        self.save_state()

    def check_registered(self):
        # --- Check for registration.
        if not self.subtensor.is_hotkey_registered(
            netuid=self.config.netuid,
            hotkey_ss58=self.wallet.hotkey.ss58_address,
        ):
            bt.logging.error(
                f"Wallet: {self.wallet} is not registered on netuid {self.config.netuid}."
                f" Please register the hotkey using `btcli subnets register` before trying again"
            )
            sys.exit()

    def should_sync_metagraph(self):
        """
        Check if enough epoch blocks have elapsed since the last checkpoint to sync.
        """
        return (
            self.block - self.metagraph.last_update[self.uid]
        ) > self.config.neuron.epoch_length

    def should_set_weights(self) -> bool:
        # Don't set weights on initialization.
        if self.step == 0:
            return False

        # Check if enough epoch blocks have elapsed since the last epoch.
        if self.config.neuron.disable_set_weights:
            return False

        # Define appropriate logic for when set weights.
        return (
            self.block - self.metagraph.last_update[self.uid]
        ) > self.config.neuron.epoch_length

    def save_state(self):
        bt.logging.warning(
            "save_state() not implemented for this neuron. You can implement this function to save model checkpoints or other useful data."
        )

    def load_state(self):
        bt.logging.warning(
            "load_state() not implemented for this neuron. You can implement this function to load model checkpoints or other useful data."
        )
