"""
Logging configuration for LabAcc Copilot

This sets up logging to both console and file for debugging and monitoring.
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

def setup_logging(log_dir: str = "logs", log_level: str = "INFO"):
    """
    Configure logging for the application
    
    Args:
        log_dir: Directory to save log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler for all logs (only INFO and above for cleaner logs)
    file_handler = logging.handlers.RotatingFileHandler(
        log_path / f"labacc_copilot_{datetime.now().strftime('%Y%m%d')}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)  # Changed from DEBUG to INFO
    file_handler.setFormatter(detailed_formatter)
    
    # File handler for agent conversations
    conversation_handler = logging.handlers.RotatingFileHandler(
        log_path / f"conversations_{datetime.now().strftime('%Y%m%d')}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    conversation_handler.setLevel(logging.INFO)
    conversation_handler.setFormatter(simple_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(simple_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)  # Changed from DEBUG to INFO
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Configure conversation logger
    conversation_logger = logging.getLogger('conversation')
    conversation_logger.addHandler(conversation_handler)
    conversation_logger.setLevel(logging.INFO)
    
    # Reduce noise from libraries - Only show ERRORS for most external libraries
    # HTTP/Web libraries
    logging.getLogger('httpx').setLevel(logging.ERROR)
    logging.getLogger('httpcore').setLevel(logging.ERROR)
    logging.getLogger('uvicorn.access').setLevel(logging.ERROR)
    logging.getLogger('uvicorn.error').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('aiohttp').setLevel(logging.ERROR)
    
    # PDF processing libraries (extremely verbose!)
    logging.getLogger('pdfminer').setLevel(logging.ERROR)
    logging.getLogger('pdfminer.psparser').setLevel(logging.CRITICAL)
    logging.getLogger('pdfminer.pdfdocument').setLevel(logging.CRITICAL)
    logging.getLogger('pdfminer.pdfinterp').setLevel(logging.CRITICAL)
    logging.getLogger('pdfminer.converter').setLevel(logging.ERROR)
    logging.getLogger('pdfminer.layout').setLevel(logging.ERROR)
    logging.getLogger('pdfminer.pdfpage').setLevel(logging.ERROR)
    
    # MinerU/magic-pdf
    logging.getLogger('magic_pdf').setLevel(logging.ERROR)
    logging.getLogger('magic_pdf.libs').setLevel(logging.ERROR)
    logging.getLogger('magic_pdf.model').setLevel(logging.ERROR)
    logging.getLogger('magic_pdf.pipe').setLevel(logging.ERROR)
    
    # Language detection
    logging.getLogger('fast_langdetect').setLevel(logging.CRITICAL)
    
    # ML/AI libraries
    logging.getLogger('transformers').setLevel(logging.ERROR)
    logging.getLogger('torch').setLevel(logging.ERROR)
    logging.getLogger('sentence_transformers').setLevel(logging.ERROR)
    
    # OpenAI/LangChain libraries
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('openai._base_client').setLevel(logging.ERROR)
    logging.getLogger('langchain').setLevel(logging.WARNING)
    logging.getLogger('langgraph').setLevel(logging.WARNING)
    
    # Other verbose libraries
    logging.getLogger('PIL').setLevel(logging.ERROR)
    logging.getLogger('python_multipart').setLevel(logging.ERROR)
    logging.getLogger('multipart').setLevel(logging.ERROR)
    logging.getLogger('watchfiles').setLevel(logging.ERROR)
    
    # Our app components - keep at INFO level for important messages
    logging.getLogger('src.api').setLevel(logging.INFO)
    logging.getLogger('src.agents').setLevel(logging.INFO)
    logging.getLogger('src.memory').setLevel(logging.INFO)
    logging.getLogger('src.components').setLevel(logging.INFO)
    
    return root_logger

def log_conversation(user_query: str, agent_response: str, session_id: str = "unknown"):
    """
    Log a conversation turn to the conversation log
    
    Args:
        user_query: User's input message
        agent_response: Agent's response
        session_id: Session identifier
    """
    conversation_logger = logging.getLogger('conversation')
    conversation_logger.info(f"[Session: {session_id}]")
    conversation_logger.info(f"User: {user_query}")
    conversation_logger.info(f"Agent: {agent_response[:500]}...")  # Truncate long responses
    conversation_logger.info("-" * 80)