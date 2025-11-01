# Project AURA (Agentic Unified Resource Automation)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange.svg)](https://aws.amazon.com/bedrock/)

> **An intelligent multi-agent system for autonomous telecommunications network management**

Developed by **Team AURA** - University of Glasgow

---
## 🌟 Overview

Project AURA (Agentic Unified Resource Automation) is an intelligent, multi-agent system that functions as a unified, autonomous control plane for heterogeneous telecommunications networks. Built to address the operational "complexity crisis" in modern telecom infrastructure, AURA moves beyond simple automation to achieve true autonomy through intelligent reasoning, planning, and adaptation.

### What Makes AURA Different?

AURA doesn't just execute predefined tasks—it **understands intent, reasons about problems, plans solutions, and adapts to achieve goals autonomously**. This represents a paradigm shift from traditional script-based automation to intelligent, agentic operations.

---

## 🚨 The Problem

Modern telecommunications networks face a critical **"Complexity Crisis"**:

### 1. **Disaggregation & Multi-Vendor Chaos**
- Open RAN (O-RAN) and cloud-native 5G architectures mean operators manage components from dozens of vendors
- Each vendor has proprietary APIs and unique lifecycle management requirements
- Integration complexity grows exponentially with each new vendor

### 2. **Brittle Automation**
- Current automation relies on vendor-specific, script-based systems
- Scripts are fragile, difficult to maintain, and break with component updates
- High error rates lead to increased operational costs (OPEX)

### 3. **New Integration Hurdles**
- Non-Terrestrial Networks (NTNs) for ubiquitous coverage add significant operational complexity
- Cross-domain fault diagnosis requires manual engineering effort
- Slow fault resolution impacts service reliability and customer satisfaction

**The Result:** High operational costs, slow incident resolution, and inability to autonomously manage network potential.

---

## 💡 Our Solution

Project AURA addresses these challenges through a three-layer architecture:

### 1. **The "Swarm" (Intelligence Layer)**
Multi-agent system built with **Strands Agents SDK** featuring:
- **Supervisor-Worker Pattern**: OperatorAgent coordinates specialized worker agents
- **Collaborative Problem-Solving**: Agents share context and work together on complex tasks
- **Specialized Agents**: RANEngineer, TransportAgent, NTNAgent for domain expertise

### 2. **The "Gateway" (Abstraction Layer)**
Our novel **AURA MCP Gateway** solves the multi-vendor integration challenge:
- **Universal API Abstraction**: Standardized, intent-based tools for agents
- **Vendor Adapters**: Translates generic commands to vendor-specific API calls
- **Governance & Security**: Single auditable chokepoint for policy enforcement

### 3. **The "Backbone" (Foundation Layer)**
Production-grade infrastructure using **Amazon Bedrock AgentCore**:
- **AgentCore Runtime**: Secure, serverless execution environment
- **AgentCore Memory**: Persistent, shared context for agent collaboration
- **AgentCore Identity**: Auditable, least-privilege access control

---

## ✨ Key Features

### 🤖 **Intelligent Multi-Agent System**
- Supervisor-worker coordination pattern
- Collaborative problem-solving with shared context
- Domain-specific expertise (RAN, Transport, NTN)

### 🔌 **Universal Vendor Integration**
- Abstraction of vendor-specific APIs
- Dynamic adapter registry for extensibility
- Support for Nokia, Ericsson, Cisco, and more

### 🛡️ **Enterprise-Grade Security**
- Auditable agent actions via AgentCore Identity
- Policy enforcement at gateway level
- Least-privilege access control

### ⚡ **Autonomous Operations**
- Intent-based task delegation
- Cross-domain fault diagnosis
- Automatic remediation with human-in-the-loop approval

### 🔄 **Future-Proof Architecture**
- Easily extensible for new capabilities
- Plugin architecture for new agents
- Scalable for 6G, network slicing, and beyond

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **AI/ML Framework** | Strands Agents SDK | Multi-agent orchestration and collaboration |
| **Cloud Platform** | Amazon Bedrock AgentCore | Production-grade agent runtime and infrastructure |
| **API Gateway** | Custom AURA MCP Gateway | Vendor API abstraction and governance |
| **Programming Language** | Python 3.9+ | Core implementation |
| **Network APIs** | REST/gRPC | Multi-vendor network integration |
| **Memory Store** | AgentCore Memory | Persistent agent context |
| **Identity Management** | AgentCore Identity | Access control and auditing |

---

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- AWS Account with Bedrock access
- Network API credentials (vendor-specific)
- Docker (optional, for containerized deployment)

### Setup Instructions

1. **Clone the repository**
```bash
   git clone https://github.com/your-org/project-aura.git
   cd project-aura
```

