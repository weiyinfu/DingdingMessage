import platform
import os

if platform.system() == "Windows":
    db_path = os.path.join(os.path.expanduser("~"), "ding")
else:
    db_path = "/data/ding"
if not os.path.exists(db_path):
    os.makedirs(db_path)

if __name__ == "__main__":
    print(db_path)
