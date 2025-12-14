
import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock environment variables if needed
os.environ['TUSHARE_TOKEN'] = 'invalid_token' # Simulate invalid token to force fallback

def check_akshare():
    try:
        import akshare
        print(f"✅ AKShare is installed. Version: {akshare.__version__}")
        return True
    except ImportError:
        print("❌ AKShare is NOT installed.")
        return False

def check_data_source_manager():
    try:
        # Add project root to path
        sys.path.append(os.getcwd())
        
        from tradingagents.dataflows.data_source_manager import DataSourceManager, ChinaDataSource
        
        manager = DataSourceManager()
        print(f"Available sources: {[s.value for s in manager.available_sources]}")
        print(f"Current source: {manager.current_source.value}")
        print(f"Default source: {manager.default_source.value}")
        
        priority_order = manager._get_data_source_priority_order('000001')
        print(f"Priority order for 000001: {[s.value for s in priority_order]}")
        
        # Test fallback logic directly
        print("\nTesting fallback logic...")
        # Force Tushare as current source
        if ChinaDataSource.TUSHARE in manager.available_sources:
            manager.set_current_source(ChinaDataSource.TUSHARE)
            print("Set current source to Tushare.")
            
            # Try to fetch data (should fail and trigger fallback)
            result = manager.get_stock_data('000001', '2024-01-01', '2024-01-10')
            print(f"Result length: {len(result) if result else 0}")
            if "❌" in result or "失败" in result:
                print(f"Result indicates failure: {result[:100]}...")
            else:
                print("Result indicates success (fallback worked?).")
        else:
            print("Tushare not available for testing.")
            
    except Exception as e:
        print(f"Error checking DataSourceManager: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Checking AKShare installation...")
    if check_akshare():
        print("\nChecking DataSourceManager...")
        check_data_source_manager()
