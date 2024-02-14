from app import app
import os
if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", 8000)))
    print("webhook is listening")