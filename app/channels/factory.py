from typing import List, Dict, Any
from enum import Enum
from app.channels.base import NotificationChannel
from app.channels.in_app import InAppChannel
from app.channels.email import EmailChannel
from app.channels.sms import SMSChannel

class ChannelType(Enum):
    """Supported notification channel types."""
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"

class ChannelFactory:
    """Factory class to create notification channels with configuration."""
    
    _channel_registry = {
        ChannelType.IN_APP: InAppChannel,
        ChannelType.EMAIL: EmailChannel,
        ChannelType.SMS: SMSChannel
    }
    
    @classmethod
    def create_channel(cls, channel_type: ChannelType, config: Dict[str, Any] = None) -> NotificationChannel:
        """Create a notification channel instance."""
        if channel_type not in cls._channel_registry:
            raise ValueError(f"Unknown channel type: {channel_type}")
        
        channel_class = cls._channel_registry[channel_type]
        return channel_class(config or {})
    
    @classmethod
    def create_channels_from_config(cls, channels_config: List[Dict[str, Any]]) -> List[NotificationChannel]:
        """Create multiple channels from configuration."""
        channels = []
        
        for config in channels_config:
            channel_type_str = config.get("type", "in_app")
            try:
                channel_type = ChannelType(channel_type_str)
                channel_config = config.get("config", {})
                channel = cls.create_channel(channel_type, channel_config)
                channels.append(channel)
            except ValueError as e:
                print(f"Warning: Skipping invalid channel type '{channel_type_str}': {e}")
                
        return channels
    
    @classmethod
    def get_default_channels(cls) -> List[NotificationChannel]:
        """Get default channels for MVP (In-App only)."""
        return [cls.create_channel(ChannelType.IN_APP)]
    
    @classmethod
    def get_available_channel_types(cls) -> List[str]:
        """Get list of available channel types."""
        return [channel_type.value for channel_type in ChannelType]
    
    @classmethod
    def register_channel(cls, channel_type: ChannelType, channel_class: type):
        """Register a new channel type (for future extensibility)."""
        cls._channel_registry[channel_type] = channel_class