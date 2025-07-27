import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from config import settings

logger = logging.getLogger(__name__)

class DatabaseProvider:
    """Provides database sessions for central and tenant databases"""
    
    def __init__(self):
        # Central database engine and session factory
        self._central_engine = None
        self._central_session_factory = None
        
        # Tenant database engines (cached by tenant slug)
        self._tenant_engines = {}
        self._tenant_session_factories = {}
    
    async def initialize(self):
        """Initialize database connections"""
        # Initialize central database
        central_url = settings.central_db.connection_string.replace('postgresql://', 'postgresql+asyncpg://')
        self._central_engine = create_async_engine(
            central_url,
            echo=False,  # Set to True for SQL logging
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,  # Limit pool size
            max_overflow=20,  # Allow some overflow
            pool_timeout=30  # Timeout for getting connection from pool
        )
        self._central_session_factory = async_sessionmaker(
            self._central_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def get_central_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a session for the central database"""
        if not self._central_session_factory:
            await self.initialize()
        
        async with self._central_session_factory() as session:
            try:
                yield session
                # Don't auto-commit here - let the caller manage transactions
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def get_tenant_session(self, tenant_slug: str) -> AsyncGenerator[AsyncSession, None]:
        """Get a session for a specific tenant's database"""
        if tenant_slug not in self._tenant_session_factories:
            await self._initialize_tenant_database(tenant_slug)
        
        async with self._tenant_session_factories[tenant_slug]() as session:
            try:
                yield session
                # Don't auto-commit here - let the caller manage transactions
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def _initialize_tenant_database(self, tenant_slug: str):
        """Initialize connection to a tenant's database"""
        # TODO: Get tenant connection string from central database
        # For now, we'll use the tenant database configuration from settings
        database_name = f"{settings.tenant_db.database_prefix}{tenant_slug}{settings.tenant_db.database_suffix}"
        tenant_url = f"postgresql+asyncpg://{settings.tenant_db.username}:{settings.tenant_db.password}@{settings.tenant_db.host}:{settings.tenant_db.port}/{database_name}"
        
        # DEBUG: Log the connection details
        logger.info(f"DEBUG: Connecting to tenant database '{database_name}'")
        logger.info(f"DEBUG: Tenant URL: {tenant_url}")
        logger.info(f"DEBUG: Host: {settings.tenant_db.host}, Port: {settings.tenant_db.port}")
        
        engine = create_async_engine(
            tenant_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,  # Smaller pool for tenant databases
            max_overflow=10,  # Allow some overflow
            pool_timeout=30  # Timeout for getting connection from pool
        )
        
        session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        self._tenant_engines[tenant_slug] = engine
        self._tenant_session_factories[tenant_slug] = session_factory
    
    async def close(self):
        """Close all database connections"""
        if self._central_engine:
            await self._central_engine.dispose()
        
        for engine in self._tenant_engines.values():
            await engine.dispose()
        
        self._tenant_engines.clear()
        self._tenant_session_factories.clear()

# Global instance
database_provider = DatabaseProvider() 