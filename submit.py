import bittensor as bt
import time

wallet = bt.wallet(name="net")
unlocked_wallet = wallet.coldkey
subtensor = bt.subtensor("finney")
tries = 1000


def create_extrinsic():
    with subtensor.substrate as substrate:
        call = substrate.compose_call(
            call_module="SubtensorModule",
            call_function="register_network",
            call_params={
                'immunity_period': 0,
                'reg_allowed': True,
            },
        )

        extrinsic = substrate.create_signed_extrinsic(
            call=call,
            keypair=unlocked_wallet,
        )

        return extrinsic

def submit_extrinsic( extrinsic):

    with subtensor.substrate as substrate:
        receipt = substrate.submit_extrinsic( extrinsic, wait_for_inclusion=True, wait_for_finalization=True )
        print(receipt)    
        # process if registration successful
        receipt.process_events()
        bt.logging.info( receipt )
        if not receipt.is_success:
            print("fail") 
            time.sleep(0.5)
        else:
            print("success")

for attempt in range (tries):
    start_time = time.time()
    signed_extrinsic = create_extrinsic()
    end_time = time.time() - start_time
    start_send_time = time.time()
    success = submit_extrinsic(signed_extrinsic)

    if success:
        end_send_time = time.time() - start_send_time
        bt.logging.info(f"Extrinsic created in {end_time} seconds and sent in {end_send_time} seconds")
    else:
        bt.logging.info(f"Extrinsic failed to send")
        continue

