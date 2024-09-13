import socket
import threading
import time
import subprocess
import re

# List of target websites
targets = [
    "google.com",
    "wikipedia.org",
    "github.com",
    "stackoverflow.com",
    "reddit.com"
]

def resolve_domain(domain):
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        print(f"Could not resolve {domain}")
        return None

# Resolve domain names to IP addresses
target_ips = {target: resolve_domain(target) for target in targets if resolve_domain(target)}

def custom_action(ip, domain):
    print(f"Target connection detected to {domain} ({ip}) at {time.strftime('%H:%M:%S')}")

def check_connections():
    while True:
        try:
            output = subprocess.check_output("netstat -n", shell=True).decode()
            
            for line in output.split('\n'):
                if 'ESTABLISHED' in line:
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+):(\d+)\s+(\d+\.\d+\.\d+\.\d+):(\d+)', line)
                    if match:
                        local_ip, local_port, remote_ip, remote_port = match.groups()
                        print(f"Connection: {local_ip}:{local_port} -> {remote_ip}:{remote_port}")
                        
                        for domain, ip in target_ips.items():
                            if remote_ip == ip:
                                custom_action(ip, domain)
        except subprocess.CalledProcessError:
            print("Error running netstat command")
        
        time.sleep(15)  # Check every 2 seconds for quicker response

if __name__ == "__main__":
    print("Website Connection Detector (Verbose Mode)")
    print("Target websites and their IPs:")
    for domain, ip in target_ips.items():
        print(f"  {domain}: {ip}")
    
    print("\nScript is running. Open any of the following links in your browser to test detection:")
    for domain in targets:
        print(f"  https://www.{domain}")
    print("\nPress Ctrl+C to stop the script.")

    check_thread = threading.Thread(target=check_connections)
    check_thread.daemon = True
    check_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")