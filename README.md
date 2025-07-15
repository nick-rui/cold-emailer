# Cold Email Sender

A Python script for sending personalized cold emails to multiple recipients with rate limiting, error handling, and logging.

## Features

- **SMTP Support**: Works with Gmail, Outlook, and custom SMTP servers
- **Personalization**: Dynamic email templates with recipient data
- **Rate Limiting**: Configurable delays to avoid spam filters
- **CSV Import**: Load recipient lists from CSV files
- **Error Handling**: Comprehensive logging and error recovery
- **Dry Run Mode**: Test your setup without sending actual emails
- **HTML & Plain Text**: Sends both formats for better deliverability

## Quick Start

### 1. Create Sample Files

```bash
python cold_emailer.py --create-samples
```

This creates:
- `config.json` - Email configuration and template
- `recipients.csv` - Sample recipient list

### 2. Configure Your Settings

Edit `config.json` with your email credentials:

```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-app-password"
  },
  "template": {
    "subject": "Hi {first_name}, I'd love to connect about {company}",
    "body": "Hi {first_name},\n\nI hope this email finds you well..."
  },
  "rate_limiting": {
    "min_delay_seconds": 30,
    "max_delay_seconds": 60,
    "max_emails_per_hour": 50
  }
}
```

### 3. Prepare Your Recipient List

Edit `recipients.csv` with your target contacts:

```csv
email,first_name,last_name,company,industry,potential_project,your_name,your_title,your_company,your_phone
john.doe@example.com,John,Doe,TechCorp,software development,web application development,Jane Smith,Business Development Manager,Innovation Labs,+1-555-0123
jane.smith@example.com,Jane,Smith,StartupXYZ,e-commerce,digital marketing strategy,Jane Smith,Business Development Manager,Innovation Labs,+1-555-0123
```

### 4. Test with Dry Run

```bash
python cold_emailer.py --dry-run
```

### 5. Send Emails

```bash
python cold_emailer.py
```

## Email Provider Setup

### Gmail

1. Enable 2-Factor Authentication
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use the app password in your config

### Outlook/Hotmail

```json
{
  "email": {
    "smtp_server": "smtp-mail.outlook.com",
    "smtp_port": 587,
    "sender_email": "your-email@outlook.com",
    "sender_password": "your-password"
  }
}
```

### Custom SMTP Server

```json
{
  "email": {
    "smtp_server": "your-smtp-server.com",
    "smtp_port": 587,
    "sender_email": "your-email@domain.com",
    "sender_password": "your-password"
  }
}
```

## Template Variables

Your email template can use these variables from the CSV:

- `{email}` - Recipient's email address
- `{first_name}` - Recipient's first name
- `{last_name}` - Recipient's last name
- `{company}` - Recipient's company
- `{industry}` - Industry/sector
- `{potential_project}` - Project opportunity
- `{your_name}` - Your name
- `{your_title}` - Your job title
- `{your_company}` - Your company
- `{your_phone}` - Your phone number

## Rate Limiting

Configure rate limiting to avoid spam filters:

```json
{
  "rate_limiting": {
    "min_delay_seconds": 30,
    "max_delay_seconds": 60,
    "max_emails_per_hour": 50
  }
}
```

- **min_delay_seconds**: Minimum delay between emails
- **max_delay_seconds**: Maximum delay between emails (randomized)
- **max_emails_per_hour**: Maximum emails per hour before waiting

## Command Line Options

```bash
# Basic usage
python cold_emailer.py

# Custom config and recipients files
python cold_emailer.py --config my-config.json --recipients my-recipients.csv

# Dry run (no emails sent)
python cold_emailer.py --dry-run

# Create sample files
python cold_emailer.py --create-samples

# Help
python cold_emailer.py --help
```

## Logging

The script creates a `cold_emailer.log` file with detailed information about:
- Email sending status
- Errors and failures
- Rate limiting delays
- Campaign progress

## Best Practices

### 1. Email Content
- Keep emails short and personal
- Include a clear call-to-action
- Avoid spam trigger words
- Test with dry run first

### 2. Rate Limiting
- Start with conservative delays (30-60 seconds)
- Limit to 50 emails per hour maximum
- Monitor your email provider's limits

### 3. Recipient Quality
- Verify email addresses before sending
- Personalize content for each recipient
- Respect unsubscribe requests

### 4. Compliance
- Follow CAN-SPAM Act requirements
- Include unsubscribe links
- Use legitimate business purposes only
- Respect recipient privacy

## Troubleshooting

### Authentication Errors
- Check your email/password
- For Gmail, use App Password, not regular password
- Verify 2FA is enabled (Gmail)

### Connection Errors
- Check SMTP server and port
- Verify firewall settings
- Try different ports (587, 465, 25)

### Delivery Issues
- Check spam folder
- Verify recipient email addresses
- Review email content for spam triggers

## Security Notes

- Never commit your `config.json` with real credentials
- Use environment variables for production
- Regularly rotate app passwords
- Monitor for suspicious activity

## Example Workflow

1. **Research**: Find potential contacts and their information
2. **Prepare**: Create personalized CSV with recipient data
3. **Template**: Write compelling email template
4. **Test**: Run dry run to verify setup
5. **Send**: Execute campaign with appropriate rate limiting
6. **Monitor**: Check logs and follow up on responses

## Legal Disclaimer

This tool is for legitimate business communication only. Users are responsible for:
- Complying with anti-spam laws
- Obtaining proper consent
- Following email marketing best practices
- Respecting recipient preferences

Use responsibly and ethically. 