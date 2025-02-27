// generateDummyData.js
// Phase 3/4 Update: Dummy Data Generation for the Updated Data Model
// This script generates a "roadmap.json" file with arrays for programs, products, material systems,
// CRAD opportunities, and suppliers, including dummy roadmap tasks, milestones, and supplier roadmap data.

const fs = require('fs');

const dummyData = {
  "programs": [
    { "id": "PRG1", "name": "Satellite Systems" },
    { "id": "PRG2", "name": "Missile Defense" },
    { "id": "PRG3", "name": "Launch Vehicles" },
    { "id": "PRG4", "name": "Space Exploration" },
    { "id": "PRG5", "name": "Communications" }
  ],
  "products": [
    {
      "id": "P1",
      "name": "SatCom Terminal",
      "programs": ["PRG1", "PRG5"],
      "designTools": ["CADPro", "SimulateX"],
      "documentation": ["User Manual", "Spec Sheet"],
      "partAcceptance": ["Visual Inspection", "Functional Test"],
      "materialSystems": ["MS1", "MS3"],
      "productSupplyChain": "Direct sourcing from approved vendors.",
      "roadmap": [
        { "task": "Initial Design", "start": "2025-01-01", "end": "2025-03-31", "status": "Complete" },
        { "task": "Prototype Build", "start": "2025-04-01", "end": "2025-06-30", "status": "In Progress" }
      ],
      "digitalToolsReferences": [
        { "name": "Simulation Setup", "start": "2025-02-01", "end": "2025-04-30", "status": "Planned" }
      ],
      "partAcceptanceRoadmap": [
        { "name": "Final Inspection", "start": "2025-07-01", "end": "2025-07-31", "status": "Planned" }
      ]
    },
    {
      "id": "P2",
      "name": "Weather Satellite",
      "programs": ["PRG1"],
      "designTools": ["OrbitSim", "ThermalAnalyzer"],
      "documentation": ["Launch Guide", "Maintenance Manual"],
      "partAcceptance": ["Thermal Test", "Vibration Test"],
      "materialSystems": ["MS2"],
      "productSupplyChain": "Specialized logistics for delicate components.",
      "roadmap": [
        { "task": "Concept Development", "start": "2025-01-15", "end": "2025-03-15", "status": "Complete" },
        { "task": "Component Testing", "start": "2025-04-01", "end": "2025-05-31", "status": "Planned" }
      ]
    },
    {
      "id": "P3",
      "name": "Interceptor Missile",
      "programs": ["PRG2"],
      "designTools": ["BallisticsCalc", "WindTunnel"],
      "documentation": ["Defense Manual", "Safety Protocol"],
      "partAcceptance": ["Impact Test", "Pressure Test"],
      "materialSystems": ["MS2"],
      "productSupplyChain": "Integrated supply chain with defense contractors.",
      "roadmap": [
        { "task": "Design Optimization", "start": "2025-03-01", "end": "2025-05-31", "status": "In Progress" },
        { "task": "Field Testing", "start": "2025-06-01", "end": "2025-08-31", "status": "Planned" }
      ]
    },
    {
      "id": "P4",
      "name": "Reusable Rocket",
      "programs": ["PRG3"],
      "designTools": ["PropulsionSim", "TrajectoryCalc"],
      "documentation": ["Launch Manual", "Maintenance Guide"],
      "partAcceptance": ["Stress Test", "Safety Test"],
      "materialSystems": ["MS1"],
      "productSupplyChain": "Optimized for rapid turnaround.",
      "roadmap": [
        { "task": "Engine Testing", "start": "2025-02-01", "end": "2025-04-30", "status": "Complete" },
        { "task": "Flight Simulation", "start": "2025-05-01", "end": "2025-07-31", "status": "Planned" }
      ]
    },
    {
      "id": "P5",
      "name": "Lunar Rover",
      "programs": ["PRG4"],
      "designTools": ["RoverSim", "3DModeler"],
      "documentation": ["Operational Manual", "Spec Sheet"],
      "partAcceptance": ["Performance Test", "Durability Test"],
      "materialSystems": ["MS3"],
      "productSupplyChain": "Customized for extraterrestrial components.",
      "roadmap": [
        { "task": "Mobility Analysis", "start": "2025-01-01", "end": "2025-02-28", "status": "Complete" },
        { "task": "Terrain Testing", "start": "2025-03-01", "end": "2025-05-31", "status": "In Progress" }
      ]
    }
  ],
  "materialSystems": [
    {
      "id": "MS1",
      "name": "Ti-6Al-4V",
      "qualification": "Qualified",
      "supplyChain": "Robust and established.",
      "relatedOpportunities": ["OPP3"],
      "roadmap": [
        { "task": "Material Certification", "start": "2025-01-01", "end": "2025-02-28", "status": "Complete" },
        { "task": "Batch Testing", "start": "2025-03-01", "end": "2025-04-30", "status": "Planned" }
      ],
      "milestones": [
        { "name": "Cert Approved", "date": "2025-02-28", "description": "Certification received from testing agency." }
      ]
    },
    {
      "id": "MS2",
      "name": "Inconel 718",
      "qualification": "Pending",
      "supplyChain": "Moderate reliability.",
      "relatedOpportunities": ["OPP4"],
      "roadmap": [
        { "task": "Preliminary Tests", "start": "2025-02-01", "end": "2025-03-31", "status": "In Progress" }
      ],
      "milestones": [
        { "name": "Initial Results", "date": "2025-03-31", "description": "First round of tests completed." }
      ]
    },
    {
      "id": "MS3",
      "name": "AlSi10Mg",
      "qualification": "Qualified",
      "supplyChain": "Strong and cost-effective.",
      "relatedOpportunities": [],
      "roadmap": [
        { "task": "Process Validation", "start": "2025-01-15", "end": "2025-03-15", "status": "Complete" }
      ],
      "milestones": []
    }
  ],
  "cradOpportunities": [
    {
      "id": "OPP1",
      "name": "Advanced SatCom Upgrade",
      "relatedEntity": "P1",
      "details": "Opportunity for enhanced satellite communication systems; potential for increased funding."
    },
    {
      "id": "OPP2",
      "name": "Reusable Rocket Efficiency",
      "relatedEntity": "P4",
      "details": "Focus on improving efficiency of reusable rockets; seeking industry partners."
    },
    {
      "id": "OPP3",
      "name": "Titanium Expansion",
      "relatedEntity": "MS1",
      "details": "Expand usage of Ti-6Al-4V in aerospace applications; high interest in collaboration."
    },
    {
      "id": "OPP4",
      "name": "Inconel Testing Initiative",
      "relatedEntity": "MS2",
      "details": "Pilot project for testing Inconel 718 under extreme conditions; funding secured."
    }
  ],
  "suppliers": [
    {
      "id": "SUP1",
      "name": "AeroSupplies Inc.",
      "materials": ["MS1", "MS3"],
      "additionalCapabilities": "Expert in aerospace-grade materials.",
      "supplierRoadmap": {
        "tasks": [
          { "task": "Vendor Qualification", "start": "2025-01-01", "end": "2025-02-15", "status": "Complete", "category": "Material System Vendor Qual" },
          { "task": "Supply Contract Negotiation", "start": "2025-03-01", "end": "2025-04-30", "status": "Planned", "category": "Supplier Management" }
        ]
      },
      "machines": [1, 2]
    },
    {
      "id": "SUP2",
      "name": "Defense Materials Ltd.",
      "materials": ["MS2"],
      "additionalCapabilities": "Specializes in high-temperature alloys.",
      "supplierRoadmap": {
        "tasks": [
          { "task": "Initial Evaluation", "start": "2025-02-01", "end": "2025-03-01", "status": "In Progress", "category": "Material System Vendor Qual" },
          { "task": "Long-term Partnership Discussion", "start": "2025-04-01", "end": "2025-05-31", "status": "Planned", "category": "Supplier Management" }
        ]
      },
      "machines": [2, 3]
    },
    {
      "id": "SUP3",
      "name": "SpaceTech Supplies",
      "materials": ["MS3"],
      "additionalCapabilities": "Innovative solutions for lightweight materials.",
      "supplierRoadmap": {
        "tasks": [
          { "task": "Capability Assessment", "start": "2025-01-15", "end": "2025-02-28", "status": "Complete", "category": "Material System Vendor Qual" }
        ]
      },
      "machines": [1]
    }
  ]
};

fs.writeFileSync("roadmap.json", JSON.stringify(dummyData, null, 2));
console.log("Dummy data generated and written to roadmap.json");
