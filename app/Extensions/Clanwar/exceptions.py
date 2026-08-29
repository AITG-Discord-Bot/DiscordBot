class StaleClanwarError(Exception):
    """Raised when Discord channel/message for a clanwar no longer exists."""

    def __init__(self, partyid: str):
        self.partyid = partyid
        super().__init__(partyid)
