# Domain Extraction and Analysis Tool

This Python script is designed to extract domains from URLs, check their expiration status, resolve DNS records, and generate detailed reports. It supports both static and dynamic content scraping using Selenium and offers options for email notifications. The tool is ideal for domain analysis and assessing subdomain takeover opportunities.

## Features

- **Domain Extraction**: Efficiently extract domains from a list of URLs.
- **Domain Expiration Check**: Determine whether domains are expired, which is useful for subdomain takeover assessments.
- **DNS Records Resolution**: Resolve and list DNS records for each domain, including A, AAAA, MX, and CNAME records.
- **Detailed Reports**: Generate comprehensive reports in CSV and text formats.
- **Email Notifications**: Optionally send reports via email with customizable settings.
- **Dynamic Content Handling**: Use Selenium to handle and scrape dynamic web content rendered by JavaScript.

## Requirements

- **Python 3.x**: Ensure Python is installed on your system.
- **Python Libraries**: Install required libraries using the following commands:
  ```bash
  pip install requests beautifulsoup4 selenium dnspython whois


Chromedriver: For Selenium support, download Chromedriver and place it in a directory of your choice. Update the path in the script if necessary.
