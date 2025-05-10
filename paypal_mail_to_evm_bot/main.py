import json
import os
import re

from imap_tools import MailBox, AND
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

class MailProvider:
    def __init__(self, imap_server, imap_username, imap_password):
        self.imap_server = imap_server
        self.imap_username = imap_username
        self.imap_password = imap_password
        self.mailbox = None
    
    def connect(self):
        """Connects to the IMAP server."""
        try:
            print(self.imap_server, self.imap_username, self.imap_password)
            self.mailbox = MailBox(self.imap_server)
            self.mailbox.login(self.imap_username, self.imap_password)
            print(f"Successfully connected to IMAP server: {self.imap_server} as {self.imap_username}")
            return True
        except Exception as e:
            print(f"Failed to connect to IMAP server: {e}")
            return False

    def fetch_paypal_emails(self, paypal_sender_email, mark_seen_after_fetch=True):
        """Fetches unseen emails from the specified PayPal sender address and optionally marks them as seen."""
        if not self.mailbox:
            print("Not connected to mailbox. Call connect() first.")
            return []
        
        emails_fetched = []
        try:
            self.mailbox.folder.set('INBOX')
            print(f"Fetching unseen emails from {paypal_sender_email}...")
            
            # Fetch UIDs of unseen emails first
            for mail in self.mailbox.fetch(AND(subject="Tr: Vous avez envoy")):
                body = mail.text or mail.html or ''
                match = re.search(r"Vous avez envoyé\s+([\d\s,.]+)\s*€\s*EUR\s+à\s+(.+?)\.", body)
                if match:
                    amount = match.group(1).replace(" ", "").replace(",", ".")
                    name = match.group(2).strip()
                    print("Name:", name, " - Amount:", amount)
                    emails_fetched.append([name, amount])

            return emails_fetched
        except Exception as e:
            print(f"Error fetching PayPal emails: {e}", exc_info=True)
            return []


with open("Escrow.json") as f:
    abi = json.load(f)['abi']

if __name__ == "__main__":

    provider = MailProvider(
        os.getenv("IMAP_SERVER"),
        os.getenv("IMAP_USERNAME"),
        os.getenv("IMAP_PASSWORD")
    )
    provider.connect()
    handles = provider.fetch_paypal_emails("service@paypal.fr")

    w3 = Web3(Web3.HTTPProvider("https://testnet.sapphire.oasis.io"))

    private_key = os.getenv("PRIVATE_KEY")
    sender_address = w3.eth.account.from_key(private_key).address
    nonce = w3.eth.get_transaction_count(sender_address)

    contract_address = "0x50222E3513d8e4Ae8EC9B965979994364a10200F"
    contract = w3.eth.contract(address=contract_address, abi=abi)

    for name, amount in handles:
        formatted_amount = int(float(amount) * (10 ** 6))
        tx = contract.functions.proofOfPaiement(name, formatted_amount).build_transaction({
            "from": sender_address,
            "nonce": w3.eth.get_transaction_count(sender_address),
            'gas': 100_000,
            'gasPrice': w3.to_wei(500, 'gwei'),
            'chainId': 23295
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)



    
