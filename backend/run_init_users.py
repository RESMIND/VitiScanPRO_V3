import sys
import os

# Adaugă calea absolută la sys.path pentru a recunoaște "app"
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.init_users import insert_test_user
import asyncio

asyncio.run(insert_test_user())
