import logging
from imap_tools import MailBox, AND, MailMessageFlags
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class EmailProcessor:
    def __init__(self, imap_server, imap_username, imap_password):
        self.imap_server = imap_server
        self.imap_username = imap_username
        self.imap_password = imap_password
        self.mailbox = None

    def connect(self):
        """Connects to the IMAP server."""
        try:
            self.mailbox = MailBox(self.imap_server)
            self.mailbox.login(self.imap_username, self.imap_password)
            logger.info(f"Successfully connected to IMAP server: {self.imap_server} as {self.imap_username}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {e}")
            return False

    def fetch_paypal_emails(self, paypal_sender_email, mark_seen_after_fetch=True):
        """Fetches unseen emails from the specified PayPal sender address and optionally marks them as seen."""
        if not self.mailbox:
            logger.error("Not connected to mailbox. Call connect() first.")
            return []
        
        emails_fetched = []
        try:
            self.mailbox.folder.set('INBOX')
            logger.info(f"Fetching unseen emails from {paypal_sender_email}...")
            
            # Fetch UIDs of unseen emails first
            unseen_mail_uids = self.mailbox.uids(AND(from_=paypal_sender_email, seen=False))

            if unseen_mail_uids:
                logger.info(f"Found {len(unseen_mail_uids)} unseen email(s) from {paypal_sender_email}.")
                # Fetch the actual email messages for these UIDs
                for msg in self.mailbox.fetch(AND(uid=unseen_mail_uids), mark_seen=False): # Fetch without marking seen initially
                    logger.info(f"Processing email: UID {msg.uid} - Subject: {msg.subject}")
                    emails_fetched.append(msg)
                
                if mark_seen_after_fetch:
                    logger.info(f"Marking {len(unseen_mail_uids)} fetched emails as seen: {unseen_mail_uids}")
                    self.mailbox.flag(unseen_mail_uids, MailMessageFlags.SEEN, True)
            else:
                logger.info(f"No new unseen emails found from {paypal_sender_email}.")
                # Fallback for development: fetch a few recent (potentially seen) emails if no unseen ones
                # This part is mainly for easier testing during development.
                # In production, you might only want to process unseen emails.
                logger.debug(f"DEV MODE: No unseen emails. Fetching up to 5 recent emails from {paypal_sender_email} for testing purposes.")
                all_paypal_mail_uids = self.mailbox.uids(AND(from_=paypal_sender_email))
                if all_paypal_mail_uids:
                    limit = 5
                    ids_to_fetch = all_paypal_mail_uids[-limit:]
                    logger.debug(f"DEV MODE: Fetching UIDs: {ids_to_fetch}")
                    for msg in self.mailbox.fetch(AND(uid=ids_to_fetch), mark_seen=False):
                        logger.debug(f"DEV MODE: Processing recent email (UID {msg.uid} - Subject: {msg.subject})")
                        # Avoid adding duplicates if an email was fetched in a previous dev run and is now seen
                        if not any(fetched_msg.uid == msg.uid for fetched_msg in emails_fetched):
                            emails_fetched.append(msg)
            
            return emails_fetched
        except Exception as e:
            logger.error(f"Error fetching PayPal emails: {e}", exc_info=True)
            return [] # Return empty list on error

    def parse_email_details(self, email_message):
        """
        Parses the email message to extract transaction ID, amount, currency,
        sender (for received) or recipient (for sent).
        Returns a dictionary with extracted details or None if parsing fails.
        """
        if not email_message.html:
            logger.warning(f"Email UID {email_message.uid} has no HTML content. Skipping parsing.")
            return None

        soup = BeautifulSoup(email_message.html, 'html.parser')
        details = {
            "uid": email_message.uid,
            "subject": email_message.subject,
            "transaction_id": None,
            "amount": None,
            "currency": None,
            "transaction_type": None, # "sent" or "received"
            "counterparty_name": None, # Sender if received, Recipient if sent
            "raw_html_for_debug": None # email_message.html # Optional: for debugging
        }

        try:
            subject = email_message.subject.lower()
            
            # --- Common parsing for Transaction ID ---
            # Look for links containing "transaction/details/"
            transaction_link = soup.find('a', href=re.compile(r"transaction/details/([^?]+)"))
            if transaction_link:
                match = re.search(r"transaction/details/([^?]+)", transaction_link['href'])
                if match:
                    details["transaction_id"] = match.group(1)
                    logger.info(f"Extracted Transaction ID: {details['transaction_id']} from link.")
            
            # Fallback for Transaction ID if not in link, try to find it in text
            if not details["transaction_id"]:
                # Example: "Numéro de transaction</strong></span><br /><span>TRANSACTION_ID</span>"
                # Or: "Transaction ID</strong></span><br /><span>TRANSACTION_ID</span>"
                tid_label = soup.find('strong', string=re.compile(r"Numéro de transaction|Transaction ID", re.IGNORECASE))
                if tid_label and tid_label.parent and tid_label.parent.find_next_sibling('span'):
                    details["transaction_id"] = tid_label.parent.find_next_sibling('span').text.strip()
                    logger.info(f"Extracted Transaction ID: {details['transaction_id']} from text label.")
                elif tid_label and tid_label.find_next('a'): # Sometimes it's directly in a link after the label
                     details["transaction_id"] = tid_label.find_next('a').text.strip()
                     logger.info(f"Extracted Transaction ID: {details['transaction_id']} from linked text label.")


            # --- Type specific parsing (Sent vs Received) ---
            # Heuristic: Subject line often indicates type
            if "vous avez envoyé un paiement" in subject or "you sent a payment" in subject:
                details["transaction_type"] = "sent"
                # Extract Amount and Currency for sent email
                # Example: "Vous avez envoyé un paiement de 20,00  EUR à Recipient Name."
                # Or from table: "<span>Montant envoyé</span></td> <td ...><span>-20,00  EUR</span>"
                
                amount_text_node = soup.find(lambda tag: tag.name == 'p' and "vous a envoyé" in tag.text.lower() and "eur" in tag.text.lower())
                if not amount_text_node: # Try another common pattern
                    amount_td_label = soup.find('td', string=re.compile(r"Montant envoy(é|e)", re.IGNORECASE))
                    if amount_td_label and amount_td_label.find_next_sibling('td'):
                         amount_text_node = amount_td_label.find_next_sibling('td').find('span')


                if amount_text_node:
                    raw_amount_text = amount_text_node.text.strip()
                    logger.debug(f"Raw amount text for 'sent' email (subject/td): {raw_amount_text}")
                    # Regex to capture amount and currency: e.g., "20,00 EUR" or "-20,00 EUR"
                    match = re.search(r"([-]?\d{1,3}(?:\.\d{3})*,\d{2})\s*([A-Z]{3})", raw_amount_text.replace('\\xa0', ' ')) # Use \xa0 for non-breaking space
                    if match:
                        details["amount"] = float(match.group(1).replace('.', '').replace(',', '.')) # Normalize to float
                        details["currency"] = match.group(2)
                        logger.info(f"Extracted Amount: {details['amount']}, Currency: {details['currency']} (sent)")
                
                # Extract Recipient Name for sent email
                # From subject: "à Recipient Name."
                subject_recipient_match = re.search(r"(?:à|to)\s+([^.]+)\.?$", email_message.subject, re.IGNORECASE) # Gets name at end of subject
                if subject_recipient_match:
                    details["counterparty_name"] = subject_recipient_match.group(1).strip()
                    logger.info(f"Extracted Recipient Name (from subject): {details['counterparty_name']}")
                else: # Fallback: try to find it in the main header
                    header_recipient_match = soup.find('p', style=lambda s: s and 'font-size:32px' in s.lower())
                    if header_recipient_match:
                        # "Vous avez envoyé un paiement de AMOUNT CURRENCY à RECIPIENT_NAME."
                        text_content = header_recipient_match.get_text(separator=' ', strip=True)
                        match = re.search(r"(?:à|to)\s+([^.]+)\.?$", text_content, re.IGNORECASE)
                        if match:
                             details["counterparty_name"] = match.group(1).strip()
                             logger.info(f"Extracted Recipient Name (from header): {details['counterparty_name']}")


            elif "has sent you money" in subject or "vous a envoyé de l'argent" in subject : # Check both English and French
                details["transaction_type"] = "received"
                # Extract Amount and Currency for received email
                # Example: "Sender Company Name vous a envoyé 100,00 EUR."
                # Or from table: "<span>Argent reçu</span></td> <td ...><span>100,00  EUR</span>"

                amount_text_node = None
                # Try the main header first
                header_amount_match = soup.find('p', style=lambda s: s and 'font-size:32px' in s.lower())
                if header_amount_match:
                    amount_text_node = header_amount_match

                if not amount_text_node: # Try table cell as fallback
                    amount_td_label = soup.find('td', string=re.compile(r"Argent re(ç|c)u|Money received", re.IGNORECASE))
                    if amount_td_label and amount_td_label.find_next_sibling('td'):
                        amount_text_node = amount_td_label.find_next_sibling('td').find('span')
                
                if amount_text_node:
                    raw_amount_text = amount_text_node.text.strip().replace('\\xa0', ' ') # Normalize non-breaking space
                    logger.debug(f"Raw amount text for 'received' email (header/td): {raw_amount_text}")
                    match = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2})\s*([A-Z]{3})", raw_amount_text)
                    if match:
                        details["amount"] = float(match.group(1).replace('.', '').replace(',', '.'))
                        details["currency"] = match.group(2)
                        logger.info(f"Extracted Amount: {details['amount']}, Currency: {details['currency']} (received)")

                # Extract Sender Name for received email
                # From subject: "Sender Company Name has sent you money"
                # Or: "Sender Company Name vous a envoyé..."
                subject_sender_match = re.match(r"(.+?)\s+(?:has sent you money|vous a envoyé)", email_message.subject, re.IGNORECASE)
                if subject_sender_match:
                    details["counterparty_name"] = subject_sender_match.group(1).strip()
                    logger.info(f"Extracted Sender Name (from subject): {details['counterparty_name']}")
                elif header_amount_match: # Fallback to header if subject parsing failed
                    text_content = header_amount_match.get_text(separator=' ', strip=True)
                    # "SENDER_NAME vous a envoyé AMOUNT CURRENCY."
                    match = re.match(r"(.+?)\s+(?:vous a envoyé|has sent you)", text_content, re.IGNORECASE)
                    if match:
                        details["counterparty_name"] = match.group(1).strip()
                        logger.info(f"Extracted Sender Name (from header): {details['counterparty_name']}")
            else:
                logger.warning(f"Email UID {email_message.uid} - Subject '{email_message.subject}' does not match known PayPal transaction types.")
                return None # Or a partial details dict if some info was found


            # Final check if essential details are missing
            if not all([details["transaction_id"], details["amount"], details["currency"], details["transaction_type"], details["counterparty_name"]]):
                logger.warning(f"Could not parse all required details for email UID {email_message.uid}. Parsed: {details}")
                # Potentially return None or partial data depending on strictness
                # For now, let's return what we have, main.py can filter
            
            logger.info(f"Successfully parsed email UID {email_message.uid}: {details}")
            return details

        except Exception as e:
            logger.error(f"Error parsing email UID {email_message.uid} - Subject: {email_message.subject}. Error: {e}", exc_info=True)
            # Optionally, store raw HTML for failed parsing for later analysis
            # details["raw_html_for_debug"] = email_message.html 
            return details # Return partial details for debugging, or None

    def logout(self):
        """Logs out from the IMAP server."""
        if self.mailbox:
            try:
                self.mailbox.logout()
                logger.info("Successfully logged out from IMAP server.")
            except Exception as e:
                logger.error(f"Error logging out from IMAP server: {e}")
        self.mailbox = None

