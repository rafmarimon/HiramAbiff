"""
Base agent class module.

This module provides a base agent class with common functionality
for all agents in the HiramAbiff system.
"""

import asyncio
import json
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from src.core.config import settings


class AgentStatus(str, Enum):
    """Agent status enum."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class BaseAgent(ABC):
    """
    Base class for all agents in the HiramAbiff system.
    """
    
    def __init__(self, agent_id: Optional[str] = None, name: str = "BaseAgent"):
        """
        Initialize a base agent.
        
        Args:
            agent_id: Unique identifier for the agent.
            name: Human-readable name for the agent.
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name
        self.status = AgentStatus.IDLE
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.last_run_at = None
        self.error_message = None
        self.result = None
        
        logger.info(f"Initialized agent: {self.name} ({self.agent_id})")
    
    @abstractmethod
    async def run(self, *args, **kwargs) -> Any:
        """
        Run the agent's main task.
        
        Returns:
            Any: The result of the agent's task.
        """
        pass
    
    async def execute(self, *args, **kwargs) -> Any:
        """
        Execute the agent's task with status tracking.
        
        Returns:
            Any: The result of the agent's task.
        """
        if self.status == AgentStatus.RUNNING:
            logger.warning(f"Agent {self.name} already running")
            return None
        
        self.status = AgentStatus.RUNNING
        self.last_run_at = datetime.now()
        self.updated_at = datetime.now()
        self.error_message = None
        
        logger.info(f"Starting agent: {self.name}")
        
        try:
            # Execute with timeout if configured
            if hasattr(settings, "AGENT_TIMEOUT") and settings.AGENT_TIMEOUT > 0:
                self.result = await asyncio.wait_for(
                    self.run(*args, **kwargs),
                    timeout=settings.AGENT_TIMEOUT
                )
            else:
                self.result = await self.run(*args, **kwargs)
            
            self.status = AgentStatus.COMPLETED
            self.updated_at = datetime.now()
            logger.info(f"Agent {self.name} completed successfully")
            return self.result
        except asyncio.TimeoutError:
            self.status = AgentStatus.FAILED
            self.error_message = "Agent execution timed out"
            self.updated_at = datetime.now()
            logger.error(f"Agent {self.name} timed out")
            return None
        except Exception as e:
            self.status = AgentStatus.FAILED
            self.error_message = str(e)
            self.updated_at = datetime.now()
            logger.exception(f"Agent {self.name} failed: {e}")
            return None
    
    def stop(self) -> None:
        """Stop the agent's execution."""
        if self.status == AgentStatus.RUNNING:
            self.status = AgentStatus.STOPPED
            self.updated_at = datetime.now()
            logger.info(f"Agent {self.name} stopped")
    
    def reset(self) -> None:
        """Reset the agent's state."""
        self.status = AgentStatus.IDLE
        self.updated_at = datetime.now()
        self.result = None
        self.error_message = None
        logger.info(f"Agent {self.name} reset")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert agent state to a dictionary.
        
        Returns:
            Dict[str, Any]: Agent state as a dictionary.
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "error_message": self.error_message,
            "result": self.result,
        }
    
    def to_json(self) -> str:
        """
        Convert agent state to JSON.
        
        Returns:
            str: Agent state as a JSON string.
        """
        return json.dumps(self.to_dict(), default=str)
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.name} ({self.agent_id}): {self.status}"
    
    def __repr__(self) -> str:
        """Representation of the agent."""
        return f"<{self.__class__.__name__} id={self.agent_id} name={self.name} status={self.status}>"
 