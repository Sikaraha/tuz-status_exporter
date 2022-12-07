from yaml import safe_load
from os import path

class settings:
    def __init__(self, f_path=path.abspath(__file__).replace('.py', '.yml')):
        self.f_path = f_path

    def read(self):
        with open(self.f_path, 'r') as file:
            data = safe_load(file)
        return data
