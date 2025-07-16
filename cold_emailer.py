#!/usr/bin/env python3
"""
Cold Email Sender Script

A Python script to send cold emails to multiple recipients with:
- SMTP email support (Gmail, Outlook, custom servers)
- Rate limiting to avoid spam filters
- Email template support
- CSV import for recipient lists
- Error handling and logging
- Email tracking (basic)

Usage:
    python cold_emailer.py --config config.json --recipients recipients.csv
"""

import smtplib
import ssl
import json
import csv
import time
import random
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import argparse
import os
from typing import List, Dict, Optional
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cold_emailer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ColdEmailer:
    def __init__(self, config_file: str):
        """Initialize the cold emailer with configuration."""
        self.config = self.load_config(config_file)
        self.smtp_server = None
        self.smtp_port = None
        self.sender_email = None
        self.sender_password = None
        self.setup_smtp()
        
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file {config_file} not found")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            raise
    
    def setup_smtp(self):
        """Setup SMTP connection details."""
        email_config = self.config.get('email', {})
        self.smtp_server = email_config.get('smtp_server')
        self.smtp_port = email_config.get('smtp_port', 587)
        self.sender_email = email_config.get('sender_email')
        self.sender_password = email_config.get('sender_password')
        
        if not all([self.smtp_server, self.sender_email, self.sender_password]):
            raise ValueError("Missing required email configuration")
    
    def create_email_message(self, recipient: Dict, template: Dict) -> MIMEMultipart:
        """Create an email message with personalization."""
        msg = MIMEMultipart('alternative')
        msg['From'] = self.sender_email
        msg['To'] = recipient['email']
        msg['Subject'] = self.personalize_subject(template['subject'], recipient)
        
        # Personalize the email body
        personalized_body = self.personalize_body(template['body'], recipient)
        
        # Create both plain text and HTML versions
        text_part = MIMEText(personalized_body, 'plain', 'utf-8')
        
        # Create HTML version with clickable links
        html_body = personalized_body.replace('\n', '<br>')
        # Make URLs clickable
        import re
        html_body = re.sub(r'(https?://[^\s]+)', r'<a href="\1" style="color: #0066cc; text-decoration: underline;">\1</a>', html_body)
        
        html_part = MIMEText(html_body, 'html', 'utf-8')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        return msg
    
    def personalize_subject(self, subject_template: str, recipient: Dict) -> str:
        """Personalize the email subject line."""
        return subject_template.format(**recipient)
    
    def personalize_body(self, body_template: str, recipient: Dict) -> str:
        """Personalize the email body with recipient data."""
        return body_template.format(**recipient)
    
    def send_email(self, msg: MIMEMultipart) -> bool:
        """Send a single email."""
        try:
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                
                text = msg.as_string()
                server.sendmail(self.sender_email, msg['To'], text)
                
                logger.info(f"Email sent successfully to {msg['To']}")
                return True
                
        except smtplib.SMTPAuthenticationError:
            logger.error(f"Authentication failed for {self.sender_email}")
            return False
        except smtplib.SMTPRecipientsRefused:
            logger.error(f"Recipient refused: {msg['To']}")
            return False
        except smtplib.SMTPServerDisconnected:
            logger.error("SMTP server disconnected")
            return False
        except Exception as e:
            logger.error(f"Error sending email to {msg['To']}: {str(e)}")
            return False
    
    def load_recipients(self, recipients_file: str) -> List[Dict]:
        """Load recipients from CSV file."""
        recipients = []
        try:
            with open(recipients_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    recipients.append(row)
            logger.info(f"Loaded {len(recipients)} recipients from {recipients_file}")
            return recipients
        except FileNotFoundError:
            logger.error(f"Recipients file {recipients_file} not found")
            raise
        except Exception as e:
            logger.error(f"Error loading recipients: {str(e)}")
            raise
    
    def send_cold_emails(self, recipients_file: str, dry_run: bool = False):
        """Send cold emails to all recipients."""
        recipients = self.load_recipients(recipients_file)
        template = self.config.get('template', {})
        
        if not template.get('subject') or not template.get('body'):
            raise ValueError("Email template must include 'subject' and 'body'")
        
        # Rate limiting settings
        min_delay = self.config.get('rate_limiting', {}).get('min_delay_seconds', 30)
        max_delay = self.config.get('rate_limiting', {}).get('max_delay_seconds', 60)
        max_emails_per_hour = self.config.get('rate_limiting', {}).get('max_emails_per_hour', 50)
        
        sent_count = 0
        failed_count = 0
        
        logger.info(f"Starting cold email campaign to {len(recipients)} recipients")
        if dry_run:
            logger.info("DRY RUN MODE - No emails will be sent")
        
        for i, recipient in enumerate(recipients):
            try:
                logger.info(f"Processing {i+1}/{len(recipients)}: {recipient.get('email', 'Unknown')}")
                
                if not dry_run:
                    msg = self.create_email_message(recipient, template)
                    success = self.send_email(msg)
                    
                    if success:
                        sent_count += 1
                    else:
                        failed_count += 1
                else:
                    # Dry run - just log what would be sent
                    msg = self.create_email_message(recipient, template)
                    logger.info(f"DRY RUN: Would send to {msg['To']} with subject: {msg['Subject']}")
                    sent_count += 1
                
                # Rate limiting
                if i < len(recipients) - 1:  # Don't delay after the last email
                    delay = random.uniform(min_delay, max_delay)
                    logger.info(f"Waiting {delay:.1f} seconds before next email...")
                    time.sleep(delay)
                
                # Hourly limit check
                if (i + 1) % max_emails_per_hour == 0 and i < len(recipients) - 1:
                    logger.info(f"Reached hourly limit ({max_emails_per_hour}). Waiting 1 hour...")
                    time.sleep(3600)  # Wait 1 hour
                
            except Exception as e:
                logger.error(f"Error processing recipient {recipient.get('email', 'Unknown')}: {str(e)}")
                failed_count += 1
        
        logger.info(f"Campaign completed. Sent: {sent_count}, Failed: {failed_count}")
        return sent_count, failed_count

def create_sample_config():
    """Create a sample configuration file."""
    config = {
        "email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "your-email@gmail.com",
            "sender_password": "your-app-password"
        },
        "template": {
            "subject": "Hi {first_name}, I'd love to connect about {company}",
            "body": """Hi {first_name},

I hope this email finds you well. I came across {company} and was impressed by your work in {industry}.

I believe there might be an opportunity for us to collaborate on {potential_project}. Would you be interested in a brief 15-minute call to discuss this further?

Looking forward to hearing from you.

Best regards,
{your_name}
{your_title}
{your_company}
{your_phone}"""
        },
        "rate_limiting": {
            "min_delay_seconds": 30,
            "max_delay_seconds": 60,
            "max_emails_per_hour": 50
        }
    }
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    logger.info("Sample configuration file 'config.json' created")

