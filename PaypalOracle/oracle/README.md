# Oasis Oracle and PayPal Escrow Processor

this part of the project has big portions taken from: https://github.com/oasisprotocol/demo-rofl-chatbot

This project provides a versatile oracle service for Oasis Sapphire environments and includes a specialized feature for processing PayPal payment emails to interact with an Escrow smart contract.

## 1. Installation

Install the required Python dependencies:

```shell
pip install -r requirements.txt
```
Or using the Makefile:
```shell
make install
```

## 2. Configuration

The application uses functionalities that require different types of configuration:

### a. Contract ABI

The primary smart contract interactions (both for the generic oracle and the PayPal escrow process) use the ABI defined in:
*   `src/Escrow.json`

Make sure this file is present and correctly defines the ABI for your Escrow contract.

### b. PayPal Email Escrow Service (`.env` file)

The PayPal email processing feature requires specific credentials and settings to be provided via a `.env` file in the project root. Create a `.env` file with the following variables:

```env
IMAP_SERVER=your_imap_server.com
IMAP_USERNAME=your_email@example.com
IMAP_PASSWORD=your_email_password
PRIVATE_KEY=0xyour_ethereum_private_key_for_escrow_transactions
# Optional: You can add other configurations if needed by your setup
```

**Note on PayPal Escrow Contract:** The `main.py` script currently has the Escrow contract address (`0x50222E3513d8e4Ae8EC9B965979994364a10200F`) and the Web3 provider URL (`https://testnet.sapphire.oasis.io`) for the PayPal escrow processing hardcoded. You may need to modify `main.py` if you use a different contract or network for this feature.

## 3. Running the Application

The main entry point is `main.py`. Executing this script will:
1.  Start the `PaypalOracle` service, which can listen to contract events and submit answers.
2.  Subsequently, run the `handle_paypal_escrow_process` function, which connects to an IMAP server, fetches PayPal emails, and interacts with the configured Escrow contract.

### Command-Line Usage:

**For Mainnet/Testnet (using ROFL App's Key Management Service - KMS):**

Provide the address of your deployed oracle-compatible contract:

```shell
./main.py <YOUR_ORACLE_CONTRACT_ADDRESS> --network <NETWORK_NAME>
```
Example:
```shell
./main.py 0x123...def --network sapphire-testnet
```

**For Localnet (or providing the secret key directly):**

Provide your oracle's private key (hex format) and the contract address:

```shell
./main.py --secret <YOUR_HEX_PRIVATE_KEY> <YOUR_ORACLE_CONTRACT_ADDRESS> --network sapphire-localnet
```
Example:
```shell
./main.py --secret 0xac09...ff80 0xabc...789 --network sapphire-localnet
```

**Available Arguments for `main.py`:**
*   `contract_address`: (Required) Address of the smart contract for the `PaypalOracle` service.
*   `--network`: Chain name to connect to (e.g., `sapphire`, `sapphire-testnet`, `sapphire-localnet`). Defaults to `sapphire-localnet`.
*   `--secret`: Secret key of the oracle account (mostly for local testing). If not provided, the system will attempt to fetch it using the KMS via `RoflUtility`.
*   `--kms`: Override ROFL's appd service URL for key fetching.
*   `--key-id`: Override the oracle's secret key ID on KMS (default: `paypal-oracle`).

The PayPal escrow processing will run automatically after the oracle service initializes, using the configuration from the `.env` file and hardcoded values in `main.py` for its specific contract interactions.

## 4. Development

### Makefile Targets

The project includes a `Makefile` with common development commands:

*   `make install`: Install dependencies.
*   `make test`: Run tests located in the `tests/` directory.
*   `make lint`: Lint the codebase using `flake8`.
*   `make check`: Run both linting and tests.
*   `make run-localnet`: Starts a local Sapphire development node using Docker. This can be used as the target network for `./main.py ... --network sapphire-localnet`.

**Note on Makefile `run` target**: The `Makefile` contains a `run: $(PYTHON) src/main.py` target. This path to `main.py` is incorrect as `main.py` is in the root directory. To run the application, directly use `./main.py` as described above or correct the Makefile target to `run: $(PYTHON) main.py`.