2. **Create virtual environment**
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
   cp .env.example .env
   # Edit .env with your credentials
```

5. **Configure AWS credentials**
```bash
   aws configure
   # Enter your AWS Access Key ID, Secret Access Key, and region
```

6. **Initialize the AURA MCP Gateway**
```bash
   python scripts/init_gateway.py
```

7. **Run the system**
```bash
   python main.py
```

---

## 🚀 Usage

### Basic Command-Line Interface
```bash
# Start AURA with interactive mode
python main.py --interactive

# Execute a specific intent
python main.py --intent "Investigate eMBB degradation at site DUB-07"

# Run in monitoring mode
python main.py --mode monitor --duration 3600
```

### Programmatic Usage
```python
from aura import OperatorAgent, AURAGateway
from bedrock import AgentCore

# Initialize components
gateway = AURAGateway(config_path="config/gateway.yaml")
agent_core = AgentCore(region="us-east-1")
operator = OperatorAgent(gateway=gateway, runtime=agent_core)

# Execute autonomous operation
result = operator.execute_intent(
    "Investigate and fix eMBB degradation at site DUB-07"
)

print(f"Status: {result.status}")
print(f"Actions Taken: {result.actions}")
print(f"Resolution Time: {result.duration}s")
```

### Configuration

Edit `config/aura_config.yaml`:
```yaml
agents:
  operator:
    model: "claude-sonnet-4-5"
    temperature: 0.7
  ran_engineer:
    model: "claude-sonnet-4-5"
    temperature: 0.5

gateway:
  vendors:
    - name: "Nokia"
      adapter: "adapters.nokia.NokiaAdapter"
      base_url: "https://nokia-api.example.com"
    - name: "Ericsson"
      adapter: "adapters.ericsson.EricssonAdapter"
      base_url: "https://ericsson-api.example.com"

bedrock:
  region: "us-east-1"
  runtime:
    timeout: 300
  memory:
    retention_days: 30
```

---

## 🎬 Demo Scenario

### Automated Cross-Domain Fault Triage & NTN Failover

**Scenario:** High-priority KPI degradation at cell site DUB-07

**Workflow:**

1. **Alert Triggered**: eMBB service degradation detected
2. **Human Intent**: Operator issues command: *"Investigate and fix eMBB degradation at site DUB-07"*
3. **Autonomous Triage**:
   - OperatorAgent creates diagnostic plan
   - RANAgent checks radio conditions → **Result: Healthy**
   - TransportAgent checks backhaul links → **Result: Critical packet loss on primary fiber**
4. **Root Cause Analysis**: OperatorAgent synthesizes findings → Fiber link failure identified
5. **Autonomous Remediation**: 
   - Human-in-the-loop approval requested
   - TransportAgent executes failover to NTN backup
6. **Verification**: RANAgent confirms service restoration

**Result:** Incident resolved in seconds vs. hours of manual effort

---

## 🤝 Contributing

We welcome contributions from the community! Please follow these guidelines:

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Write unit tests for new features
- Update documentation for API changes
- Add comments for complex logic
- Ensure all tests pass before submitting PR

### Code of Conduct

Please read our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

---

## 👥 Team

**Team AURA - University of Glasgow**

- **Nitesh Ranjan Singh** - [3090808S@student.gla.ac.uk](mailto:3090808S@student.gla.ac.uk)
- **Dharun Prasanth** - [3077252S@student.gla.ac.uk](mailto:3077252S@student.gla.ac.uk)

**Registration Type:** Virtual

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Anthropic** for the Claude AI models powering our agents via Strands SDK
- **Amazon Web Services** for Bedrock AgentCore infrastructure
- **Strands** for the flexible agent framework
- **O-RAN Alliance** for open architecture specifications
- **University of Glasgow** for academic support

---

## 📊 Solution Impact

### Key Benefits

| Metric | Traditional Approach | With AURA |
|--------|---------------------|-----------|
| **Fault Resolution Time** | Hours | Seconds |
| **OPEX Reduction** | Baseline | 70-80% reduction |
| **Network Resilience** | Manual failover (5-15 min) | Autonomous (< 30 sec) |
| **Multi-Vendor Integration** | Hard-coded per vendor | Universal abstraction |
| **Scalability** | Limited | Highly extensible |

### Future Roadmap

- ✅ Basic autonomous fault triage and remediation
- ✅ Multi-vendor API abstraction via MCP Gateway
- 🔄 Advanced network slicing optimization
- 🔄 6G integration capabilities
- 🔄 Energy-aware autonomous optimization
- 🔄 Predictive maintenance using historical patterns
- 🔄 Multi-region orchestration

---

<div align="center">

**Made with ❤️ by Team AURA**

*Transforming telecommunications through intelligent autonomy*

</div>
