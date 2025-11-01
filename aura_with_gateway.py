#!/usr/bin/env python3
"""
AURA Agent with MCP Gateway Integration
Connects to AWS Lambda-based vendor adapters via API Gateway
"""

import boto3
import json
import requests
from typing import List, Dict, Callable, Any
from dataclasses import dataclass
import re
import time
from botocore.exceptions import ClientError

# Load gateway configuration
try:
    with open('gateway_config.json', 'r') as f:
        GATEWAY_CONFIG = json.load(f)
    GATEWAY_ENDPOINT = GATEWAY_CONFIG['endpoint']
    USE_GATEWAY = True
    print(f"✅ Gateway configuration loaded: {GATEWAY_ENDPOINT}")
except FileNotFoundError:
    print("⚠️  No gateway configuration found. Using local mock data.")
    USE_GATEWAY = False
    GATEWAY_ENDPOINT = None

# Initialize Bedrock client
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

# Model configuration
CLAUDE_MODEL = 'us.anthropic.claude-sonnet-4-20250514-v1:0'

# Rate limiting configuration
RETRY_DELAY = 3
MAX_RETRIES = 5
INTER_CALL_DELAY = 3

# --- Tool Definitions with Gateway Integration ---

@dataclass
class Tool:
    """Represents a tool that the agent can use"""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, str]

