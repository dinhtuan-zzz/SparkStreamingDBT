import json
import logging
import kafka
from typing import List, Any, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError

class KafkaPublisher:
    """
    A robust, configurable Kafka message publisher

    Design Principles:
    - Separate message production from source logic
    - Provide flexible configuration
    - Implement comprehensive error handling
    """
    def __init__(
            self,
            bootstrap_servers: List[str],
            topic: str
    ):
        """
        Initialize Kafka Producer with robust configuration

        Args:
            bootstrap_servers: List of Kafka broker addresses
            topic: Kafka topic to publish messages
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Attempting to use KafkaProducer class: {KafkaProducer}")
        self.logger.info(f"Imported from module: {KafkaProducer.__module__}")
        try:
            # Check the file path of the top-level kafka module if possible
            self.logger.info(f"Top-level kafka module path: {kafka.__file__}")
        except AttributeError:
            self.logger.warning("Could not determine kafka.__file__") 

        try:
            self.producer = KafkaProducer(
                    bootstrap_servers=bootstrap_servers,
                    value_serializer=self._serialize_message,
                    retries=3,
                    acks='all',
                    compression_type='gzip'
            )

            self.topic = topic
            self.logger.info("KafkaProducer instantiated successfully.")
        except TypeError as e:
            self.logger.error(f"TypeError during KafkaProducer init: {e}", exc_info=True) # Log full traceback
            raise
        except Exception as e:
            self.logger.error(f"Kafka Producer initialization failed: {e}")
            raise

    @staticmethod
    def _serialize_message(message: Any) -> bytes:
        """
        Serialize message to JSON bytes

        Args:
            message: Message to serialize

        Returns:
            Serialized message bytes
        """
        try:
            return json.dumps(message).encode('utf-8')
        except TypeError as e:
            logging.error(f"Serializtion error: {e}")
            raise

    def publish_message(
            self,
            message: Any,
            key: Optional[bytes] = None
    ) -> Optional[str]:
        """
        Publish a message to Kafka topic

        Args:
            message: Message to publish
            key: Optional message key for partitioning

        Returns:
            Metadata about published message or None
        """
        try:
            # Send message and get future
            future = self.producer.send(
                    self.topic,
                    value=message,
                    key=key
            )

            # Wait for send confirmation
            record_metadata = future.get(timeout=10)
            self.logger.info(
                    f"Message sent to {record_metadata.topic}, "
                    f"partition {record_metadata.partition}"
            )
        except KafkaError as e:
            self.logger.error(f"Kafka publishing error: {e}")
            return None

    def close(self):
        """
        Gracefully close Kafka producer
        """
        if self.producer:
            self.producer.flush()
            self.producer.close()

            
def create_kafka_publisher(
        env: str = 'development'
     ) -> KafkaPublisher:
    """
    Create Kafka publisher based on environment

    Args:
        env: Environment configuration

    Returns:
        Configured KafkaPublisher instance
    """
    configs = {
        'development': {
            'bootstrap_servers': ['kafka-server:9092'],
            'topic': 'dev_api_data'
        },
        'production': {
            'bootstrap_servers': ['kafka1:9092', 'kafka2:9092'],
            'topic': 'prod_api_data',
            'client_id': 'prod_data_collector'
        }
    }
    config = configs.get(env, configs['development'])
    return KafkaPublisher(**config)
