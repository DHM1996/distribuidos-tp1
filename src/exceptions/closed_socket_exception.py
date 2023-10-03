class ClosedSocketException(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return f"El socket se encuentra cerrado"
