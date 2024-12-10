class ProductionData:
    def __init__(self):
        self.data = []

    def add_data(self, day, production):
        self.data.append({"Day": day, "Production": production})

    def get_data(self):
        return self.data
