"""
Quick launcher for the NovaStore FastAPI application.
"""
import uvicorn

if __name__ == "__main__":
    print("Iniciando NovaStore em http://127.0.0.1:8000 ...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
