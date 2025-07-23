from abc import ABC, abstractmethod


class IFinancialReportService(ABC):
    @abstractmethod
    async def generate_financial_summary(self) -> str:
        pass
    @abstractmethod
    async def send_financial_report(self) -> bool:
        pass
    @abstractmethod
    async def schedule_financial_report_task(self) -> None:
        pass