def call_gateway(tool: str, target: str) -> dict:
    """Call the MCP Gateway API"""
    try:
        response = requests.post(
            GATEWAY_ENDPOINT,
            json={
                "tool": tool,
                "target": target
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {})
        else:
            return {
                "error": f"Gateway returned status {response.status_code}",
                "details": response.text
            }
    except Exception as e:
        return {
            "error": "Gateway request failed",
            "details": str(e)
        }

def get_cell_kpis(cell_id: str) -> dict:
    """
    Retrieves Key Performance Indicators (KPIs) for a specific network cell.
    Routes through MCP Gateway to appropriate vendor adapter.
    """
    print(f"🔍 Checking KPIs for {cell_id}...")
    
    if USE_GATEWAY:
        print(f"   → Calling MCP Gateway...")
        result = call_gateway("get_cell_kpis", cell_id)
        return result
    else:
        # Fallback to local mock
        time.sleep(0.5)
        if "DUB-07" in cell_id:
            return {"status": "HEALTHY", "radio_signal": -75, "packet_loss": "0.1%"}
        return {"status": "UNKNOWN", "error": "Cell ID not found"}

def measure_link_latency(link_id: str) -> dict:
    """
    Measures latency on a specific backhaul link (fiber or NTN).
    Routes through MCP Gateway to appropriate vendor adapter.
    """
    print(f"📡 Measuring latency for {link_id}...")
    
    if USE_GATEWAY:
        print(f"   → Calling MCP Gateway...")
        result = call_gateway("measure_link_latency", link_id)
        return result
    else:
        # Fallback to local mock
        time.sleep(0.5)
        if "DUB-07-FIBER" in link_id:
            return {"status": "DEGRADED", "latency_ms": 500, "packet_loss": "45%"}
        if "DUB-07-NTN" in link_id:
            return {"status": "HEALTHY", "latency_ms": 120, "packet_loss": "0.5%"}
        return {"status": "HEALTHY", "latency_ms": 10, "packet_loss": "0%"}

def initiate_ntn_failover(site_id: str) -> dict:
    """
    Initiates a traffic failover to the Non-Terrestrial Network (NTN) backup.
    Routes through MCP Gateway to appropriate vendor adapter.
    This is a SERVICE-IMPACTING change.
    """
    print(f"⚠️  EXECUTING NTN FAILOVER for {site_id}...")
    
    if USE_GATEWAY:
        print(f"   → Calling MCP Gateway...")
        result = call_gateway("initiate_ntn_failover", site_id)
        return result
    else:
        # Fallback to local mock
        time.sleep(1)
        return {"status": "SUCCESS", "new_active_link": "DUB-07-NTN"}

# --- Tool Registry ---

TOOLS = [
    Tool(
        name="get_cell_kpis",
        description="Retrieves Key Performance Indicators (KPIs) for a specific network cell via MCP Gateway. Routes to the appropriate vendor adapter (Nokia, Ericsson, Cisco).",
        function=get_cell_kpis,
        parameters={"cell_id": "The ID of the cell to check (e.g., 'DUB-07', 'LON-15', 'PAR-03')"}
    ),
    Tool(
        name="measure_link_latency",
        description="Measures latency on a specific backhaul link (fiber or NTN) via MCP Gateway. Routes to the appropriate vendor adapter.",
        function=measure_link_latency,
        parameters={"link_id": "The ID of the link to measure (e.g., 'DUB-07-FIBER' or 'DUB-07-NTN')"}
    ),
    Tool(
        name="initiate_ntn_failover",
        description="Initiates a traffic failover to the Non-Terrestrial Network (NTN) backup via MCP Gateway. This is a SERVICE-IMPACTING change and requires human approval.",
        function=initiate_ntn_failover,
        parameters={"site_id": "The site ID to failover (e.g., 'DUB-07')"}
    )
]

# --- Agent Implementation ---

class AURAAgent:
    """
    AURA: Autonomous network operations agent
    Implements a reasoning loop with tool calling capability
    Now integrated with MCP Gateway for multi-vendor support
    """
    
    def __init__(self, model_id: str = CLAUDE_MODEL):
        self.model_id = model_id
        self.conversation_history: List[Dict] = []
        self.system_prompt = """You are AURA, an autonomous network operations agent for multi-vendor telecommunications networks. Your goal is to diagnose and resolve network faults across Nokia, Ericsson, and Cisco infrastructure.

Your workflow:
1. INVESTIGATE: First, investigate all parts of the problem (e.g., RAN, Transport) using available tools. The tools automatically route to the correct vendor.
2. ANALYZE: Synthesize the findings to determine the root cause.
3. PROPOSE: Propose a remediation plan with clear steps.
4. APPROVAL: If the plan is service-impacting (like a failover), you MUST ask for human-in-the-loop approval before executing.
5. EXECUTE: After approval, execute the remediation.
6. VERIFY: Verify the fix was successful.

Available tools (all route through MCP Gateway to vendor-specific adapters):
- get_cell_kpis: Check cell site health (supports DUB-07 [Nokia], LON-15 [Ericsson], PAR-03 [Cisco])
- measure_link_latency: Measure backhaul link performance
- initiate_ntn_failover: Execute failover (REQUIRES APPROVAL)

When you need to use a tool, respond with:
TOOL_CALL: tool_name(parameter_value)

Example: TOOL_CALL: get_cell_kpis(DUB-07)

Always explain your reasoning before and after tool calls."""
        
    def _format_tools_description(self) -> str:
        """Format tools for the system prompt"""
        tools_desc = "\n\nAvailable Tools:\n"
        for tool in TOOLS:
            tools_desc += f"\n- {tool.name}: {tool.description}\n"
            tools_desc += f"  Parameters: {tool.parameters}\n"
        return tools_desc
    
    def _parse_tool_call(self, response: str) -> tuple:
        """Extract tool call from agent response"""
        pattern = r'TOOL_CALL:\s*(\w+)\(([^)]+)\)'
        match = re.search(pattern, response)
        
        if match:
            tool_name = match.group(1)
            param = match.group(2).strip().strip('"').strip("'")
            return tool_name, param
        return None, None
    
    def _execute_tool(self, tool_name: str, param: str) -> dict:
        """Execute a tool by name"""
        for tool in TOOLS:
            if tool.name == tool_name:
                try:
                    result = tool.function(param)
                    return {"success": True, "result": result}
                except Exception as e:
                    return {"success": False, "error": str(e)}
        return {"success": False, "error": f"Tool '{tool_name}' not found"}
    
    def _call_claude_with_retry(self, messages: List[Dict]) -> str:
        """Make API call to Claude with exponential backoff retry"""
        for attempt in range(MAX_RETRIES):
            try:
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2000,
                    "system": self.system_prompt + self._format_tools_description(),
                    "messages": messages
                }
                
                response = bedrock_runtime.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(request_body)
                )
                
                response_body = json.loads(response['body'].read())
                time.sleep(INTER_CALL_DELAY)
                
                return response_body['content'][0]['text']
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                
                if error_code == 'ThrottlingException':
                    if attempt < MAX_RETRIES - 1:
                        wait_time = RETRY_DELAY * (2 ** attempt)
                        print(f"⏳ Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{MAX_RETRIES}...")
                        time.sleep(wait_time)
                    else:
                        return f"Error: Rate limit exceeded after {MAX_RETRIES} retries. Please wait a moment and try again."
                else:
                    return f"AWS Error ({error_code}): {str(e)}"
                    
            except Exception as e:
                return f"Error calling Claude: {str(e)}"
        
        return "Error: Maximum retries exceeded"
    
    def process_message(self, user_message: str, max_iterations: int = 5) -> str:
        """Process a user message with tool calling loop"""
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        iteration = 0
        
        while iteration < max_iterations:
            response = self._call_claude_with_retry(self.conversation_history)
            
            if response.startswith("Error"):
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                return response
            
            tool_name, param = self._parse_tool_call(response)
            
            if tool_name:
                print(f"\n🔧 Agent wants to use tool: {tool_name}({param})")
                
                tool_result = self._execute_tool(tool_name, param)
                
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                
                tool_message = f"Tool result from {tool_name}({param}):\n{json.dumps(tool_result, indent=2)}"
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_message
                })
                
                iteration += 1
            else:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                return response
        
        return "Maximum iterations reached. Please provide more guidance."
    
    def reset(self):
        """Reset conversation history"""
        self.conversation_history = []


