"""
Root endpoint handler module.
"""
from typing import Dict, Any

async def root() -> Dict[str, Any]:
    """Root endpoint providing basic API information"""
    return {"message": "API is running. Use /docs for documentation.", "status": "healthy"} 