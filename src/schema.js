// JSON schema definition for roadmap.json
const schema = {
  type: "object",
  properties: {
    programs: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          name: { type: "string" },
          description: { type: "string" },
          tasks: {
            type: "array",
            items: {
              type: "object",
              properties: {
                id: { type: "string" },
                name: { type: "string" },
                description: { type: "string" },
                startDate: { type: "string", format: "date" },
                endDate: { type: "string", format: "date" },
                status: { type: "string" }
              },
              required: ["id", "name"]
            }
          }
        },
        required: ["id", "name"]
      }
    },
    products: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          name: { type: "string" },
          description: { type: "string" },
          programs: { 
            type: "array", 
            items: { type: "string" } 
          },
          productSupplyChain: { type: "string" }
        },
        required: ["id", "name"]
      }
    },
    materialSystems: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          name: { type: "string" },
          qualification: { type: "string" },
          qualificationClass: { type: "string" },
          supplyChain: { type: "string" },
          standardNDT: { 
            type: "array", 
            items: { type: "string" } 
          }
        },
        required: ["id", "name"]
      }
    },
    cradOpportunities: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          name: { type: "string" },
          relatedEntity: { type: "string" },
          details: { type: "string" }
        },
        required: ["id", "name"]
      }
    },
    suppliers: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          name: { type: "string" },
          materials: { 
            type: "array", 
            items: { type: "string" } 
          },
          additionalCapabilities: { type: "string" }
        },
        required: ["id", "name"]
      }
    }
  },
  // Only require programs to be present, other arrays can be empty
  required: ["programs"]
};

module.exports = { schema }; 