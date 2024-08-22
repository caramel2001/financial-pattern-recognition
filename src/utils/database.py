class DB:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None