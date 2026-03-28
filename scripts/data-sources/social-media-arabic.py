#!/usr/bin/env python3
"""
Arabic Social Media OSINT Pipeline — JASASS/PSI-DOMINION Defensive
Monitors X/Twitter, Telegram, TikTok for trafficking, radicalization, psyops
Supports Gulf, Levantine, Egyptian, MSA dialect detection
"""
import requests, json, time, os, re
from datetime import datetime

# Arabic threat keywords (trafficking, radicalization, terrorism, smuggling)
ARABIC_THREAT_KEYWORDS = {
    'trafficking': ['تهريب', 'تهريب_بشر', 'اتجار', 'استغلال', 'عبودية'],
    'radicalization': ['تطرف', 'تجنيد', 'جهاد', 'تكفير', 'غسيل_أدمغة'],
    'terrorism': ['إرهاب', 'تفجير', 'هجوم', 'تخريب', 'عبوة_ناسفة'],
    'smuggling': ['تسلل', 'مخدرات', 'حشيش', 'كبتاغون', 'تبييض_أموال'],
    'psyops': ['دعاية', 'تضليل', 'أخبار_كاذبة', 'حرب_نفسية', 'بوتات']
}

# Gulf dialect markers (Omani/UAE/Saudi)
GULF_MARKERS = ['يبه', 'وايد', 'زين', 'شلون', 'انزين', 'حيل', 'خوش', 'يعل']
EGYPTIAN_MARKERS = ['ازيك', 'كدا', 'بتاع', 'ده', 'دي', 'يعني', 'الله']
LEVANTINE_MARKERS = ['هلق', 'شو', 'كيفك', 'هيك', 'منيح', 'يلا']

def detect_dialect(text):
    """Auto-detect Arabic dialect"""
    if any(m in text for m in GULF_MARKERS): return 'gulf'
    if any(m in text for m in EGYPTIAN_MARKERS): return 'egyptian'
    if any(m in text for m in LEVANTINE_MARKERS): return 'levantine'
    return 'msa'

def detect_threats(text):
    """Scan text for threat keywords across all categories"""
    found = {}
    for category, keywords in ARABIC_THREAT_KEYWORDS.items():
        matches = [kw for kw in keywords if kw in text]
        if matches:
            found[category] = matches
    return found

def scan_x_twitter(query, api_key=None):
    """Search X/Twitter for Arabic threat indicators (legal, public API)"""
    key = api_key or os.environ.get('GROK_API_KEY', '')
    if not key:
        print("[WARN] No Grok/X API key — skipping Twitter scan")
        return []
    try:
        resp = requests.post('https://api.x.ai/v1/chat/completions',
            headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
            json={
                'model': 'grok-3',
                'messages': [{'role': 'user', 'content': f'Search recent X/Twitter posts in Arabic about "{query}". Return JSON array with: text, dialect, sentiment, threat_level (0-1), entities.'}]
            }, timeout=30)
        return resp.json().get('choices', [{}])[0].get('message', {}).get('content', '[]')
    except Exception as e:
        print(f"[ERROR] X/Twitter scan: {e}")
        return []

def scan_telegram_channels(keywords):
    """Monitor public Telegram channels for threat indicators (passive, legal)"""
    # Uses TelegramOSINT (open-source) or Telethon for public channels
    print(f"[QAREEN] Telegram passive scan for: {keywords}")
    # In production: connects to local Telethon instance
    return []

def generate_threat_report(results):
    """Generate structured threat report for MADA fusion"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_items': len(results),
        'by_dialect': {},
        'by_threat': {},
        'high_priority': []
    }
    for r in results:
        if isinstance(r, dict):
            dialect = r.get('dialect', 'unknown')
            report['by_dialect'][dialect] = report['by_dialect'].get(dialect, 0) + 1
            if r.get('threat_level', 0) > 0.7:
                report['high_priority'].append(r)
    return report

if __name__ == "__main__":
    print(f"[{datetime.now()}] QAREEN Arabic Social Media OSINT Pipeline Starting")
    print(f"Monitoring {sum(len(v) for v in ARABIC_THREAT_KEYWORDS.values())} Arabic threat keywords")
    
    while True:
        results = scan_x_twitter(' OR '.join(ARABIC_THREAT_KEYWORDS['trafficking'][:3]))
        report = generate_threat_report(results if isinstance(results, list) else [])
        with open('/tmp/mada-socmint.json', 'w') as f:
            json.dump(report, f, ensure_ascii=False, default=str)
        print(f"[{datetime.now()}] SOCMINT scan complete — {report['total_items']} items, {len(report['high_priority'])} high priority")
        time.sleep(300)  # Every 5 minutes
