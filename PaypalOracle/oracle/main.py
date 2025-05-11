#!/usr/bin/env python3

from src.PaypalOracle import PaypalOracle
from src.RoflUtility import RoflUtility
import argparse
# Added imports
import json
import os
# import re # re is imported in MailProvider.py, not directly needed here unless MailProvider changes
from dotenv import load_dotenv
from web3 import Web3
from src.MailProvider import MailProvider # Ensure this path is correct and MailProvider.py is in src

# --- New function for PayPal email processing and escrow interaction ---
def handle_paypal_escrow_process():
    print("\nStarting PayPal email processing and escrow contract interaction...")
    load_dotenv() # Loads variables from .env file into environment

    # Configuration for the email and escrow process
    imap_server = os.getenv("IMAP_SERVER")
    imap_username = os.getenv("IMAP_USERNAME")
    imap_password = os.getenv("IMAP_PASSWORD")
    private_key = os.getenv("PRIVATE_KEY")
    
    # Constructing path to Escrow.json, assuming main.py is at the project root
    # and Escrow.json is in the 'src' subdirectory.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    escrow_json_path = os.path.join(current_dir, "src", "Escrow.json")

    try:
        with open(escrow_json_path) as f:
            abi = json.load(f)['abi']
    except FileNotFoundError:
        print(f"Error: Escrow.json not found at {escrow_json_path}. Skipping PayPal escrow process.")
        return
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error reading ABI from Escrow.json ({escrow_json_path}): {e}. Skipping PayPal escrow process.")
        return

    if not all([imap_server, imap_username, imap_password]):
        print("IMAP server credentials (IMAP_SERVER, IMAP_USERNAME, IMAP_PASSWORD) not fully configured in .env. Skipping PayPal escrow process.")
        return
    if not private_key:
        print("PRIVATE_KEY not configured in .env. Skipping PayPal escrow process.")
        return

    mail_provider = MailProvider(imap_server, imap_username, imap_password)
    if not mail_provider.connect(): # connect() should return True on success, False on failure
        print("Failed to connect to mail provider. Skipping PayPal escrow process.")
        return

    paypal_sender_email = "service@paypal.fr" # As per your original script
    print(f"Fetching PayPal emails from {paypal_sender_email}...")
    email_data = mail_provider.fetch_paypal_emails(paypal_sender_email)

    if not email_data:
        print("No new PayPal emails found or an error occurred during fetch. PayPal escrow process complete.")
        return

    # Web3 setup - details from your original script
    web3_provider_url = "https://testnet.sapphire.oasis.io"
    w3 = Web3(Web3.HTTPProvider(web3_provider_url))

    if not w3.is_connected():
        print(f"Failed to connect to Web3 provider at {web3_provider_url}. Skipping transactions.")
        return
        
    sender_address = w3.eth.account.from_key(private_key).address
    # Escrow contract address from your original script
    escrow_contract_address = "0x50222E3513d8e4Ae8EC9B965979994364a10200F" 
    contract = w3.eth.contract(address=escrow_contract_address, abi=abi)

    print(f"Processing {len(email_data)} PayPal transactions for escrow contract {escrow_contract_address}...")

    for name, amount_str in email_data:
        try:
            # The MailProvider already does .replace(" ", "").replace(",", ".")
            amount_float = float(amount_str) 
            formatted_amount = int(amount_float * (10**6)) # Example: 6 decimals for EUR
            
            nonce = w3.eth.get_transaction_count(sender_address)
            
            tx_params = {
                "from": sender_address,
                "nonce": nonce,
                'gas': 100_000,  # Consider making this configurable via .env
                'gasPrice': w3.to_wei(500, 'gwei'), # Consider making this configurable via .env
                'chainId': 23295  # Sapphire Testnet Chain ID. Make configurable if using other networks.
            }

            print(f"  - Preparing transaction for: Name='{name}', Amount={amount_float} EUR ({formatted_amount} units)")
            transaction = contract.functions.proofOfPaiement(name, formatted_amount).build_transaction(tx_params)
            
            signed_tx = w3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            print(f"    Transaction sent. Hash: {tx_hash.hex()}")
            
            # Optional: wait for transaction receipt
            # print(f"    Waiting for confirmation for tx: {tx_hash.hex()}...")
            # receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180) # e.g., 180s timeout
            # print(f"    Transaction confirmed. Block: {receipt.blockNumber}")

        except ValueError as ve:
            print(f"    Error converting amount '{amount_str}' for '{name}' to float: {ve}")
        except Exception as e:
            # Consider more specific error handling for Web3/RPC errors
            print(f"    Error processing transaction for '{name}', amount '{amount_str}': {type(e).__name__} - {e}")
    
    print("PayPal email processing and escrow contract interaction finished.")
# --- End of new function ---

def main():
    """
    Main method for the Python CLI tool.

    :return: None
    """
    parser = argparse.ArgumentParser(description="A Python CLI tool for compiling, deploying, and interacting with smart contracts.")

    parser.add_argument(
        "contract_address",
        type=str,
        help="Address of the smart contract to interact with"
    )

    parser.add_argument(
        "--network",
        help="Chain name to connect to "
             "(sapphire, sapphire-testnet, sapphire-localnet)",
        default="sapphire-localnet",
    )

    parser.add_argument(
        "--kms",
        help="Override ROFL's appd service URL",
        default="",
    )

    parser.add_argument(
        "--key-id",
        help="Override the oracle's secret key ID on KMS",
        default="paypal-oracle",
    )

    parser.add_argument(
        "--secret",
        help="Secret key of the oracle account (only for testing)",
        required=False,
    )

    arguments = parser.parse_args()

    print(f"Starting ChatBot Oracle service. Using contract {arguments.contract_address} on {arguments.network}.")
    rofl_utility = RoflUtility(arguments.kms)

    secret = arguments.secret
    if secret == None:
        secret = rofl_utility.fetch_key(arguments.key_id)

    paypalOracle = PaypalOracle(arguments.contract_address, arguments.network, rofl_utility, secret)
    paypalOracle.run()

    # --- Call the new PayPal escrow processing function --- 
    # This will run after the PaypalOracle service logic.
    # It uses its own configuration from .env and hardcoded values from your original script.
    handle_paypal_escrow_process()
    # --- End of call ---

if __name__ == '__main__':
    main()