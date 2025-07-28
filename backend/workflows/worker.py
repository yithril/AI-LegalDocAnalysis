"""
Temporal worker for running document processing workflows.
"""
import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker
from .document_workflow import (
    DocumentProcessingWorkflow,
    extract_text_from_document,
    classify_document,
    store_document_metadata
)


class DocumentProcessingWorker:
    """Worker for processing document workflows."""
    
    def __init__(self, host: str = "localhost", port: int = 7233):
        self.host = host
        self.port = port
        self.client: Client = None
        self.worker: Worker = None
    
    async def start(self):
        """Start the worker."""
        logging.info("Starting document processing worker...")
        
        # Connect to Temporal server
        self.client = await Client.connect(f"{self.host}:{self.port}")
        
        # Create worker
        self.worker = Worker(
            self.client,
            task_queue="document-processing",
            workflows=[DocumentProcessingWorkflow],
            activities=[
                extract_text_from_document,
                classify_document,
                store_document_metadata
            ]
        )
        
        logging.info("Worker created, starting to run...")
        await self.worker.run()
    
    async def stop(self):
        """Stop the worker."""
        if self.worker:
            await self.worker.shutdown()
        logging.info("Worker stopped.")


async def start_worker():
    """Start the document processing worker."""
    worker = DocumentProcessingWorker()
    await worker.start()


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start the worker
    asyncio.run(start_worker()) 