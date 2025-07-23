"""
Database abstraction layer for the Content Manager application.
"""
import asyncio
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import MetaData
import structlog

from app.config import get_settings
from app.core.exceptions import DatabaseError


logger = structlog.get_logger()


class Base(DeclarativeBase):
    """Base class for all database models."""
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )


class DatabaseManager:
    """Database manager for handling different database types."""
    
    def __init__(self):
        self.engine = None
        self.async_session_factory = None
        self.settings = get_settings()
        
    async def initialize(self):
        """Initialize database connection."""
        try:
            database_url = self._get_database_url()
            
            # Create async engine
            self.engine = create_async_engine(
                database_url,
                echo=self.settings.debug,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
            
            # Create session factory
            self.async_session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info("Database initialized", database_type=self.settings.database_type)
            
        except Exception as e:
            logger.error("Failed to initialize database", error=str(e))
            raise DatabaseError(f"Database initialization failed: {str(e)}")
    
    def _get_database_url(self) -> str:
        """Get database URL based on database type."""
        base_url = self.settings.database_url
        
        # Convert sync URLs to async for SQLAlchemy 2.0
        if self.settings.database_type == "postgresql":
            if base_url.startswith("postgresql://"):
                return base_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif base_url.startswith("postgres://"):
                return base_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif self.settings.database_type == "mysql":
            if base_url.startswith("mysql://"):
                return base_url.replace("mysql://", "mysql+aiomysql://", 1)
        elif self.settings.database_type == "sqlite":
            if base_url.startswith("sqlite://"):
                return base_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        
        return base_url
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session."""
        if not self.async_session_factory:
            raise DatabaseError("Database not initialized")
        
        async with self.async_session_factory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error("Database session error", error=str(e))
                raise
            finally:
                await session.close()
    
    async def create_tables(self):
        """Create all database tables."""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")
        except Exception as e:
            logger.error("Failed to create tables", error=str(e))
            raise DatabaseError(f"Table creation failed: {str(e)}")
    
    async def close(self):
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")


# Global database manager instance
database_manager = DatabaseManager()


async def init_db():
    """Initialize the database."""
    await database_manager.initialize()
    await database_manager.create_tables()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async for session in database_manager.get_session():
        yield session


# MongoDB support (for non-relational data)
class MongoDBManager:
    """MongoDB manager for document storage."""
    
    def __init__(self):
        self.client = None
        self.database = None
        self.settings = get_settings()
    
    async def initialize(self):
        """Initialize MongoDB connection."""
        if self.settings.database_type != "mongodb":
            return
        
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            
            self.client = AsyncIOMotorClient(self.settings.database_url)
            self.database = self.client.get_default_database()
            
            # Test connection
            await self.client.admin.command('ping')
            
            logger.info("MongoDB initialized")
            
        except Exception as e:
            logger.error("Failed to initialize MongoDB", error=str(e))
            raise DatabaseError(f"MongoDB initialization failed: {str(e)}")
    
    async def get_collection(self, collection_name: str):
        """Get MongoDB collection."""
        if not self.database:
            raise DatabaseError("MongoDB not initialized")
        return self.database[collection_name]
    
    async def close(self):
        """Close MongoDB connections."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connections closed")


# Global MongoDB manager instance
mongodb_manager = MongoDBManager() 