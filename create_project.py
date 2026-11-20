from pathlib import Path

#Current working Directory
root = Path(".")

#Folder to create
folders = [
    "app/api",
    "app/core",
    "app/rag",
    "app/services",
    "data",
    "templates",
    "static",
    "uploads",
    "test",
]

#Files to create
files = [
    "app/main.py",
    "ingest_sample_kb.py",
    "requirements.txt",
    "run.py",
    ".env"
]

#Create Folder
for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

for file in files:
    (root / file).touch(exist_ok=True)

print("Proect structure created successfully")