if __name__ == '__main__':
    # This is a basic test block.
    # You would need to set up a .env file with your IMAP credentials
    # and have some PayPal emails in your inbox for this to work.
    
    from src.config import load_configuration
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logger.info("EmailProcessor direct execution for testing.")

    try:
        config = load_configuration()
        if not all([config.get("IMAP_SERVER"), config.get("IMAP_USERNAME"), config.get("IMAP_PASSWORD")]):
            logger.error("IMAP credentials not found in config. Skipping live test.")
            # Attempt to parse local anonymized EML files instead for testing parsing logic
            
            processor = EmailProcessor("dummy_server", "dummy_user", "dummy_pass") # Dummy for local parsing

            test_files = {
                "anonymized_received_payment.eml": "received",
                "anonymized_sent_payment.eml": "sent"
            }
            
            class MockEmailMessage:
                def __init__(self, uid, subject, html_content):
                    self.uid = uid
                    self.subject = subject
                    self.html = html_content
                    self.text = "" # Not used by current parser but good to have
            
            for filename, type_hint in test_files.items():
                try:
                    with open(f"./{filename}", 'r', encoding='utf-8') as f: # Assuming files are in the same dir or adjust path
                        logger.info(f"--- Parsing local file: {filename} (expected type: {type_hint}) ---")
                        eml_content = f.read()
                        
                        # Basic EML parsing to get subject and HTML body
                        # This is a simplified way to get HTML for testing; real EML parsing can be more complex
                        # For this test, we assume the .eml file content *is* the HTML part or easily extractable
                        
                        # Crude way to get subject for testing (real EMLs have headers)
                        # Let's use a placeholder or derive from filename for mock
                        mock_subject = ""
                        if "received" in filename:
                            mock_subject = "Sender Company Name has sent you money" # From anonymized_received_payment.eml
                        elif "sent" in filename:
                            mock_subject = "Vous avez envoyé un paiement de 20,00 EUR à Recipient Name" # From anonymized_sent_payment.eml
                        
                        mock_email = MockEmailMessage(uid=f"local_{filename}", subject=mock_subject, html_content=eml_content)
                        parsed_data = processor.parse_email_details(mock_email)
                        if parsed_data:
                            logger.info(f"Parsed data for {filename}:")
                            for key, value in parsed_data.items():
                                if key != "raw_html_for_debug": # Don't print full HTML
                                    logger.info(f"  {key}: {value}")
                        else:
                            logger.warning(f"Failed to parse {filename} or no data extracted.")
                except FileNotFoundError:
                    logger.error(f"Test file {filename} not found. Place it in the 'paypal_mail_to_evm_bot' directory or update path.")
                except Exception as e_file:
                    logger.error(f"Error processing test file {filename}: {e_file}", exc_info=True)
            exit()


        processor = EmailProcessor(
            imap_server=config["IMAP_SERVER"],
            imap_username=config["IMAP_USERNAME"],
            imap_password=config["IMAP_PASSWORD"]
        )

        if processor.connect():
            paypal_emails = processor.fetch_paypal_emails(config.get("PAYPAL_SENDER_EMAIL", "service@paypal.com"))
            if paypal_emails:
                logger.info(f"Fetched {len(paypal_emails)} PayPal email(s).")
                for email_msg in paypal_emails:
                    logger.info(f"--- Attempting to parse email UID: {email_msg.uid}, Subject: {email_msg.subject} ---")
                    details = processor.parse_email_details(email_msg)
                    if details:
                        logger.info("Parsed Details:")
                        for key, value in details.items():
                             if key != "raw_html_for_debug":
                                logger.info(f"  {key}: {value}")
                    else:
                        logger.warning(f"Could not parse details for email UID: {email_msg.uid}")
            else:
                logger.info("No PayPal emails found to parse.")
            processor.logout()
        else:
            logger.error("Could not connect to IMAP server. Aborting test.")

    except ValueError as ve: # Config loading error
        logger.error(f"Configuration error: {ve}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during testing: {e}", exc_info=True) 