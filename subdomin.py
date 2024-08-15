import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import csv
import concurrent.futures
import re
import whois
import dns.resolver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from requests.exceptions import RequestException
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def extract_domains(url, use_selenium=False):
    try:
        if use_selenium:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            service = Service('D:/تسطيب/chromedriver-win64/chromedriver.exe')
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(url)
            time.sleep(5)  # Allow time for page to load fully
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()
        else:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            soup = BeautifulSoup(response.content, 'html.parser')

        links = soup.find_all('a', href=True)
        domains = set()
        parsed_base_url = urlparse(url)

        for link in links:
            href = link['href']
            href = urljoin(url, href)
            parsed_url = urlparse(href)
            domain = parsed_url.netloc

            # Ensure domain is part of the base URL or is a subdomain
            if domain and (parsed_base_url.netloc in domain or domain.endswith(parsed_base_url.netloc)):
                if re.match(r'[a-zA-Z0-9.-]+', domain):
                    domains.add(domain)
        
        return domains

    except RequestException as e:
        print(f"Request error for URL {url}: {e}")
        return set()
    except Exception as e:
        print(f"An error occurred: {e}")
        return set()

def check_domain_expiry(domain):
    try:
        w = whois.whois(domain)
        expiration_date = w.expiration_date
        if expiration_date:
            if isinstance(expiration_date, list):
                expiration_date = expiration_date[0]
            return expiration_date < time.time()
        return False
    except Exception as e:
        print(f"Error checking domain expiration for {domain}: {e}")
        return None

def resolve_dns(domain):
    try:
        answers = dns.resolver.resolve(domain, 'A')
        return [answer.to_text() for answer in answers]
    except dns.resolver.NoAnswer:
        return []
    except dns.resolver.NXDOMAIN:
        return []
    except Exception as e:
        print(f"Error resolving DNS for {domain}: {e}")
        return []

def fetch_domains_from_urls(urls, use_selenium=False):
    domains = set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(extract_domains, url, use_selenium) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            domains.update(result)
    return domains

def save_domains_to_csv(domains, filename="domains.csv"):
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Domain", "Expired", "DNS Records"])
            for domain, expired, dns_records in domains:
                writer.writerow([domain, expired, ", ".join(dns_records)])
        print(f"Domains saved to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def generate_report(domains, filename="report.txt"):
    try:
        with open(filename, mode='w') as file:
            file.write("Domain Extraction Report\n")
            file.write("="*40 + "\n")
            file.write(f"Total domains extracted: {len(domains)}\n\n")
            file.write("Extracted Domains:\n")
            for domain, expired, dns_records in domains:
                status = "Expired" if expired else "Active"
                file.write(f"- {domain}: {status}\n")
                file.write(f"  DNS Records: {', '.join(dns_records)}\n")
        print(f"Report saved to {filename}")
    except Exception as e:
        print(f"Error generating report: {e}")

def send_email(subject, body, to_email):
    try:
        from_email = "your_email@example.com"  # Replace with your email
        from_password = "your_password"  # Replace with your email password

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.example.com', 587) as server:  # Replace with your SMTP server details
            server.starttls()
            server.login(from_email, from_password)
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)

        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    urls = input("Enter URLs to extract domains from (comma-separated): ").split(',')
    urls = [url.strip() for url in urls]
    
    # Option to use Selenium for dynamic content
    use_selenium = input("Use Selenium for dynamic content? (y/n): ").strip().lower() == 'y'
    
    if not urls:
        print("Error: Please enter at least one URL.")
    else:
        print("Extraction started. This may take some time...")
        domains = fetch_domains_from_urls(urls, use_selenium)
        
        if domains:
            # Check domain expiry and resolve DNS
            domains_with_status = [(domain, check_domain_expiry(domain), resolve_dns(domain)) for domain in domains]
            
            print("\nExtracted domains:")
            for domain, expired, dns_records in domains_with_status:
                status = "Expired" if expired else "Active"
                print(f"{domain}: {status}, DNS Records: {', '.join(dns_records)}")
            
            # Save domains to CSV
            save_domains_to_csv(domains_with_status)
            
            # Generate report
            generate_report(domains_with_status)
            
            # Optionally send email with the report
            send_report = input("Send report via email? (y/n): ").strip().lower() == 'y'
            if send_report:
                email_address = input("Enter recipient email address: ").strip()
                email_subject = "Domain Extraction Report"
                with open("report.txt", "r") as report_file:
                    email_body = report_file.read()
                send_email(email_subject, email_body, email_address)
        else:
            print("No domains were extracted.")