def create_sample_recipients():
    """Create a sample recipients CSV file."""
    recipients = [
        {
            'email': 'john.doe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'company': 'TechCorp',
            'industry': 'software development',
            'potential_project': 'web application development',
            'your_name': 'Jane Smith',
            'your_title': 'Business Development Manager',
            'your_company': 'Innovation Labs',
            'your_phone': '+1-555-0123'
        },
        {
            'email': 'jane.smith@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'company': 'StartupXYZ',
            'industry': 'e-commerce',
            'potential_project': 'digital marketing strategy',
            'your_name': 'Jane Smith',
            'your_title': 'Business Development Manager',
            'your_company': 'Innovation Labs',
            'your_phone': '+1-555-0123'
        }
    ]
    
    with open('recipients.csv', 'w', newline='', encoding='utf-8') as f:
        if recipients:
            writer = csv.DictWriter(f, fieldnames=recipients[0].keys())
            writer.writeheader()
            writer.writerows(recipients)
    logger.info("Sample recipients file 'recipients.csv' created")

def main():
    """Main function to run the cold emailer."""
    parser = argparse.ArgumentParser(description='Send cold emails to multiple recipients')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--recipients', default='recipients.csv', help='Recipients CSV file path')
    parser.add_argument('--test', action='store_true', help='Use test.csv instead of recipients.csv for testing')
    parser.add_argument('--dry-run', action='store_true', help='Run without sending emails')
    parser.add_argument('--create-samples', action='store_true', help='Create sample config and recipients files')
    
    args = parser.parse_args()
    
    if args.create_samples:
        create_sample_config()
        create_sample_recipients()
        print("Sample files created. Please edit config.json and recipients.csv before running.")
        return
    
    # Determine which recipients file to use
    recipients_file = 'test.csv' if args.test else args.recipients
    
    try:
        emailer = ColdEmailer(args.config)
        sent, failed = emailer.send_cold_emails(recipients_file, args.dry_run)
        
        print(f"\nCampaign Summary:")
        print(f"Emails sent: {sent}")
        print(f"Emails failed: {failed}")
        
    except Exception as e:
        logger.error(f"Campaign failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 


# TESTTEST