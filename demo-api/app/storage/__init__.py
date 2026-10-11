from app.storage.base import Store
from app.storage.memory import InMemoryStore

# Change this line to switch storage backends.
store: Store = InMemoryStore()
