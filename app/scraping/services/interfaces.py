from abc import ABC, abstractmethod
from typing import Any, Dict, List


from app.scraping.models.scraping import ScrapingConfig
from typing import Dict
from typing import Any
from typing import Dict
from typing import Any


class IScraperService(ABC):
    """Interface for scraper service."""
    
    @abstractmethod
    async def run_scraping_job(self, config_id: str, source: str, location: str, property_type: str) -> Any:
        """Run a scraping job."""
        pass

    @abstractmethod
    async def create_config(self, config_data: Dict[str, Any], customer_id: str) -> ScrapingConfig:
        """Create a new scraping configuration."""
        pass

    @abstractmethod
    def get_active_configs(self) -> List[ScrapingConfig]:
        """Get all active scraping configurations."""
        pass

class IScheduler(ABC):
    """Interface for scheduler service."""
    
    @abstractmethod
    def start(self):
        """Start the scheduler."""
        pass

    @abstractmethod
    def shutdown(self):
        """Shutdown the scheduler."""
        pass

    @abstractmethod
    def schedule_config(self, config: ScrapingConfig):
        """Schedule scraping jobs for a configuration."""
        pass

    @abstractmethod
    def unschedule_config(self, config_id: str):
        """Remove scheduled jobs for a configuration."""
        pass 