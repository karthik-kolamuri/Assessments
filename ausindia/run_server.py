import uvicorn

if __name__ == "__main__":
    print("Starting Bulk Certificate Generator API Server on http://localhost:8000 ...")
    print("Web Dashboard: http://localhost:8000/")
    print("Swagger UI:    http://localhost:8000/docs")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
