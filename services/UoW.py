class UnitOfWork:
    def __init__(self, manager):
        self._session_factory = manager.session_factory

    async def __aenter__(self):
        self.session_ctx = self._session_factory.begin()
        self.session = await self.session_ctx.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session_ctx.__aexit__(exc_type, exc_val, exc_tb)
        self.session = None

    async def flush(self):
        await self.session.flush()
