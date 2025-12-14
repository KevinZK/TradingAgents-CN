
import os
import sys
from pymongo import MongoClient
import datetime

# Get config from env or defaults
host = os.environ.get("MONGODB_HOST", "mongodb")
port = int(os.environ.get("MONGODB_PORT", 27017))
username = os.environ.get("MONGODB_USERNAME", "admin")
password = os.environ.get("MONGODB_PASSWORD", "tradingagents123")
database = os.environ.get("MONGODB_DATABASE", "tradingagents")
auth_source = os.environ.get("MONGODB_AUTH_SOURCE", "admin")
tushare_token = os.environ.get("TUSHARE_TOKEN")

if not tushare_token:
    print("Error: TUSHARE_TOKEN env var not set!")
    sys.exit(1)

uri = f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource={auth_source}"
print(f"Connecting to MongoDB...")

try:
    client = MongoClient(uri)
    db = client[database]
    config_coll = db.system_configs
    
    # Get active config
    config = config_coll.find_one({"is_active": True}, sort=[("version", -1)])
    
    if not config:
        print("No active config found!")
        sys.exit(1)
        
    print(f"Found active config version: {config.get('version')}")
    
    # Update logic
    # We need to create a new version of config to maintain history
    new_config = config.copy()
    new_config.pop('_id') # Remove _id to insert new doc
    new_config['version'] = config['version'] + 1
    new_config['updated_at'] = datetime.datetime.utcnow()
    
    ds_configs = new_config.get('data_source_configs', [])
    updated = False
    
    for ds in ds_configs:
        if ds.get('type') == 'tushare' or ds.get('name') == 'Tushare':
            print("Updating Tushare config...")
            ds['api_key'] = tushare_token
            ds['enabled'] = True
            updated = True
            break
            
    if updated:
        # Deactivate old config
        config_coll.update_many({"is_active": True}, {"$set": {"is_active": False}})
        
        # Insert new config
        config_coll.insert_one(new_config)
        print(f"Successfully updated configuration to version {new_config['version']}")
        print(f"Tushare Token set to: {tushare_token[:6]}...{tushare_token[-6:]}")
        print(f"Tushare Enabled: True")
    else:
        print("Tushare config not found in data_source_configs!")

except Exception as e:
    print(f"Error: {e}")
