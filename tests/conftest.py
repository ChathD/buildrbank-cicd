"""
Fake keys, set before anything imports the app.

app/settings.py refuses to start without OPENROUTER_API_KEY, SUPABASE_URL
and SUPABASE_KEY. On your laptop they come from .env. On GitHub's machine
there is no .env, so we put obvious fakes here.

`setdefault` means a real value already in the environment wins. And because
load_dotenv() never overwrites what is already set, these fakes also win over
your real .env when you run pytest locally. The tests behave the same in both
places, which is the only way a test is worth anything.

Nothing in the test suite calls a model or a database, so fakes are enough.
"""
import os

os.environ.setdefault("OPENROUTER_API_KEY", "test-key-not-real")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key-not-real")
