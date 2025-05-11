import asyncio
import requests

from ollama import Client, ChatResponse

from .ContractUtility import ContractUtility
from .RoflUtility import RoflUtility


class PaypalOracle:
    def __init__(self,
                 contract_address: str,
                 network_name: str,
                 rofl_utility: RoflUtility,
                 secret: str):
        contract_utility = ContractUtility(network_name, secret)
        abi, bytecode = ContractUtility.get_contract('Escrow')

        self.rofl_utility = rofl_utility
        self.contract = contract_utility.w3.eth.contract(address=contract_address, abi=abi)
        self.w3 = contract_utility.w3

    def set_oracle_address(self):
        contract_addr = self.contract.functions.oracle().call()
        if  contract_addr != self.w3.eth.default_account:
            print(f"Contract oracle {contract_addr} does not match our address {self.w3.eth.default_account}, updating...",)
            tx_params = self.contract.functions.setOracle(self.w3.eth.default_account).build_transaction({'gasPrice': self.w3.eth.gas_price})
            tx_hash = self.rofl_utility.submit_tx(tx_params)
            print(f"Got receipt {tx_hash} {dir(tx_hash)}")
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Updated. Transaction hash: {tx_receipt.transactionHash.hex()}")
        else:
            print(f"Contract oracle {contract_addr} matches our address {self.w3.eth.default_account}")

    async def log_loop(self, poll_interval):
        print(f"Listening for subscriptions...", flush=True)
        while True:
            logs = self.contract.events.NewSubscription().get_logs(fromBlock=self.w3.eth.block_number)
            for log in logs:
                submitter = log.args.sender
                id = log.args.id
                print(f"New subscription {id} submitted by {submitter}")
                # TODO: handle subscription
            await asyncio.sleep(poll_interval)

    def run(self) -> None:
        self.set_oracle_address()

        # Subscribe to NewSubscription event
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                asyncio.gather(self.log_loop(2)))
        finally:
            loop.close()

    def submit_answer(self, answer: str, prompt_id: int, address: str):
        # Set a message
        tx_hash = self.contract.functions.submitAnswer(answer, prompt_id, address).transact({'gasPrice': self.w3.eth.gas_price, 'gas': max(3000000, 1500*len(answer))})
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Submitted answer. Transaction hash: {tx_receipt.transactionHash.hex()}")
