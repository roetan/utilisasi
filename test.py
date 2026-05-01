import requests
import re
import base64
from bs4 import BeautifulSoup

def get_all_available_streams():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Referer': 'https://stream.livenobarseru.com/'
    }

    base_url = "https://stream.livenobarseru.com/"
    all_streams = []

    try:
        print(f"[*] Fetching match list from {base_url}...")
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Find all match containers
        match_cards = soup.find_all('div', class_='match')
        print(f"[*] Found {len(match_cards)} potential matches.\n")

        for card in match_cards:
            try:
                # Extract Match Details
                match_name = card.find('h2').text.strip() if card.find('h2') else "Unknown Match"
                
                # Get the Player Page URL (English is usually in 'data-player')
                meta_tag = card.find('div', class_='meta')
                player_url = meta_tag.get('data-player') if meta_tag else None

                if not player_url:
                    continue

                print(f"[*] Processing: {match_name}")

                # 2. Fetch the Player Page for this specific match
                player_res = requests.get(player_url, headers=headers, timeout=5)
                
                # 3. Search for the Base64 encoded stream link
                encoded_match = re.search(r'mplay\.php\?data=([a-zA-Z0-9+/=]+)', player_res.text)

                if encoded_match:
                    base64_string = encoded_match.group(1)
                    decoded_bytes = base64.b64decode(base64_string)
                    m3u8_link = decoded_bytes.decode('utf-8')

                    # Store the data in a structured format
                    all_streams.append({
                        "match": match_name,
                        "stream_url": m3u8_link,
                        "source_page": player_url
                    })
                else:
                    print(f"    [!] No stream data found for {match_name}")

            except Exception as e:
                print(f"    [X] Error processing {match_name}: {e}")

        return all_streams

    except Exception as e:
        print(f"[X] Critical Error: {e}")
        return []

if __name__ == "__main__":
    results = get_all_available_streams()
    
    print("\n" + "="*50)
    print(f"   FINAL RESULTS: {len(results)} STREAMS FOUND")
    print("="*50)
    
    for item in results:
        print(f"MATCH: {item['match']}")
        print(f"LINK : {item['stream_url']}")
        print("-" * 50)
