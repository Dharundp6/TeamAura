import json
from datetime import datetime

def display_dashboard():
    """Display AURA operations dashboard"""
    
    # Load recent logs
    try:
        with open('aura_operations.log', 'r') as f:
            logs = f.readlines()[-20:]  # Last 20 lines
    except:
        logs = []
    
    print("=" * 70)
    print("AURA OPERATIONS DASHBOARD")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("📊 RECENT ACTIVITY:")
    for log in logs[-10:]:
        print(f"  {log.strip()}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    display_dashboard()