import logging
import time
from src.config import load_configuration
from src.email_processor import EmailProcessor
from src.blockchain_handler import BlockchainHandler

# Configure basic logging
# TODO: Allow log level to be set from config
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 300 # Check for new emails every 5 minutes

def main():
    logger.info("Starting PayPal to EVM Bot...")
    
    blockchain_handler = None # Initialize
    config = None
    try:
        config = load_configuration()
        logger.setLevel(config.get("LOG_LEVEL", "INFO").upper())
        logger.info("Configuration loaded.")

        # Initialize BlockchainHandler if EVM config is present
        if config.get("EVM_RPC_URL") and config.get("SENDER_PRIVATE_KEY"):
            try:
                logger.info("EVM configuration found. Initializing BlockchainHandler...")
                blockchain_handler = BlockchainHandler(
                    rpc_url=config["EVM_RPC_URL"],
                    sender_private_key=config["SENDER_PRIVATE_KEY"],
                    chain_id=config.get("CHAIN_ID") 
                )
                logger.info(f"BlockchainHandler initialized. Sender Address: {blockchain_handler.sender_address}")
            except ConnectionError as ce:
                logger.error(f"BlockchainHandler Connection Error: {ce}. EVM features will be disabled.")
                blockchain_handler = None 
            except Exception as e_bc:
                logger.error(f"Error initializing BlockchainHandler: {e_bc}. EVM features will be disabled.", exc_info=True)
                blockchain_handler = None
        else:
            logger.warning("EVM_RPC_URL or SENDER_PRIVATE_KEY not configured. EVM transaction features will be disabled.")

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please ensure IMAP_SERVER, IMAP_USERNAME, and IMAP_PASSWORD are set.")
        logger.error("If using EVM features, also ensure EVM_RPC_URL and SENDER_PRIVATE_KEY are correctly set.")
        return
    except Exception as e_conf:
        logger.error(f"An unexpected error occurred during initial configuration: {e_conf}", exc_info=True)
        return
        
    if not config:
        logger.error("Configuration could not be loaded. Exiting.")
        return

    email_processor = EmailProcessor(
        imap_server=config["IMAP_SERVER"],
        imap_username=config["IMAP_USERNAME"],
        imap_password=config["IMAP_PASSWORD"]
    )

    if not email_processor.connect():
        logger.error("Failed to connect to IMAP server. Exiting.")
        return

    logger.info(f"Successfully connected to IMAP: {config.get('IMAP_SERVER', 'N/A')}. Bot is running...")
    logger.info(f"Will check for new emails from {config.get('PAYPAL_SENDER_EMAIL', 'N/A')} every {POLL_INTERVAL_SECONDS} seconds.")

    try:
        while True:
            logger.info("Checking for new PayPal emails...")
            paypal_emails = email_processor.fetch_paypal_emails(config["PAYPAL_SENDER_EMAIL"])
            
            if not paypal_emails:
                logger.info("No new PayPal emails found.")
            else:
                logger.info(f"Fetched {len(paypal_emails)} new PayPal email(s) to process.")
                for email_msg in paypal_emails:
                    logger.info(f"--- Processing Email --- UID: {email_msg.uid} Subject: {email_msg.subject}")
                    parsed_details = email_processor.parse_email_details(email_msg)
                    
                    if parsed_details and \
                       parsed_details.get("transaction_id") and \
                       parsed_details.get("amount") and \
                       parsed_details.get("transaction_type") == "received":
                        
                        logger.info("Successfully parsed PayPal email (received payment):")
                        logger.info(f"  Transaction ID: {parsed_details.get('transaction_id')}")
                        logger.info(f"  Amount: {parsed_details.get('amount')} {parsed_details.get('currency')}")
                        logger.info(f"  From: {parsed_details.get('counterparty_name')}")
                        
                        if blockchain_handler and parsed_details.get("amount", 0) > 0:
                            target_address = config.get("MOCKUP_RECIPIENT_ADDRESS")
                            amount_to_send = parsed_details.get("amount") # This is float
                            
                            # Currency check - very basic, assuming native token transaction for now
                            # A real system would need robust currency conversion if PayPal currency isn't the chain's native one.
                            if parsed_details.get("currency") not in ["ETH", "BNB", "MATIC"]: # Add other native token symbols as needed
                                logger.warning(f"Parsed currency {parsed_details.get('currency')} may not be the chain's native token. Attempting to send {amount_to_send} as native token. Implement proper conversion if needed.")
                            
                            gas_limit = config.get("GAS_LIMIT", 21000)
                            raw_gas_price = config.get("GAS_PRICE_GWEI")
                            gas_price_gwei = float(raw_gas_price) if raw_gas_price and raw_gas_price.lower() != 'auto' else None

                            logger.info(f"Attempting EVM transaction: Send {amount_to_send} (parsed from email) to {target_address}")
                            try:
                                receipt = blockchain_handler.send_native_token(
                                    recipient_address=target_address,
                                    amount_ether=float(amount_to_send), # Ensure it's float
                                    gas_limit=int(gas_limit),
                                    gas_price_gwei=gas_price_gwei
                                )
                                if receipt and receipt.get('status') == 1:
                                    logger.info(f"EVM Transaction successful for PayPal TX ID {parsed_details.get('transaction_id')}. EVM TX Hash: {receipt.transactionHash.hex()}")
                                elif receipt:
                                    logger.error(f"EVM Transaction failed (status 0) for PayPal TX ID {parsed_details.get('transaction_id')}. Receipt: {receipt}")
                                else:
                                    logger.error(f"EVM Transaction did not return a receipt or failed for PayPal TX ID {parsed_details.get('transaction_id')}.")
                            except Exception as e_tx:
                                logger.error(f"Exception during EVM transaction for PayPal TX ID {parsed_details.get('transaction_id')}: {e_tx}", exc_info=True)
                        elif not blockchain_handler:
                            logger.warning("BlockchainHandler not initialized or failed to initialize. Skipping EVM transaction.")
                        elif parsed_details.get("amount", 0) <= 0:
                            logger.warning(f"Parsed amount is zero or negative ({parsed_details.get('amount')}). Skipping EVM transaction.")

                    elif parsed_details and parsed_details.get("transaction_type") == "sent":
                        logger.info("Parsed a 'sent' PayPal email. No action taken for this type.")
                    elif parsed_details:
                        logger.warning(f"Email parsed but did not meet criteria for EVM trigger or was not fully parsed: UID {email_msg.uid}")
                    else:
                        logger.warning(f"Could not parse details for email UID: {email_msg.uid}. Subject: {email_msg.subject}")
            
            logger.info(f"Waiting for {POLL_INTERVAL_SECONDS} seconds before next check...")
            time.sleep(POLL_INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        logger.info("Bot manually interrupted. Shutting down...")
    except Exception as e_main_loop:
        logger.error(f"An unexpected error occurred in the main loop: {e_main_loop}", exc_info=True)
    finally:
        if email_processor: # Check if email_processor was initialized
            logger.info("Logging out from IMAP server...")
            email_processor.logout()
        logger.info("PayPal to EVM Bot shut down.")

if __name__ == "__main__":
    main() 