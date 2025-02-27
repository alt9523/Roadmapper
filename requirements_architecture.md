# Interactive AM Roadmap – Requirements Document

## 1. Introduction

**Purpose:**  
Define the functional and non-functional requirements for the Interactive AM Roadmap system. The solution will be a self-contained HTML file that is updated locally and deployed in environments like SharePoint.

**Scope:**  
Focus on managing and displaying data for Programs, Products, Material Systems, CRAD Opportunities, and Suppliers. The roadmap will include interactive filtering, detailed task/milestone views, and enhanced navigation that integrates legacy relationships from previous implementations.

---

## 2. Functional Requirements

### A. Data Update & Management
- **Local Data Management:**  
  - Allow users to update roadmap data via a local interface.
  - Store data in a structured JSON file.
  - Validate data using AJV against a defined JSON schema.
- **Extended Data Model:**  
  - Maintain separate arrays for:
    - **Programs:** Contains a unique identifier and name.
    - **Products:** Detailed attributes (design tools, documentation, part acceptance, product-specific supply chain) and associated program IDs.
    - **Material Systems:** Includes qualification details, supply chain information, and an array of related CRAD opportunity IDs.
    - **CRAD Opportunities:** Each opportunity includes an ID, name, a related entity (product or material system), and a detailed description.
    - **Suppliers:** A new array with supplier details, capabilities, materials supplied, supplier-specific roadmap tasks, and milestones.

### B. HTML Generation & Client-Side Interactivity
- **Self-Contained Output:**  
  - Generate a single HTML file that embeds all necessary HTML, CSS, JavaScript, and JSON data.
  - Ensure offline functionality and full compatibility with SharePoint.
- **Interactive Display:**  
  - Implement multiple views for:
    - **Programs:** Lists programs and their associated products.
    - **Products:** Provides detailed view including design tools, documentation, part acceptance, and related material systems.
    - **Material Systems:** Displays qualification and supply chain details, products using them, and linked CRAD opportunities.
    - **CRAD Opportunities:** Presented in a table with complete details.
    - **Suppliers:** Allows browsing and detailed supplier view, including supplier-specific roadmap tasks.
  - Integrate dynamic filtering, case-insensitive search, and expand/collapse functionality for improved readability.
  - Enable interactive roadmap displays with detailed tasks and milestone pop-ups based on legacy elements.

### C. Navigation & Legacy Integration
- **Enhanced Navigation:**  
  - Retain the established navigational flows from the legacy `index.html`.
  - Provide seamless transitions between main views and detailed views (e.g., product → supplier → roadmap details).
- **Task and Milestone Interactivity:**  
  - Include clickable roadmap tasks and milestone cells that reveal detailed information.
  - Utilize tooltips and hover descriptions to guide users through the interface.

### D. Build Process & Deployment
- **Automated Build Process:**  
  - A Node.js script will:
    - Read and validate the JSON file.
    - Generate the updated HTML file.
    - Copy the generated file to an external repository (e.g., SharePoint folder).
  - Implement a file-watching mechanism to automatically rebuild the HTML file upon JSON data updates.

---

## 3. Non-Functional Requirements

### A. Performance & Responsiveness
- Fast load times and smooth interaction across all views.
- Responsive design for desktops, tablets, and mobile devices.

### B. Usability
- An intuitive, user-friendly interface requiring minimal training.
- Clear separation between data presentation and navigation, using expandable sections and tooltips for guidance.

### C. Maintainability & Scalability
- Clearly organized code with modular JavaScript components that separate data management, UI rendering, and event handling.
- The design should allow for future expansions (e.g., additional data categories or enhanced interactivity) without extensive rework.

### D. Portability
- The output HTML file must function correctly on modern browsers and be fully self-contained for deployment in SharePoint and similar environments.

---

## 4. Data & Integration

### A. Data Sources
- Local JSON file containing arrays for:
  - Programs
  - Products
  - Material Systems
  - CRAD Opportunities
  - Suppliers

### B. Integration Points
- **Build Script:**  
  - Validate the JSON data against the defined schema.
  - Generate a self-contained HTML file.
  - Automatically copy the generated file to the designated external repository.

### C. Data Model Relationships
- **Programs & Products:**  
  - Products reference one or more programs via their IDs.
- **Products & Material Systems:**  
  - Products reference material systems; material systems list the products that use them.
- **Material Systems & CRAD Opportunities:**  
  - Material systems link to CRAD opportunities via opportunity IDs (displayed by name in the UI).
- **Suppliers & Products:**  
  - Suppliers are linked to products indirectly through the materials they supply.
- **Roadmap Tasks & Milestones:**  
  - Integrated across products and suppliers, with legacy navigation elements incorporated to display detailed task and milestone information.

---

# Interactive AM Roadmap – Architecture Design Document