# --- Interactive Mode ---

def interactive_mode():
    """Run AURA agent interactively"""
    
    agent = AURAAgent()
    
    print("=" * 70)
    print("AURA Network Operations Agent - MCP Gateway Integration")
    print("=" * 70)
    
    if USE_GATEWAY:
        print(f"🌐 Gateway: {GATEWAY_ENDPOINT}")
        print("✅ Multi-vendor support enabled (Nokia, Ericsson, Cisco)")
    else:
        print("⚠️  Running in local mock mode")
    
    print("\nCommands:")
    print("  - Type your message to interact with AURA")
    print("  - Type 'reset' to clear conversation history")
    print("  - Type 'quit' to exit")
    print("=" * 70)
    
    # Preset scenarios for quick testing
    scenarios = {
        '1': "I see KPI degradation at site DUB-07. Please investigate the issue.",
        '2': "Check the status of site LON-15 (Ericsson network).",
        '3': "The fiber link issue looks correct. Please propose a remediation plan and ask for approval if needed.",
        '4': "You are approved to proceed with the NTN failover.",
        '5': "APPROVED",
    }
    
    print("\nQuick scenarios:")
    for key, scenario in scenarios.items():
        print(f"  {key}. {scenario[:60]}...")
    print()
    
    while True:
        user_input = input("\n👤 You: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if user_input.lower() == 'reset':
            agent.reset()
            print("🔄 Conversation history cleared.")
            continue
        
        # Check if user entered a scenario number
        if user_input in scenarios:
            user_input = scenarios[user_input]
            print(f"   (Using scenario: {user_input})")
        
        print("\n🤖 AURA is thinking...\n")
        
        try:
            response = agent.process_message(user_input)
            print(f"\n🤖 AURA:\n{response}\n")
            
            # Automatic delay to avoid rate limiting
            print("⏳ Waiting 5 seconds to avoid rate limits...")
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    interactive_mode()