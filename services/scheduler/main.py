"""
Main entry point for Scheduler Service
"""

import asyncio
import logging
import sys

# Add parent directory to Python path for shared imports
sys.path.append('/home/dre/Desktop/Github/OmniPriceX')

from app.service import serve

def main():
    """Main entry point"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("scheduler_service.log")
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting OmniPriceX Scheduler Service...")
    
    try:
        # Run the gRPC server
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("🛑 Scheduler Service stopped by user")
    except Exception as e:
        logger.error(f"❌ Scheduler Service crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
