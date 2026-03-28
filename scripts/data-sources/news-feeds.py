#!/usr/bin/env python3
"""
News Feed Aggregator for MADA — Regional & Global Intelligence
Sources: Al Jazeera, Reuters, BBC Arabic, Oman News Agency (all free RSS)
"""
import feedparser, json, time, re
from datetime import datetime

NEWS_FEEDS = {
    'aljazeera_arabic': 'https://www.aljazeera.net/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9',
    'aljazeera_english': 'https://www.aljazeera.com/xml/rss/all.xml',
    'reuters_world': 'https://feeds.reuters.com/reuters/worldNews',
    'bbc_arabic': 'https://feeds.bbci.co.uk/arabic/rss.xml',
    'bbc_middleeast': 'https://feeds.bbci.co.uk/news/world/middle_east/rss.xml',
}

# Middle East / Security keywords for filtering
MADA_KEYWORDS = [
    'oman', 'عمان', 'gulf', 'خليج', 'iran', 'إيران', 'yemen', 'يمن',
    'strait', 'هرمز', 'hormuz', 'security', 'أمن', 'military', 'عسكري',
    'cyber', 'سيبراني', 'drone', 'طائرة', 'maritime', 'بحري', 'oil', 'نفط',
    'terrorism', 'إرهاب', 'trafficking', 'تهريب', 'smuggling', 'missile', 'صاروخ'
]

def fetch_all_feeds():
    results = []
    for name, url in NEWS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:20]:
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                content = f"{title} {summary}".lower()
                
                # Filter for MADA-relevant news
                relevance = sum(1 for kw in MADA_KEYWORDS if kw in content)
                if relevance > 0:
                    results.append({
                        'source': name,
                        'title': title,
                        'summary': summary[:300],
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'relevance': relevance,
                        'timestamp': datetime.now().isoformat()
                    })
        except Exception as e:
            print(f"[WARN] Feed {name}: {e}")
    
    # Sort by relevance
    results.sort(key=lambda x: x['relevance'], reverse=True)
    return results

if __name__ == "__main__":
    while True:
        news = fetch_all_feeds()
        with open('/tmp/mada-news.json', 'w') as f:
            json.dump(news, f, ensure_ascii=False, default=str)
        print(f"[{datetime.now()}] News feed updated — {len(news)} relevant articles")
        time.sleep(300)  # Every 5 minutes
