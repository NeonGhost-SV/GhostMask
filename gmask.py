import random 
import time
import requests
import yaml
import socks
import socket
import os
import sys
import select
from threading import Thread, Event
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

BANNER = """
██████╗ ██╗      █████╗  ██████╗███╗   ███╗██╗███╗   ██╗ ██████╗ ██████╗ 
██╔══██╗██║     ██╔══██╗██╔════╝████╗ ████║██║████╗  ██║██╔════╝ ██╔══██╗
██████╔╝██║     ███████║██║     ██╔████╔██║██║██╔██╗ ██║██║  ███╗██████╔╝
██╔═══╝ ██║     ██╔══██║██║     ██║╚██╔╝██║██║██║╚██╗██║██║   ██║██╔═══╝ 
██║     ███████╗██║  ██║╚██████╗██║ ╚═╝ ██║██║██║ ╚████║╚██████╔╝██║     
╚═╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝     
"""

print(BANNER)
print(Fore.YELLOW + "👨💻 DEVELOPER: ANKIT KUMAR")
print(Fore.CYAN + "  🔥 GHOST MASK - THE ULTIMATE PROXY MASKING TOOL 🔥\n" + Style.RESET_ALL)

print(Fore.CYAN + "⚙ Starting Anonymous service in background...")
os.system("service tor start")
print(Fore.GREEN + "✅ Service started successfully!\n")

# Control event to stop threads
stop_event = Event()

# User selection for network mode
def choose_mode():
    print(Fore.GREEN + "Select a mode:")
    print(Fore.MAGENTA + "1. Use Tor Network (Secure but Slow)" + Style.RESET_ALL)
    print(Fore.MAGENTA + "2. Use Proxychains (Secure and Fast)" + Style.RESET_ALL)
    print(Fore.MAGENTA + "3. Use Tor + VPN" + Style.RESET_ALL)
    print(Fore.MAGENTA + "4. Use Proxychains + VPN" + Style.RESET_ALL)
    print(Fore.MAGENTA + "5. Use VPN Only" + Style.RESET_ALL)
    choice = input(Fore.YELLOW + "Enter Anonymous Mode (1, 2, 3, 4, or 5): ")

    if choice == "1":
        print(Fore.CYAN + "⚙ Starting Tor service...")
        os.system("service tor start")
        print(Fore.GREEN + "✅ Tor started successfully!")
        return "tor"
    elif choice == "2":
        print(Fore.GREEN + "🔗 Using proxychains mode with custom SOCKS5 proxies.")
        return "proxy"
    elif choice == "3":
        print(Fore.CYAN + "⚙ Starting Tor + VPN service...")
        os.system("service tor start")
        start_vpn()  # Start VPN after Tor
        return "tor+vpn"
    elif choice == "4":
        print(Fore.GREEN + "🔗 Using proxychains + VPN mode.")
        start_vpn()  # Start VPN first
        return "proxy+vpn"
    elif choice == "5":
        print(Fore.GREEN + "🔒 Using VPN only mode.")
        start_vpn()  # Start VPN only
        return "vpn"
    else:
        print(Fore.RED + "❌ Invalid choice. Exiting...")
        exit()

# Function to start VPN (example placeholder)
def start_vpn():
    print(Fore.CYAN + "⚙ Starting VPN service...")
    # Here, you can integrate VPN logic (for example, calling a VPN client command).
    # This could be any VPN service (like OpenVPN or a custom VPN script).
    os.system("service openvpn start")  # Example VPN service
    print(Fore.GREEN + "✅ VPN started successfully!")

# Load proxies from config.yaml
def load_proxy_config():
    try:
        with open("config.yaml", "r") as f:
            data = yaml.safe_load(f)
        tor_proxies = data.get("proxy", [])
        proxychains_proxies = data.get("proxies", [])
        return tor_proxies, proxychains_proxies
    except FileNotFoundError:
        print(Fore.RED + "❌ config.yaml file not found!")
        return [], []

# Set SOCKS5 proxy
def set_proxy(proxy):
    proxy_ip, proxy_port = proxy.split(":")
    socks.set_default_proxy(socks.SOCKS5, proxy_ip, int(proxy_port))
    socket.socket = socks.socksocket

