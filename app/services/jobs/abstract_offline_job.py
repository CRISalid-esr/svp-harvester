from abc import ABC, abstractmethod


class AbstractOfflineJob(ABC):
    """
    Abstract class for offline jobs.
    """

    @abstractmethod
    async def run(self):
        """
        Run the job.
        """
        raise NotImplementedError
