from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Bot is running!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
