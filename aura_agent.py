import boto3
import json
from typing import List, Dict, Callable, Any
from dataclasses import dataclass
import re
import time
from botocore.exceptions import ClientError

# Initialize Bedrock client
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

# Model configuration
CLAUDE_MODEL = 'us.anthropic.claude-sonnet-4-20250514-v1:0'

# Rate limiting configuration
RETRY_DELAY = 2  # seconds between retries
MAX_RETRIES = 3
INTER_CALL_DELAY = 1  # seconds between normal API calls

# --- Tool Definitions ---

@dataclass
class Tool:
    """Represents a tool that the agent can use"""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, str]

def get_cell_kpis(cell_id: str) -> dict:
    """
    Retrieves Key Performance Indicators (KPIs) for a specific network cell.
    (This would call a vendor's RAN management API).
    """
    print(f"🔍 Checking KPIs for {cell_id}...")
    time.sleep(0.5)  # Simulate API call
    # Mocked data:
    if "DUB-07" in cell_id:
        return {"status": "HEALTHY", "radio_signal": -75, "packet_loss": "0.1%"}
    return {"status": "UNKNOWN", "error": "Cell ID not found"}

def measure_link_latency(link_id: str) -> dict:
    """
    Measures latency on a specific backhaul link (fiber or NTN).
    (This would call a transport network API).
    """
    print(f"📡 Measuring latency for {link_id}...")
    time.sleep(0.5)  # Simulate API call
    # Mocked data for the demo scenario:
    if "DUB-07-FIBER" in link_id:
        return {"status": "DEGRADED", "latency_ms": 500, "packet_loss": "45%"}
    if "DUB-07-NTN" in link_id:
        return {"status": "HEALTHY", "latency_ms": 120, "packet_loss": "0.5%"}
    return {"status": "HEALTHY", "latency_ms": 10, "packet_loss": "0%"}

def initiate_ntn_failover(site_id: str) -> dict:
    """
    Initiates a traffic failover to the Non-Terrestrial Network (NTN) backup.
    (This is a service-impacting change).
    """
    print(f"⚠️  EXECUTING NTN FAILOVER for {site_id}...")
    time.sleep(1)  # Simulate API call
    # Mocked response:
    return {"status": "SUCCESS", "new_active_link": "DUB-07-NTN"}

# --- Tool Registry ---

TOOLS = [
    Tool(
        name="get_cell_kpis",
        description="Retrieves Key Performance Indicators (KPIs) for a specific network cell. Use this to check the health status of a cell site.",
        function=get_cell_kpis,
        parameters={"cell_id": "The ID of the cell to check (e.g., 'DUB-07')"}
    ),
    Tool(
        name="measure_link_latency",
        description="Measures latency on a specific backhaul link (fiber or NTN). Use this to diagnose transport network issues.",
        function=measure_link_latency,
        parameters={"link_id": "The ID of the link to measure (e.g., 'DUB-07-FIBER' or 'DUB-07-NTN')"}
    ),
    Tool(
        name="initiate_ntn_failover",
        description="Initiates a traffic failover to the Non-Terrestrial Network (NTN) backup. This is a SERVICE-IMPACTING change and requires human approval.",
        function=initiate_ntn_failover,
        parameters={"site_id": "The site ID to failover (e.g., 'DUB-07')"}
    )
]

# --- Agent Implementation ---

class AURAAgent:
    """
    AURA: Autonomous network operations agent
    Implements a reasoning loop with tool calling capability
    """
    
    def __init__(self, model_id: str = CLAUDE_MODEL):
        self.model_id = model_id
        self.conversation_history: List[Dict] = []
        self.system_prompt = """You are AURA, an autonomous network operations agent. Your goal is to diagnose and resolve network faults.

Your workflow:
1. INVESTIGATE: First, investigate all parts of the problem (e.g., RAN, Transport) using available tools.
2. ANALYZE: Synthesize the findings to determine the root cause.
3. PROPOSE: Propose a remediation plan with clear steps.
4. APPROVAL: If the plan is service-impacting (like a failover), you MUST ask for human-in-the-loop approval before executing.
5. EXECUTE: After approval, execute the remediation.
6. VERIFY: Verify the fix was successful.

Available tools:
- get_cell_kpis: Check cell site health
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
        # Look for pattern: TOOL_CALL: tool_name(param)
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
                
                # Add delay between successful calls to avoid rate limiting
                time.sleep(INTER_CALL_DELAY)
                
                return response_body['content'][0]['text']
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                
                if error_code == 'ThrottlingException':
                    if attempt < MAX_RETRIES - 1:
                        wait_time = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
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
        """
        Process a user message with tool calling loop
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        iteration = 0
        
        while iteration < max_iterations:
            # Get response from Claude with retry logic
            response = self._call_claude_with_retry(self.conversation_history)
            
            # Check if we got an error
            if response.startswith("Error"):
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                return response
            
            # Check for tool call
            tool_name, param = self._parse_tool_call(response)
            
            if tool_name:
                print(f"\n🔧 Agent wants to use tool: {tool_name}({param})")
                
                # Execute tool
                tool_result = self._execute_tool(tool_name, param)
                
                # Add assistant response and tool result to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                
                # Add tool result as user message
                tool_message = f"Tool result from {tool_name}({param}):\n{json.dumps(tool_result, indent=2)}"
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_message
                })
                
                iteration += 1
            else:
                # No tool call, return response
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                return response
        
        return "Maximum iterations reached. Please provide more guidance."
    
    def reset(self):
        """Reset conversation history"""
        self.conversation_history = []


# --- Main Testing ---

def main():
    """Test the AURA agent with the network fault scenario"""
    
    print("=" * 70)
    print("AURA Network Operations Agent - Testing")
    print("=" * 70)
    
    agent = AURAAgent()
    
    # Scenario 1: Initial fault report
    print("\n" + "="*70)
    print("SCENARIO: Network KPI Degradation at DUB-07")
    print("="*70)
    
    prompt1 = "I see KPI degradation at site DUB-07. Please investigate the issue."
    print(f"\n👤 Operator: {prompt1}")
    print("\n🤖 AURA is thinking...\n")
    
    response1 = agent.process_message(prompt1)
    print(f"\n🤖 AURA Response:\n{response1}\n")
    
    # Wait between scenarios
    print("\n⏳ Waiting 3 seconds before next interaction...")
    time.sleep(3)
    
    # Scenario 2: Follow-up investigation
    print("\n" + "="*70)
    print("FOLLOW-UP: Operator confirms findings")
    print("="*70)
    
    prompt2 = "The fiber link issue looks correct. Please propose a remediation plan and ask for approval if needed."
    print(f"\n👤 Operator: {prompt2}")
    print("\n🤖 AURA is thinking...\n")
    
    response2 = agent.process_message(prompt2)
    print(f"\n🤖 AURA Response:\n{response2}\n")
    
    # Wait between scenarios
    print("\n⏳ Waiting 3 seconds before next interaction...")
    time.sleep(3)
    
    # Scenario 3: Grant approval
    print("\n" + "="*70)
    print("APPROVAL: Operator grants permission")
    print("="*70)
    
    prompt3 = "You are approved to proceed with the NTN failover."
    print(f"\n👤 Operator: {prompt3}")
    print("\n🤖 AURA is thinking...\n")
    
    response3 = agent.process_message(prompt3)
    print(f"\n🤖 AURA Response:\n{response3}\n")
    
    print("\n" + "="*70)
    print("Test Complete!")
    print("="*70)


if __name__ == "__main__":
    main()