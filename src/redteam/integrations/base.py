from abc import ABC, abstractmethod

class IntegrationAdapter(ABC):
    """Contract for future integrations. Adapters must document permissions and scope."""

    name: str

    @abstractmethod
    def availability(self) -> tuple[bool, str]:
        """Return whether the optional integration is installed; do not execute it."""
        raise NotImplementedError

class DisabledAdapter(IntegrationAdapter):
    def __init__(self, name: str):
        self.name = name

    def availability(self) -> tuple[bool, str]:
        return False, f"{self.name} integration is intentionally disabled in this starter."
