import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

# Load .env
load_dotenv()

# Configuration
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "opsmind-incidents")

if not HINDSIGHT_API_KEY:
    raise ValueError("HINDSIGHT_API_KEY is missing from .env")

# Connect to Hindsight Cloud
client = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=HINDSIGHT_API_KEY,
)

print("Connected to Hindsight Cloud.")

# Create our incident memory bank
try:
    client.create_bank(
        bank_id=BANK_ID,
        name="OpsMind Incident Memory",
    )
    print(f"Memory bank created: {BANK_ID}")
except Exception as e:
    print(f"Bank may already exist: {e}")

# Store our first incident
incident = """
Incident ID: INC-001

Service: Payment API

Symptoms:
- API latency increased to 4.5 seconds
- HTTP 500 error rate reached 35%
- Database connection utilization reached 100%

Root Cause:
The database connection pool was exhausted.

Resolution:
The connection pool size was increased and the Payment API was restarted.

Outcome:
API latency returned to normal and the error rate dropped below 1%.

Important lesson:
When Payment API latency and HTTP 500 errors increase together with
100% database connection utilization, check for database connection
pool exhaustion.
"""

print("\nStoring incident in Hindsight...")

client.retain(
    bank_id=BANK_ID,
    content=incident,
    context="SRE production incident",
    metadata={
        "incident_id": "INC-001",
        "service": "payment-api",
        "severity": "critical",
    },
)

print("Incident stored successfully.")

# Search memory
query = """
Have we seen a previous Payment API incident involving high latency,
HTTP 500 errors, and database connection pool exhaustion?
"""

print("\nSearching Hindsight memory...")

result = client.recall(
    bank_id=BANK_ID,
    query=query,
)

print("\n========== RECALLED MEMORIES ==========\n")

if not result.results:
    print("No memories found.")
else:
    for memory in result.results:
        print(memory.text)
        print("--------------------------------------")

print("\nMemory test complete.")