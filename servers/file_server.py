# We import os and pathlib to handle file system manipulations securely
import os
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
# We import Union to allow confirm_delete to accept either booleans or strings
from typing import Union

# We initialize the FastAPI application for file operations
app = FastAPI(title="FileSystem MCP Server")

# We define and create a local sandbox directory to securely contain all file modifications
SANDBOX_DIR = Path("./sandbox")
SANDBOX_DIR.mkdir(exist_ok=True)

# We define the JSON payload schema with corrected spelling and flexible typing
class FileRequest(BaseModel):
    action: str
    filename: str
    content: str = ""
    # We use Union[bool, str] so the server accepts True, False, "true", or "yes" without throwing validation errors
    confirm_delete: Union[bool, str] = False

@app.post("/mcp")
async def handle_file_operation(payload: FileRequest):
    # We resolve the absolute path inside the sandbox to block path traversal attacks (e.g., '../../')
    target_file = (SANDBOX_DIR / payload.filename).resolve()

    # We verify that the requested file path strictly remains inside our designated sandbox directory
    if not str(target_file).startswith(str(SANDBOX_DIR.resolve())):
        return {"result": "Security Alert: Access denied outside the sandbox folder."}

    try:
        # We handle creating a brand new empty file
        if payload.action == "create":
            target_file.touch(exist_ok=False)
            return {"result": f"File created successfully: {payload.filename}"}

        # We handle reading text from an existing file
        elif payload.action == "read":
            if not target_file.exists():
                return {"result": f"Error: {payload.filename} does not exist."}
            data = target_file.read_text(encoding="utf-8")
            return {"result": f"File content ({payload.filename}):\n{data}"}

        # We handle writing or overwriting text content into a file
        elif payload.action == "write":
            target_file.write_text(payload.content, encoding="utf-8")
            return {"result": f"Wrote {len(payload.content)} characters to {payload.filename}"}

        # We handle file deletion with strict confirmation logic
        elif payload.action == "delete":
            # We convert the payload value to a string and check if it matches valid confirmation words
            is_confirmed = str(payload.confirm_delete).lower() in ["true", "yes", "1", "confirm"]
            
            # We abort the deletion immediately if the confirmation flag is missing or false
            if not is_confirmed:
                return {"result": "Delete Rejected: you must provide 'confirm_delete:true' to remove files."}
            
            if not target_file.exists():
                return {"result": f"Error: File {payload.filename} not found."}
                
            # We permanently delete the file from the disk
            target_file.unlink()
            return {"result": f"File deleted permanently: {payload.filename}"}

        else:
            return {"result": f"Invalid action '{payload.action}'. Valid choices: create, read, write, delete."}

    except FileExistsError:
        return {"result": f"Error: {payload.filename} already exists."}
    except Exception as e:
        return {"result": f"FileSystem Error: {str(e)}"}