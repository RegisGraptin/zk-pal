# Blockchain Handler for EVM Interactions
import logging
from web3 import Web3
from web3.middleware import geth_poa_middleware # For POA chains like BSC, Polygon

logger = logging.getLogger(__name__)

class BlockchainHandler:
    def __init__(self, rpc_url, sender_private_key, chain_id=None):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.sender_private_key = sender_private_key
        self.sender_address = self.w3.eth.account.from_key(sender_private_key).address
        self.chain_id = chain_id

        if not self.w3.is_connected():
            logger.error(f"Failed to connect to EVM RPC: {rpc_url}")
            raise ConnectionError(f"Failed to connect to EVM RPC: {rpc_url}")
        else:
            logger.info(f"Successfully connected to EVM RPC: {rpc_url}. Chain ID: {self.w3.eth.chain_id}")
            if self.chain_id and self.w3.eth.chain_id != self.chain_id:
                logger.warning(f"Provided chain_id ({self.chain_id}) does not match RPC chain_id ({self.w3.eth.chain_id}). Using RPC's chain_id.")
                self.chain_id = self.w3.eth.chain_id # Prefer the RPC's chain_id if different
            elif not self.chain_id:
                self.chain_id = self.w3.eth.chain_id

        # Middleware for PoA chains (e.g., Polygon, BSC)
        # This might be needed if connecting to such networks.
        # You might need to conditionally apply this based on the chain or RPC.
        # For now, let's inject it as it's often required for common testnets/mainnets.
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    def get_balance(self, address=None):
        """Gets the native currency balance of an address (default: sender's address)."""
        if address is None:
            address = self.sender_address
        balance_wei = self.w3.eth.get_balance(Web3.to_checksum_address(address))
        balance_ether = Web3.from_wei(balance_wei, 'ether')
        logger.info(f"Balance of {address}: {balance_ether} ETH/Native")
        return balance_ether

    def send_native_token(self, recipient_address, amount_ether, gas_limit=21000, gas_price_gwei=None):
        """
        Sends native currency (e.g., ETH) to a recipient.
        amount_ether: Amount in Ether (or native token equivalent like BNB, MATIC).
        gas_price_gwei: Optional. If None, web3.py will estimate.
        """
        if not self.w3.is_connected():
            logger.error("Not connected to EVM RPC. Cannot send transaction.")
            return None

        try:
            recipient_checksum_address = Web3.to_checksum_address(recipient_address)
            nonce = self.w3.eth.get_transaction_count(self.sender_address)
            value_wei = Web3.to_wei(amount_ether, 'ether')

            tx_params = {
                'nonce': nonce,
                'to': recipient_checksum_address,
                'value': value_wei,
                'gas': gas_limit,
                'chainId': self.chain_id
            }

            if gas_price_gwei:
                tx_params['gasPrice'] = Web3.to_wei(gas_price_gwei, 'gwei')
            else:
                # Let web3.py estimate gas price. This can sometimes be slow or inaccurate.
                # For production, consider a more robust gas price strategy (e.g., external oracle)
                tx_params['gasPrice'] = self.w3.eth.gas_price
                logger.info(f"Estimated gas price: {Web3.from_wei(tx_params['gasPrice'], 'gwei')} Gwei")

            logger.info(f"Preparing to send {amount_ether} native token from {self.sender_address} to {recipient_checksum_address}")
            logger.debug(f"Transaction parameters: {tx_params}")

            signed_tx = self.w3.eth.account.sign_transaction(tx_params, self.sender_private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            logger.info(f"Transaction sent! Hash: {tx_hash.hex()}")
            logger.info(f"Waiting for transaction receipt (timeout 120s)...")
            
            # Wait for the transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120) # 120 seconds timeout
            
            if tx_receipt['status'] == 1:
                logger.info(f"Transaction successful! Block number: {tx_receipt['blockNumber']}, Gas used: {tx_receipt['gasUsed']}")
                return tx_receipt
            else:
                logger.error(f"Transaction failed! Receipt: {tx_receipt}")
                return None

        except Exception as e:
            logger.error(f"Error sending native token: {e}", exc_info=True)
            return None

# Example Usage (for testing directly, if needed)
if __name__ == '__main__':
    # THIS IS FOR LOCAL TESTING ONLY. DO NOT COMMIT REAL PRIVATE KEYS.
    # Ensure you have a .env file or set environment variables for these:
    # TEST_RPC_URL, TEST_SENDER_PRIVATE_KEY, TEST_RECIPIENT_ADDRESS
    import os
    from dotenv import load_dotenv
    load_dotenv()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    rpc_url = os.getenv("TEST_RPC_URL")
    private_key = os.getenv("TEST_SENDER_PRIVATE_KEY")
    recipient = os.getenv("TEST_RECIPIENT_ADDRESS")
    chain_id_env = os.getenv("TEST_CHAIN_ID")
    test_chain_id = int(chain_id_env) if chain_id_env else None


    if not all([rpc_url, private_key, recipient]):
        logger.error("Please set TEST_RPC_URL, TEST_SENDER_PRIVATE_KEY, and TEST_RECIPIENT_ADDRESS in your environment or .env file for testing blockchain_handler.py")
    else:
        try:
            logger.info("--- BlockchainHandler Test --- ")
            handler = BlockchainHandler(rpc_url, private_key, chain_id=test_chain_id)
            
            logger.info(f"Sender address: {handler.sender_address}")
            handler.get_balance()
            
            # Test sending a very small amount
            # MAKE SURE THE TEST RPC AND ACCOUNT ARE FOR TESTING PURPOSES ONLY (e.g., Sepolia, a local testnet)
            # Adjust amount as necessary, 0.0001 is just an example.
            test_amount = 0.0001 
            logger.info(f"Attempting to send {test_amount} native token to {recipient}...")
            
            # Example with specific gas price (optional, often good for testnets)
            # receipt = handler.send_native_token(recipient, test_amount, gas_price_gwei=10) 
            
            # Example letting web3.py estimate gas price
            receipt = handler.send_native_token(recipient, test_amount)

            if receipt:
                logger.info(f"Test transaction successful. Receipt: {receipt}")
            else:
                logger.error("Test transaction failed or timed out.")

        except ConnectionError as ce:
            logger.error(f"Connection error during test: {ce}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during blockchain_handler test: {e}", exc_info=True) 