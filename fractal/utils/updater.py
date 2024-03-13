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
import sys
import requests
import bittensor as bt
import fractal

def autoupdate(self, branch: str = "main"):
    pass
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


