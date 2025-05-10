# PayPal Email to EVM Transaction Bot

This project implements a bot that monitors an email inbox for PayPal transaction notifications, parses them to extract transaction details (ID, amount), and (as a bonus feature) can trigger a corresponding transaction on an EVM-compatible blockchain.

## Features

- Connects to an IMAP email server.
- Fetches emails from a specified PayPal sender address.
- Parses email content to find transaction ID and amount (currently placeholder, requires PayPal EML examples for accurate parsing).
- Basic logging implemented.
- (Planned) EVM blockchain transaction capabilities.
- (Planned) Dockerization for deployment.

## Project Structure

```
paypal_mail_to_evm_bot/
├── main.py               # Main application script
├── requirements.txt      # Python dependencies
├── CHANGELOG.md          # Tracks changes to the project
├── Dockerfile            # For building the Docker image
├── README.md             # This file
├── anonymized_received_payment.eml # Example anonymized EML for testing
├── anonymized_sent_payment.eml     # Example anonymized EML for testing
└── src/
    ├── __init__.py
    ├── config.py         # Handles configuration and environment variables
    ├── email_processor.py  # Logic for fetching and parsing emails
    └── blockchain_handler.py # Logic for EVM blockchain interactions (NEW)
```

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd paypal_mail_to_evm_bot
    ```

2.  **Create a Python virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    Create a `.env` file in the `paypal_mail_to_evm_bot` directory by copying and modifying the example below. **Do not commit your `.env` file to version control if it contains sensitive credentials.**

    **Example `.env` file content:**
    ```env
    # Email Configuration
    IMAP_SERVER="imap.example.com"
    IMAP_USERNAME="your_email@example.com"
    IMAP_PASSWORD="your_email_password"
    PAYPAL_SENDER_EMAIL="service@paypal.com" # Or the specific PayPal email address you want to monitor

    # Blockchain Configuration (Required for EVM transaction feature)
    EVM_RPC_URL="https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID" # Example for Sepolia testnet
    SENDER_PRIVATE_KEY="your_wallet_private_key_for_sending_transactions" # WARNING: Handle with extreme care!
    MOCKUP_RECIPIENT_ADDRESS="0x1234567890123456789012345678901234567890" # Destination address for EVM transactions
    CHAIN_ID="11155111" # Optional: e.g., 1 for ETH Mainnet, 5 for Goerli, 11155111 for Sepolia. If not set, will try to get from RPC.
    GAS_LIMIT="21000" # Default for native token transfers. Adjust if needed (e.g., for contract interactions).
    GAS_PRICE_GWEI="" # Optional: Specify a gas price in Gwei (e.g., "5"). If empty or "auto", it will be estimated (can be slow/unreliable).

    # Logging Configuration
    LOG_LEVEL="INFO" # DEBUG, INFO, WARNING, ERROR
    ```
    **Important Security Notes for `.env`:**
    *   `SENDER_PRIVATE_KEY` grants control over your wallet. Keep it secret and secure. Consider using a separate, dedicated wallet for this bot with limited funds.
    *   Ensure your `EVM_RPC_URL` is for the correct network (mainnet or testnet) that corresponds to your `SENDER_PRIVATE_KEY` and intended operations.

## Usage

1.  **Run the bot:**
    ```bash
    python main.py
    ```
    The bot will connect to the IMAP server and start polling for new emails from the specified PayPal sender address.

2.  **Testing Email Parsing (without live IMAP):**
    You can test the email parsing logic using the provided anonymized EML files:
    ```bash
    python src/email_processor.py
    ```
    This will attempt to parse `anonymized_received_payment.eml` and `anonymized_sent_payment.eml` located in the `paypal_mail_to_evm_bot` directory.

3.  **Testing Blockchain Handler (without full bot):**
    You can test the blockchain sending functionality directly (requires testnet RPC and a funded test private key):
    Create/update your `.env` with `TEST_RPC_URL`, `TEST_SENDER_PRIVATE_KEY`, `TEST_RECIPIENT_ADDRESS`, and optionally `TEST_CHAIN_ID`.
    ```bash
    python src/blockchain_handler.py
    ```

## Dockerization (Planned)

A `Dockerfile` is provided to containerize the application. 

1.  **Build the Docker image:**
    ```bash
    docker build -t paypal-evm-bot .
    ```

2.  **Run the Docker container:**
    You'll need to pass the environment variables to the container. One way is using an environment file:
    ```bash
    docker run --env-file ./.env paypal-evm-bot
    ```
    (Ensure your `.env` file is correctly set up as described above.)

## Development

-   Follow the setup instructions.
-   The bot uses standard Python logging. Check the console output for activity and errors.
-   The main loop is in `main.py`.
-   Email fetching/parsing logic is in `src/email_processor.py`.
-   EVM blockchain logic is in `src/blockchain_handler.py`.

## Contributing

(Placeholder for contribution guidelines)

## License

(Placeholder for license information - e.g., MIT) 