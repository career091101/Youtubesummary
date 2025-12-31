#!/usr/bin/env python3
"""
Proxy Tester Script
Tests all proxies in proxy_list.txt and reports which ones are working.
"""

import sys
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ProxyTestResult:
    """Result of a proxy test."""
    host: str
    port: int
    is_working: bool
    response_time: float = 0.0
    error_message: str = ""
    external_ip: str = ""


def parse_proxy_line(line: str) -> Tuple[str, int, str, str]:
    """Parse a proxy line in the format: ip:port:username:password"""
    parts = line.strip().split(':')
    if len(parts) == 4:
        return parts[0], int(parts[1]), parts[2], parts[3]
    elif len(parts) == 2:
        return parts[0], int(parts[1]), '', ''
    else:
        raise ValueError(f"Invalid proxy format: {line}")


def test_proxy(host: str, port: int, username: str, password: str, 
               timeout: int = 10) -> ProxyTestResult:
    """Test a single proxy by making a request to a test URL."""
    
    # Build proxy URL
    if username and password:
        proxy_url = f"http://{username}:{password}@{host}:{port}"
    else:
        proxy_url = f"http://{host}:{port}"
    
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    # Test URLs - we'll try httpbin first, then fall back to others
    test_urls = [
        'https://httpbin.org/ip',
        'https://api.ipify.org?format=json',
        'http://ip-api.com/json'
    ]
    
    for test_url in test_urls:
        try:
            start_time = time.time()
            response = requests.get(
                test_url,
                proxies=proxies,
                timeout=timeout,
                verify=True
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # Try to extract IP from response
                try:
                    data = response.json()
                    external_ip = data.get('origin', '') or data.get('ip', '') or data.get('query', '')
                except:
                    external_ip = "Unknown"
                
                return ProxyTestResult(
                    host=host,
                    port=port,
                    is_working=True,
                    response_time=response_time,
                    external_ip=external_ip
                )
        except requests.exceptions.ProxyError as e:
            error_msg = f"Proxy Error: {str(e)[:100]}"
        except requests.exceptions.ConnectTimeout:
            error_msg = "Connection Timeout"
        except requests.exceptions.ReadTimeout:
            error_msg = "Read Timeout"
        except requests.exceptions.SSLError as e:
            error_msg = f"SSL Error: {str(e)[:100]}"
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection Error: {str(e)[:100]}"
        except Exception as e:
            error_msg = f"Error: {str(e)[:100]}"
    
    return ProxyTestResult(
        host=host,
        port=port,
        is_working=False,
        error_message=error_msg
    )


def load_proxies(filename: str) -> List[Tuple[str, int, str, str]]:
    """Load proxies from file."""
    proxies = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            try:
                proxies.append(parse_proxy_line(line))
            except ValueError as e:
                print(f"Warning: {e}")
    return proxies


def main():
    proxy_file = "proxy_list.txt"
    timeout = 15  # seconds
    max_workers = 5  # parallel tests
    
    print("=" * 70)
    print("🔍 Proxy Tester")
    print("=" * 70)
    print()
    
    # Load proxies
    try:
        proxies = load_proxies(proxy_file)
    except FileNotFoundError:
        print(f"Error: {proxy_file} not found")
        sys.exit(1)
    
    if not proxies:
        print("No proxies found in the file")
        sys.exit(1)
    
    print(f"📋 Found {len(proxies)} proxies to test")
    print(f"⏱️  Timeout: {timeout} seconds per proxy")
    print(f"🔄 Max parallel tests: {max_workers}")
    print()
    print("Testing proxies...")
    print("-" * 70)
    
    results: List[ProxyTestResult] = []
    
    # Test proxies in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_proxy = {
            executor.submit(test_proxy, host, port, username, password, timeout): 
            (host, port) for host, port, username, password in proxies
        }
        
        for future in as_completed(future_to_proxy):
            result = future.result()
            results.append(result)
            
            if result.is_working:
                print(f"✅ {result.host}:{result.port} - "
                      f"OK ({result.response_time:.2f}s) - IP: {result.external_ip}")
            else:
                print(f"❌ {result.host}:{result.port} - "
                      f"FAILED - {result.error_message}")
    
    # Summary
    working = [r for r in results if r.is_working]
    failed = [r for r in results if not r.is_working]
    
    print()
    print("=" * 70)
    print("📊 Summary")
    print("=" * 70)
    print(f"✅ Working proxies: {len(working)}/{len(results)}")
    print(f"❌ Failed proxies:  {len(failed)}/{len(results)}")
    print()
    
    if working:
        print("Working Proxies:")
        print("-" * 70)
        for r in sorted(working, key=lambda x: x.response_time):
            print(f"  {r.host}:{r.port} - {r.response_time:.2f}s - IP: {r.external_ip}")
        
        # Calculate average response time
        avg_time = sum(r.response_time for r in working) / len(working)
        print()
        print(f"Average response time: {avg_time:.2f}s")
    
    if failed:
        print()
        print("Failed Proxies:")
        print("-" * 70)
        for r in failed:
            print(f"  {r.host}:{r.port} - {r.error_message}")
    
    # Save results to file
    output_file = "proxy_test_results.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Proxy Test Results - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"Working: {len(working)}/{len(results)}\n")
        f.write(f"Failed: {len(failed)}/{len(results)}\n\n")
        
        f.write("WORKING PROXIES:\n")
        f.write("-" * 70 + "\n")
        for r in sorted(working, key=lambda x: x.response_time):
            f.write(f"{r.host}:{r.port} | {r.response_time:.2f}s | IP: {r.external_ip}\n")
        
        f.write("\nFAILED PROXIES:\n")
        f.write("-" * 70 + "\n")
        for r in failed:
            f.write(f"{r.host}:{r.port} | Error: {r.error_message}\n")
    
    print()
    print(f"📄 Results saved to: {output_file}")
    print()
    
    return 0 if working else 1


if __name__ == "__main__":
    sys.exit(main())
