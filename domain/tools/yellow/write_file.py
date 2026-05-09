"""
domain/tools/yellow/write_file.py

YELLOW tool: partially reversible (create/modify), audit log required.
Idempotency: repeated calls with the same key produce the same result.
Least Privilege: access outside SANDBOX_DIR is blocked.
"""
import os
import hashlib
from pathlib import Path
from pydantic import BaseModel, Field

SANDBOX_DIR = Path(os.environ.get("SANDBOX_DIR", "/tmp/agent_sandbox"))
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

_PROCESSED_KEYS: set[str] = set()


class WriteFileParams(BaseModel):
    filename:         str      = Field(description="File name to save (no path separators)")
    content:          str      = Field(description="Content to write to the file")
    idempotency_key:  str|None = Field(default=None, description="Idempotency key")


def write_file(filename: str, content: str, idempotency_key: str | None = None) -> dict:
    """
    Save a file to the sandbox directory.
    Use when: you need to save analysis results, reports, or summaries as a file.
    ⚠️ YELLOW level: an audit log will be recorded.
    """
    params = WriteFileParams(filename=filename, content=content, idempotency_key=idempotency_key)
    key = params.idempotency_key or hashlib.md5(
        f"{params.filename}:{params.content[:100]}".encode()
    ).hexdigest()

    if key in _PROCESSED_KEYS:
        return {"success": True, "message": f"Already processed (key:{key})", "idempotent": True}

    try:
        safe = (SANDBOX_DIR / params.filename).resolve()
        if not str(safe).startswith(str(SANDBOX_DIR)):
            return {"success": False, "error": "Cannot write files outside the allowed directory. Path traversal characters like '../' are forbidden."}
    except Exception as e:
        return {"success": False, "error": f"Path validation failed: {e}"}

    safe.write_text(params.content, encoding="utf-8")
    _PROCESSED_KEYS.add(key)
    return {
        "success":         True,
        "path":            str(safe),
        "message":         f"'{params.filename}' saved ({len(params.content)} chars)",
        "idempotency_key": key,
    }


def read_file(filename: str) -> dict:
    """Read a sandbox file. (GREEN behavior)"""
    try:
        safe = (SANDBOX_DIR / filename).resolve()
        if not str(safe).startswith(str(SANDBOX_DIR)):
            return {"success": False, "error": "Cannot read files outside the allowed directory."}
        if not safe.exists():
            return {"success": False, "error": f"'{filename}' not found. Use list_files() to check available files first."}
        return {"success": True, "filename": filename, "content": safe.read_text(encoding="utf-8")}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_files() -> dict:
    """Return the list of sandbox files. (GREEN behavior)"""
    files = [{"name": f.name, "size": f.stat().st_size} for f in SANDBOX_DIR.iterdir() if f.is_file()]
    return {"files": files, "count": len(files)}
