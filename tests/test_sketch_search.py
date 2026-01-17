import asyncio
import base64
import io

import httpx
from PIL import Image


async def test_pure_sketch_search() -> None:
    # 1. Create a dummy sketch (a simple black circle on white background)
    img = Image.new('RGB', (224, 224), color='white')
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.ellipse([50, 50, 150, 150], outline='black', width=5)
    
    # 2. Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    sketch_base64 = base64.b64encode(buffered.getvalue()).decode()

    # 3. Prepare payload (NO TEXT QUERY)
    payload = {
        "sketch_base64": sketch_base64,
        "query": "",  # Pure sketch
        "max_results": 5
    }

    print("🚀 Sending pure sketch search request (Zero-Shot)...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post("http://localhost:8000/search", json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Found {data['count']} results.")
                for i, res in enumerate(data['results']):
                    print(f"[{i+1}] {res['title']} - {res['url']}")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_pure_sketch_search())
