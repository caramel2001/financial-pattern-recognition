class MacroBase:
    def __init__(self, data, **kwargs):
        self.data = data
        self.kwargs = kwargs
    
    def run(self):
        raise NotImplementedError("The run method is not implemented")

class MacroIndia(MacroBase):
    def __init__(self, data, **kwargs):
        super().__init__(data, **kwargs)
    
    def run(self):
        print("Running the MacroIndia class")

class MacroUS(MacroBase):
    def __init__(self, data, **kwargs):
        super().__init__(data, **kwargs)
    
    def run(self):
        print("Running the MacroUS class")

class MacroCrypto(MacroBase):
    def __init__(self, data, **kwargs):
        super().__init__(data, **kwargs)
    
    def run(self):
        print("Running the MacroCrypto class")