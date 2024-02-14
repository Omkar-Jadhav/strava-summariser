from fastapi import FastAPI

app = FastAPI()

@app.route('/', methods=['GET'])
def hello():
    return "Hello"

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
    print("Webhook is listening")  # Log listening message
