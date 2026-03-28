#!/usr/bin/env python3
"""SpiderFoot HX integration for automated KYC/AML/OSINT (UkhmaOS graph fusion)"""
import requests, json, os

SPIDERFOOT_URL = os.environ.get("SPIDERFOOT_URL", "http://localhost:5001")

def run_osint_scan(target: str, scan_type: str = "passive"):
    """Run SpiderFoot passive OSINT scan for defensive KYC/AML vetting"""
    try:
        # SpiderFoot HX API (local install, free, 200+ modules)
        scan_config = {
            "scanname": f"MADA-{target}-{scan_type}",
            "scantarget": target,
            "usecase": "Passive",
            "modulelist": "sfp_dnsresolve,sfp_whois,sfp_emailformat,sfp_accounts,sfp_socialprofiles"
        }
        resp = requests.post(f"{SPIDERFOOT_URL}/api/scan/start", json=scan_config, timeout=30)
        scan_id = resp.json().get("scanId")
        print(f"[OSINT] SpiderFoot scan started: {scan_id} for target: {target}")
        return scan_id
    except Exception as e:
        print(f"[ERROR] SpiderFoot: {e}")
        return None

def get_scan_results(scan_id: str):
    """Retrieve scan results for UkhmaOS knowledge graph fusion"""
    try:
        resp = requests.get(f"{SPIDERFOOT_URL}/api/scan/{scan_id}/results", timeout=30)
        return resp.json()
    except Exception as e:
        print(f"[ERROR] SpiderFoot results: {e}")
        return []

if __name__ == "__main__":
    # Example: Defensive KYC scan
    scan_id = run_osint_scan("example.com", "passive")
    if scan_id:
        print(f"Scan {scan_id} running — check results with get_scan_results()")
