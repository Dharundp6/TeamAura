import logging
from datetime import datetime
import json
from aura_agent import AURAAgent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aura_operations.log'),
        logging.StreamHandler()
    ]
)

class AURAAgentWithLogging(AURAAgent):
    """Enhanced AURA agent with logging and metrics"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = {
            "total_interactions": 0,
            "tool_calls": 0,
            "approvals_requested": 0,
            "remediations_executed": 0,
            "start_time": datetime.now()
        }
    
    def process_message(self, user_message: str, max_iterations: int = 5) -> str:
        """Process message with logging"""
        self.metrics["total_interactions"] += 1
        
        logging.info(f"Processing user message: {user_message[:100]}...")
        
        response = super().process_message(user_message, max_iterations)
        
        # Track if approval was requested
        if "APPROVAL" in response or "approve" in response.lower():
            self.metrics["approvals_requested"] += 1
        
        logging.info(f"Response generated: {len(response)} characters")
        
        return response
    
    def _execute_tool(self, tool_name: str, param: str) -> dict:
        """Execute tool with logging"""
        self.metrics["tool_calls"] += 1
        logging.info(f"Executing tool: {tool_name}({param})")
        
        result = super()._execute_tool(tool_name, param)
        
        if tool_name == "initiate_ntn_failover" and result.get("success"):
            self.metrics["remediations_executed"] += 1
        
        logging.info(f"Tool result: {result}")
        
        return result
    
    def get_metrics(self) -> dict:
        """Get current metrics"""
        runtime = (datetime.now() - self.metrics["start_time"]).total_seconds()
        self.metrics["runtime_seconds"] = runtime
        return self.metrics