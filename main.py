from fastapi import FastAPI
from playwright.async_api import async_playwright

app = FastAPI()

@app.get("/")
def home():
    return {"message": "✅ Bot is working!"}

@app.get("/check")
async def check(product: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.ebay.co.uk/sch/i.html?_nkw={product}&LH_Sold=1")
        await page.wait_for_timeout(3000)
        items = await page.locator(".s-item").count()
        await browser.close()
        return {"product": product, "sold_results": items}
