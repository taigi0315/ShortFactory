import logging
import os
from datetime import datetime
from typing import Optional

class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        """Initialize the logger with proper formatting and file handling."""
        # Create logs directory if it doesn't exist
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create a timestamp for the log file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"short_factory_{timestamp}.log")
        
        # Configure logging
        self.logger = logging.getLogger("ShortFactory")
        self.logger.setLevel(logging.INFO)
        
        # Create formatters
        file_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_formatter = logging.Formatter(
            "%(message)s"
        )
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """Log an informational message."""
        self.logger.info(message)
    
    def error(self, message: str):
        """Log an error message."""
        self.logger.error(f"❌ ERROR: {message}")
    
    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(f"⚠️ WARNING: {message}")
    
    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(f"🔍 DEBUG: {message}")
    
    def section(self, title: str):
        """Log a section header."""
        self.logger.info(f"\n{'='*50}")
        self.logger.info(f"📑 {title}")
        self.logger.info(f"{'='*50}\n")
    
    def subsection(self, title: str):
        """Log a subsection header."""
        self.logger.info(f"\n{'-'*30}")
        self.logger.info(f"📌 {title}")
        self.logger.info(f"{'-'*30}\n")
    
    def success(self, message: str):
        """Log a success message."""
        self.logger.info(f"✅ SUCCESS: {message}")
    
    def process(self, message: str):
        """Log a process message."""
        self.logger.info(f"⚙️ PROCESSING: {message}")
    
    def result(self, title: str, content: str):
        """Log a result with title and content."""
        self.logger.info(f"\n📊 {title}:")
        self.logger.info(f"{content}\n")
    
    def prompt(self, title: str, content: str):
        """Log a prompt with title and content."""
        self.logger.info(f"\n💭 {title}:")
        self.logger.info(f"{content}\n")
    
    def api_call(self, service: str, action: str, details: Optional[str] = None):
        """Log an API call."""
        message = f"🌐 API CALL - {service}: {action}"
        if details:
            message += f"\nDetails: {details}"
        self.logger.info(message)
    
    def asset_generation(self, asset_type: str, status: str, details: Optional[str] = None):
        """Log asset generation status."""
        message = f"🎨 ASSET GENERATION - {asset_type}: {status}"
        if details:
            message += f"\nDetails: {details}"
        self.logger.info(message) 