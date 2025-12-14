
import os
import sys
from pymongo import MongoClient
import pprint

# Get config from env or defaults
host = os.environ.get("MONGODB_HOST", "mongodb")
port = int(os.environ.get("MONGODB_PORT", 27017))
username = os.environ.get("MONGODB_USERNAME", "admin")
password = os.environ.get("MONGODB_PASSWORD", "tradingagents123")
database = os.environ.get("MONGODB_DATABASE", "tradingagents")
auth_source = os.environ.get("MONGODB_AUTH_SOURCE", "admin")

uri = f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource={auth_source}"
print(f"Connecting to MongoDB...")

try:
    client = MongoClient(uri)
    db = client[database]
    config_coll = db.system_configs
    
    # Get active config
    config = config_coll.find_one({"is_active": True}, sort=[("version", -1)])
    
    if config:
        print(f"Found active config version: {config.get('version')}")
        ds_configs = config.get('data_source_configs', [])
        for ds in ds_configs:
            if ds.get('type') == 'tushare' or ds.get('name') == 'Tushare':
                print("Tushare config found:")
                pprint.pprint(ds)
    else:
        print("No active config found!")
        
except Exception as e:
    print(f"Error: {e}")
