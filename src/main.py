from fastapi import FastAPI

app = FastAPI(title="Outlyne API")

@app.get("/")
async def root():
    return {"message": "Outlyne API is running"}

def main():
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
