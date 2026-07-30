"""
Workflow Engine package.

Public entry point:
    from app.engines.workflow import get_daily_workflow
"""

from .workflow_engine import get_daily_workflow

__all__ = ["get_daily_workflow"]