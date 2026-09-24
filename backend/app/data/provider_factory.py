from app.core.config import settings
from app.data.base import FinancialDataProvider
from app.data.mock_provider import MockDataProvider


def get_data_provider() -> FinancialDataProvider:
    provider = settings.DATA_PROVIDER.lower()
    if provider == "mock":
        return MockDataProvider()
    # Future: FMPProvider, AlphaVantageProvider
    return MockDataProvider()
