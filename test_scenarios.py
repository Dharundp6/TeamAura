from aura_agent import AURAAgent
import time

def run_scenario_suite():
    """Run multiple test scenarios"""
    
    scenarios = {
        "Fiber Failure": "Site DUB-07 has KPI degradation. Investigate.",
        
        "Power Outage": "Site LON-15 shows power alarms and backup battery at 20%. Check status.",
        
        "Multiple Sites": "We're seeing issues at DUB-07, LON-15, and PAR-03. Please triage.",
        
        "False Alarm": "Alert received for DUB-07 but KPIs look normal. Investigate.",
        
        "Capacity Issue": "Users complaining about slow data at DUB-07 during peak hours."
    }
    
    for name, scenario in scenarios.items():
        print("\n" + "=" * 70)
        print(f"TEST SCENARIO: {name}")
        print("=" * 70)
        
        agent = AURAAgent()
        
        print(f"\n👤 Operator: {scenario}")
        print("\n🤖 AURA is thinking...\n")
        
        response = agent.process_message(scenario)
        print(f"\n🤖 AURA: {response}\n")
        
        print("\n⏳ Waiting 10 seconds before next scenario...")
        time.sleep(10)

if __name__ == "__main__":
    run_scenario_suite()