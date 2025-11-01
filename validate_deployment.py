#!/usr/bin/env python3
"""
Complete validation of AURA MCP Gateway deployment
"""

import json
import requests
import time

def validate_gateway():
    """Run comprehensive validation tests"""
    
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║        AURA MCP Gateway - Deployment Validation                   ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()
    
    # Load configuration
    try:
        with open('gateway_config.json', 'r') as f:
            config = json.load(f)
        endpoint = config['endpoint']
        print(f"✅ Configuration loaded")
        print(f"   Endpoint: {endpoint}")
    except FileNotFoundError:
        print("❌ gateway_config.json not found!")
        print("   Run ./create_api_gateway.sh first")
        return False
    
    print()
    
    # Validation tests
    tests = [
        {
            "category": "Nokia Adapter",
            "tests": [
                ("Cell KPIs", {"tool": "get_cell_kpis", "target": "DUB-07"}),
                ("Fiber Latency", {"tool": "measure_link_latency", "target": "DUB-07-FIBER"}),
                ("NTN Latency", {"tool": "measure_link_latency", "target": "DUB-07-NTN"}),
                ("Failover", {"tool": "initiate_ntn_failover", "target": "DUB-07"}),
            ]
        },
        {
            "category": "Ericsson Adapter",
            "tests": [
                ("Cell KPIs", {"tool": "get_cell_kpis", "target": "LON-15"}),
                ("Link Latency", {"tool": "measure_link_latency", "target": "LON-15-FIBER"}),
            ]
        },
        {
            "category": "Cisco Adapter",
            "tests": [
                ("Device KPIs", {"tool": "get_cell_kpis", "target": "PAR-03"}),
                ("Path Latency", {"tool": "measure_link_latency", "target": "PAR-03-MPLS"}),
            ]
        },
    ]
    
    total_tests = sum(len(cat["tests"]) for cat in tests)
    passed = 0
    failed = 0
    
    for category in tests:
        print(f"\n{'='*70}")
        print(f"Testing: {category['category']}")
        print(f"{'='*70}")
        
        for test_name, payload in category["tests"]:
            print(f"\n  ▶ {test_name}")
            print(f"    Payload: {json.dumps(payload)}")
            
            try:
                response = requests.post(
                    endpoint,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    vendor = data.get('vendor', 'Unknown')
                    success = data.get('success', False)
                    
                    if success:
                        print(f"    ✅ PASS - Vendor: {vendor}")
                        print(f"       Response: {json.dumps(data.get('data', {}), indent=8)[:200]}...")
                        passed += 1
                    else:
                        print(f"    ❌ FAIL - Success flag is False")
                        failed += 1
                else:
                    print(f"    ❌ FAIL - HTTP {response.status_code}")
                    print(f"       {response.text[:200]}")
                    failed += 1
                    
            except Exception as e:
                print(f"    ❌ FAIL - Exception: {str(e)}")
                failed += 1
            
            time.sleep(1)  # Rate limiting
    
    # Summary
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                      VALIDATION SUMMARY                            ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()
    print(f"Total Tests:  {total_tests}")
    print(f"✅ Passed:     {passed}")
    print(f"❌ Failed:     {failed}")
    print(f"Success Rate: {(passed/total_tests*100):.1f}%")
    print()
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Gateway is ready for production.")
        print()
        print("Next Steps:")
        print("  1. Run: python3 aura_with_gateway.py")
        print("  2. Test end-to-end agent workflow")
        print("  3. Proceed to Phase 3: AgentCore deployment")
        return True
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    validate_gateway() # Documentation