import uvicorn


def main() -> None:
    print("Iniciando NovaStore em http://localhost:8000 ...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
