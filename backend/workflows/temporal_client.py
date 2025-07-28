"""
Temporal client configuration for connecting to the local Temporal server.
"""
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio import workflow, activity
from typing import Optional


class TemporalClient:
    """Temporal client for managing workflow connections."""
    
    def __init__(self, host: str = "localhost", port: int = 7233):
        self.host = host
        self.port = port
        self.client: Optional[Client] = None
    
    async def connect(self) -> Client:
        """Connect to the Temporal server."""
        if not self.client:
            self.client = await Client.connect(f"{self.host}:{self.port}")
        return self.client
    
    async def start_worker(self, task_queue: str, workflows: list, activities: list):
        """Start a Temporal worker."""
        client = await self.connect()
        
        worker = Worker(
            client,
            task_queue=task_queue,
            workflows=workflows,
            activities=activities
        )
        
        await worker.run()
    
    async def start_workflow(self, workflow_type: str, task_queue: str, **kwargs):
        """Start a new workflow execution."""
        client = await self.connect()
        
        handle = await client.start_workflow(
            workflow_type,
            task_queue=task_queue,
            **kwargs
        )
        
        return handle


# Global temporal client instance
temporal_client = TemporalClient() 