## 1. System Overview

**Objective:**  
Provide a self-contained interactive roadmap solution that updates local data and compiles it into an HTML file suitable for offline use and SharePoint deployment. The system integrates legacy UI elements with a modern, decoupled data model.

**Components:**
- **Data Management Module:**  
  - Handles local data updates and validation using a JSON file and AJV.
- **Build/Compile Module:**  
  - A Node.js (or Python) script that reads the JSON file, validates data, and generates the final HTML file.
- **User Interface Module:**  
  - Renders multiple interactive views: Programs, Products, Material Systems, CRAD Opportunities, and Suppliers.
- **CRAD Opportunities Module:**  
  - Manages opportunity tagging and filtered views.
- **Legacy Integration:**  
  - Retains navigation and interactivity elements from the previous `index.html` (e.g., roadmap task details, supplier views, milestone pop-ups).

---

## 2. System Architecture

### A. Client-Side Architecture
- **Single-Page Application (SPA):**
  - All HTML, CSS, and JavaScript are bundled into one self-contained HTML file.
  - The UI supports multiple views (Programs, Products, Material Systems, CRAD Opportunities, Suppliers) using tabbed navigation and dedicated sections.
- **Modular JavaScript Components:**
  - **Navigation Module:**  
    - Manages section transitions, back navigation, and history tracking.
  - **Data Rendering Modules:**  
    - Separate functions for rendering each view (e.g., `renderPrograms()`, `renderProducts()`, `renderMaterialSystems()`, `renderCradOpportunities()`, `renderSuppliers()`).
    - Integrates legacy rendering logic from the previous `index.html` for roadmap tasks, milestones, and detailed supplier information.
  - **Event Handling & Interaction:**  
    - Implements dynamic filtering, expand/collapse behavior, tooltips, and interactive roadmap components.

### B. Build Process
- **Local Build Script:**  
  - Reads the JSON data file and validates it using AJV against the updated schema.
  - Uses templating (or inline template literals) to generate a fully self-contained HTML file.
  - Automates copying the generated HTML file to the external repository (e.g., SharePoint folder).
  - Implements a file watcher to monitor JSON changes and trigger automated rebuilds.

---

## 3. Data Flow and Integration

### A. Data Flow
1. **Data Update:**  
   - Users update the local JSON file containing arrays for Programs, Products, Material Systems, CRAD Opportunities, and Suppliers.
2. **Validation & Build:**  
   - The build process validates the JSON data and compiles it into a self-contained HTML file.
3. **Deployment:**  
   - The updated HTML file is automatically copied to the external repository for deployment (e.g., SharePoint).
4. **User Interaction:**  
   - End users interact with the generated HTML file, with client-side scripts managing view transitions and dynamic data filtering.

### B. Extended Data Relationships
- **Programs:**  
  - Contain only an ID and name.
- **Products:**  
  - Maintain detailed attributes and reference Programs, Material Systems, and product-specific supply chain details.
- **Material Systems:**  
  - Include qualification details, supply chain information, and reference CRAD Opportunities.
- **CRAD Opportunities:**  
  - Include a name, linked entity (Product or Material System), and detailed information.
- **Suppliers:**  
  - Newly integrated; include detailed supplier information, capabilities, materials supplied, and supplier-specific roadmap tasks.
- **Roadmap Tasks & Milestones:**  
  - Integrated into both Product and Supplier views, with legacy navigation elements preserved for detailed pop-ups.

---

## 4. Future Enhancements
- **Cloud Integration:**  
  - Automatic updates via cloud storage solutions.
- **Expanded Modules:**  
  - Additional categories or modules can be added without major rework.
- **User Authentication & Data Versioning:**  
  - Future iterations may include user authentication and version control for data changes.

  Front-End Framework Layer:

Component Architecture: Describe how the application is broken into components (e.g., Navigation, Timeline, Detail Views, and Task Entry forms).
State Management: Outline how state (e.g., current tasks, timeline zoom level, selected swim lane) will be managed within the chosen framework.
Visualization Integration:

Timeline Component: Document the chosen visualization library (e.g., vis-timeline) and how it will be integrated as a component.
Customization: Explain how the timeline will be configured to support three swim lanes, milestone markers, and interactive task editing.
Build and Deployment Process:

Describe the build process (using a tool like Webpack/Vite) that compiles the application into a set of static assets.
Emphasize that the final bundled output is self-contained and compatible with SharePoint.


---

## Summary

- **Requirements Document:**  
  - Details expanded UI requirements (including Suppliers, detailed roadmap tasks, and milestones) and an extended data model with interlinked relationships.
- **Architecture Design Document:**  
  - Outlines a modular, SPA-based client-side architecture with integrated legacy UI elements, a robust build process, and a clear data flow that supports offline, self-contained deployments.
