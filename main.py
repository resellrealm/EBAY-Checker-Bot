from fastapi import FastAPI
from playwright.async_api import async_playwright
import re
from datetime import datetime, timedelta
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return {"message": "✅ eBay Bot is running! Add /check?product=youritem"}

@app.get("/check")
async def check(product: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Go to eBay sold page for the product
        await page.goto(f"https://www.ebay.co.uk/sch/i.html?_nkw={product}&LH_Sold=1")
        await page.wait_for_timeout(4000)

        items = await page.locator(".s-item").all()
        sold_24h = 0
        sold_7d = 0
        prices = []

        now = datetime.utcnow()

        for item in items:
            # Extract date text (e.g. "Sold 23 Oct 2025")
            try:
                date_text = await item.locator(".s-item__title--tagblock").inner_text()
            except:
                continue

            match = re.search(r"(\d{1,2}\s\w+\s20\d{2})", date_text)
            if not match:
                continue

            sold_date = datetime.strptime(match.group(1), "%d %b %Y")
            diff_days = (now - sold_date).days

            # Check time range
            if diff_days <= 1:
                sold_24h += 1
            if diff_days <= 7:
                sold_7d += 1

            # Extract price
            try:
                price_text = await item.locator(".s-item__price").inner_text()
                price = float(re.sub(r"[^\d.]", "", price_text))
                prices.append(price)
            except:
                pass

        await browser.close()

        avg_price = round(sum(prices)/len(prices), 2) if prices else 0

        return {
            "product": product,
            "sold_last_24h": sold_24h,
            "sold_last_7d": sold_7d,
            "average_price": f"£{avg_price}"
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
