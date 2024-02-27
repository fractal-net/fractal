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

def autoupdate(branch: str = "main"):
    '''
    Automatically updates the Targon codebase to the latest version available.

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
        # Fetching latest version from the main branch
        response = requests.get(
            "https://raw.githubusercontent.com/fractal-net/fractal/main/VERSION",
            headers={'Cache-Control': 'no-cache'}
        )
        response.raise_for_status()
        latest_version = response.content.decode().strip()  # Remove trailing newline characters

        # Checking if local version is older than the remote version
        if latest_version != fractal.__version__:
            bt.logging.info(f"A newer version of Fractal ({latest_version}) is available. Updating...")
            base_path = os.path.abspath(__file__)
            while os.path.basename(base_path) != "fractal":
                base_path = os.path.dirname(base_path)
            base_path = os.path.dirname(base_path)

            # Fetching the tag corresponding to the latest version
            tag_response = requests.get(
                f"https://api.github.com/repos/fractal-net/fractal/git/refs/tags/{latest_version}"
            )
            tag_response.raise_for_status()
            tag_info = tag_response.json()
            tag_sha = tag_info["object"]["sha"]

            # Performing git checkout to update to the latest version
            os.system(f"cd {base_path} && git fetch --tags && git checkout {tag_sha}")

            # Checking if the update was successful
            with open(os.path.join(base_path, "VERSION")) as f:
                new_version = f.read().strip()

            # Restarting the application if the update was successful
            if new_version == latest_version:
                bt.logging.info("Fractal updated successfully. Restarting...")
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                bt.logging.error("Update failed. Manual update required.")
                
            # Update local version number
            fractal.__version__ = new_version
        else:
            bt.logging.info("Fractal is already up to date.")
    except Exception as e:
        bt.logging.error(f"Update check failed: {e}")

