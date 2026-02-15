class BaseMode:
    name = "Base"

    def capture(self, app, filename):
        raise NotImplementedError
