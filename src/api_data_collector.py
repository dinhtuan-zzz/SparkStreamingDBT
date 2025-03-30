import requests
import logging
from typing import Dict, Any, Optional
from .kafka_producer_util import KafkaPublisher, create_kafka_publisher
class APIDataCollector:
    """
    Decoupled API data collection with flexible publishing
    """
    def __init__(
            self, 
            api_url: str,
            publisher: Optional[KafkaPublisher] = None
    ):
        """
        Initialize API collector
        
        Args:
            api_url: Source API endpoint
            publisher: Optional Kafka publisher
        """
        self.api_url = api_url
        self.publisher = publisher
        self.logger = logging.getLogger(self.__class__.__name__)

    def fetch_data(
            self,
            headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch data from API with robust error handling

        Args:
            headers: Optional request headers

        Returns:
            Parsed JSON response or None
        """
        try:
            response = requests.get(
                    self.api_url,
                    headers=headers,
                    timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"API Request Error: {e}")
            return None

    def process_and_publish(
            self,
            headers: Optional[Dict[str, str]] = None
    ):
        """
        Fetch and publish data to Kafka
        
        Args:
            headers: Optional request headers
        
        Returns:
            Whether publishing was successful
        """
        if not self.publisher:
            self.logger.warning("No publisher configured")
            return False
        data_list = self.fetch_data(headers)
        
        if not data_list:
            return False
        for data in data_list:
            result = self.publisher.publish_message(data)

def stream():
    # Environment-based configuration
    kafka_publisher = create_kafka_publisher('development')

    try:
        collector = APIDataCollector(
                api_url='http://api-generator:8000/v2/random-data-list',
            publisher=kafka_publisher
        )

        # Optional: Add custom headers
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Send list of data to kafka
        collector.process_and_publish(headers)
        

    finally:
        # Always close resources
        kafka_publisher.close()

if __name__ == "__main__":
     logging.basicConfig(level=logging.INFO)
     stream()


