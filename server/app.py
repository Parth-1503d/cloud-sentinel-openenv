import uvicorn # type: ignore
# This imports the app we already built!
from src.envs.cloud_audit.server import app 

def main():
    print("Starting Cloud-Sentinel via OpenEnv Grader...")
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()