# Test proxy and return public IP
def test_proxy(proxy):
    try:
        set_proxy(proxy)
        response = requests.get("http://checkip.amazonaws.com", timeout=5)
        return response.text.strip()
    except Exception:
        return None

# Rotate proxychains proxies and return success status
def rotate_proxies(proxychains_proxies):
    if not proxychains_proxies:
        print(Fore.RED + "⚠ No proxies found in [proxies] section!")
        return False

    print(Fore.MAGENTA + "\n🔄 New Proxy Chain:\n")
    success = False
    selected_proxies = random.sample(proxychains_proxies, min(3, len(proxychains_proxies)))
    for proxy in selected_proxies:
        if stop_event.is_set():
            break
        ip = test_proxy(proxy)
        if ip:
            print(Fore.GREEN + f"✅ Proxy Active: {proxy} → IP: {ip}")
            success = True
        else:
            print(Fore.RED + f"❌ Proxy Failed: {proxy}")
    return success

# Example request with current proxy
def fetch_data(url="http://checkip.amazonaws.com"):
    try:
        response = requests.get(url, timeout=5)
        print(Fore.BLUE + "🌍 Your Current IP:", response.text.strip())
    except Exception as e:
        print(Fore.RED + f"⚠ Failed to fetch data: {e}")

# ========== MAIN ========== 
# ===================== MAIN =====================
if __name__ == "__main__":
    tor_proxies, proxychains_proxies = load_proxy_config()
    mode = choose_mode()

    if mode == "tor":
        if tor_proxies:
            set_proxy(tor_proxies[0])
            print(Fore.YELLOW + "🌐 Routing traffic through Tor network...")
        else:
            print(Fore.RED + "❌ No Tor proxy found in config.yaml!")
            exit()
    elif mode == "proxy":
        success = rotate_proxies(proxychains_proxies)
        if not success:
            print(Fore.YELLOW + "⚠ All proxychains proxies failed! Switching to Tor as fallback...")
            if tor_proxies:
                set_proxy(tor_proxies[0])
                print(Fore.YELLOW + "🌐 Routing traffic through Tor network...")
            else:
                print(Fore.RED + "❌ No Tor proxy found to fallback. Exiting.")
                exit()
    elif mode == "tor+vpn":
        if tor_proxies:
            set_proxy(tor_proxies[0])
            print(Fore.YELLOW + "🌐 Routing traffic through Tor + VPN...")
        else:
            print(Fore.RED + "❌ No Tor proxy found in config.yaml!")
            exit()
    elif mode == "proxy+vpn":
        success = rotate_proxies(proxychains_proxies)
        if not success:
            print(Fore.YELLOW + "⚠ All proxychains proxies failed! Switching to Tor + VPN as fallback...")
            if tor_proxies:
                set_proxy(tor_proxies[0])
                print(Fore.YELLOW + "🌐 Routing traffic through Tor + VPN...")
            else:
                print(Fore.RED + "❌ No Tor proxy found to fallback. Exiting.")
                exit()
    elif mode == "vpn":
        start_vpn()  # Only VPN, no proxy service needed
        print(Fore.GREEN + "🌐 Routing traffic through VPN...")

    print(Fore.LIGHTGREEN_EX + "\n⏳ Press 'q' or '0' anytime to stop the program.\n")

    try:
        while not stop_event.is_set():
            fetch_data()
            for _ in range(60):  # 60 seconds
                if sys.stdin in select.select([sys.stdin], [], [], 1)[0]:
                    user_input = input().strip().lower()
                    if user_input in ['q', '0']:
                        stop_event.set()
                        print(Fore.RED + "\n🛑 Killing All processes...")

                        # Stop Tor service if it's running
                        print(Fore.CYAN + "⚙ Stopping Tor service...")
                        os.system("service tor stop")
                        print(Fore.GREEN + "✅ Tor service stopped.")

                        # Stop VPN service if it's running
                        print(Fore.CYAN + "⚙ Stopping VPN service...")
                        os.system("service openvpn stop")
                        print(Fore.GREEN + "✅ VPN service stopped.")
                        
                        break
            if stop_event.is_set():
                break
    except KeyboardInterrupt:
        stop_event.set()
        print(Fore.RED + "\n🛑 Interrupted. Exiting GHOSTMASK...")

    print(Fore.GREEN + "👋 Goodbye! Stay anonymous, hacker!")







