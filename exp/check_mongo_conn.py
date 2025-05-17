import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.mongoDB import LocalMongoDB

if __name__ == "__main__":
    mongo = LocalMongoDB()
    mongo.check_db_connection()