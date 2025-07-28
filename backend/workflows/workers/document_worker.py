"""
Document worker for processing document workflows.
"""
import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker
from ..document_workflow import DocumentWorkflow
from ..activities.document_processing.validation_activities import check_document_exists, validate_file_type
from ..activities.document_processing.storage_activities import save_document_info


class DocumentWorker:
    """Worker for document processing."""
    
    def __init__(self, host: str = "localhost", port: int = 7233):
        self.host = host
        self.port = port
        self.client: Client = None
        self.worker: Worker = None
    
    async def start(self):
        """Start the worker."""
        logging.info("Starting document worker...")
        
        # Connect to Temporal server
        self.client = await Client.connect(f"{self.host}:{self.port}")
        
        # Create worker
        self.worker = Worker(
            self.client,
            task_queue="document-processing",
            workflows=[DocumentWorkflow],
            activities=[check_document_exists, validate_file_type, save_document_info]
        )
        
        logging.info("Document worker created, starting to run...")
        await self.worker.run()
    
    async def stop(self):
        """Stop the worker."""
        if self.worker:
            await self.worker.shutdown()
        logging.info("Document worker stopped.")


async def start_document_worker():
    """Start the document worker."""
    worker = DocumentWorker()
    await worker.start()


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start the worker
    asyncio.run(start_document_worker()) 