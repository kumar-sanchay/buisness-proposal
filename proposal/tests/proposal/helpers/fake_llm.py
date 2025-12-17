from langchain_core.runnables import Runnable


class FakeChatLLM(Runnable):

    def __init__(self, return_value=None):
        self.return_value = return_value
        self.structured_schema = None
    
    def with_structured_output(self, structured_output):
        self.structured_schema = structured_output
        return self
    
    def invoke(self, *args, **kwargs):
        return self.return_value