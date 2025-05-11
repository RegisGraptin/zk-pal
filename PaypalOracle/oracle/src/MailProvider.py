import re

from imap_tools import MailBox, AND

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