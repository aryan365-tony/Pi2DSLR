class BasePostProcessor:
    def process(self, filepath, frames=None):
        raise NotImplementedError
