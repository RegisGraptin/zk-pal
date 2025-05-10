import os
from dotenv import load_dotenv

def load_configuration():
    """Loads environment variables from .env file and returns them as a dictionary."""
    load_dotenv()
    config = {
        "IMAP_SERVER": os.getenv("IMAP_SERVER"),
        "IMAP_USERNAME": os.getenv("IMAP_USERNAME"),
        "IMAP_PASSWORD": os.getenv("IMAP_PASSWORD"),
        "PAYPAL_SENDER_EMAIL": os.getenv("PAYPAL_SENDER_EMAIL", "service@paypal.com"),
        
        # Blockchain related
        "EVM_RPC_URL": os.getenv("EVM_RPC_URL"),
        "SENDER_PRIVATE_KEY": os.getenv("SENDER_PRIVATE_KEY"),
        "MOCKUP_RECIPIENT_ADDRESS": os.getenv("MOCKUP_RECIPIENT_ADDRESS", "0x1234567890123456789012345678901234567890"), # Default mock address
        "CHAIN_ID": os.getenv("CHAIN_ID"), # Optional: e.g., 1 for Ethereum Mainnet, 5 for Goerli, 11155111 for Sepolia.
        "GAS_LIMIT": os.getenv("GAS_LIMIT", "21000"), # Default for native token transfer
        "GAS_PRICE_GWEI": os.getenv("GAS_PRICE_GWEI"), # Optional: e.g., "5", "auto"

        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO").upper()
    }

    # Basic validation for essential email credentials
    if not all([config["IMAP_SERVER"], config["IMAP_USERNAME"], config["IMAP_PASSWORD"]]):
        raise ValueError("IMAP_SERVER, IMAP_USERNAME, and IMAP_PASSWORD must be set.")
    
    # Basic validation for essential EVM credentials if EVM_RPC_URL is provided (indicating intent to use EVM features)
    if config["EVM_RPC_URL"] and not config["SENDER_PRIVATE_KEY"]:
        raise ValueError("SENDER_PRIVATE_KEY must be set if EVM_RPC_URL is provided.")

    # Convert CHAIN_ID to int if present, otherwise keep as None
    if config["CHAIN_ID"]:
        try:
            config["CHAIN_ID"] = int(config["CHAIN_ID"])
        except ValueError:
            raise ValueError("CHAIN_ID must be an integer if provided.")

    # Convert GAS_LIMIT to int
    try:
        config["GAS_LIMIT"] = int(config["GAS_LIMIT"])
    except ValueError:
        raise ValueError("GAS_LIMIT must be an integer.")

    return config

if __name__ == '__main__':
    # For testing purposes, print loaded config
    try:
        settings = load_configuration()
        print("Configuration loaded successfully:")
        for key, value in settings.items():
            print(f"{key}: {value if key != 'IMAP_PASSWORD' and key != 'SENDER_PRIVATE_KEY' else '********'}")
    except ValueError as e:
        print(f"Error loading configuration: {e}") 