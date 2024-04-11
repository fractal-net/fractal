import bittensor as bt

# Assuming you have a Subtensor instance
subtensor = bt.subtensor(network="finney")

# Call the function with the specific UID and netuid
neuron_info = subtensor.neuron_for_uid(uid=1, netuid=29)

print(neuron_info)
