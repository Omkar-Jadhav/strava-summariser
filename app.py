from fastapi import FastAPI
import os
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, world!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn  # Or gunicorn for production
    # Note: You don't need a Procfile for Vercel deployment
    
    # Environment variables will be injected by Vercel during deployment
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
    print("webhook is listening")