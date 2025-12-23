# Persona-Agent 👤🤖

A next-generation conversational agent that goes beyond text and audio to create a more natural and human-like interaction. Persona-Agent features a digital avatar with realistic facial expressions and body language, using real-time visual and auditory cues to make conversations feel more empathetic and engaging.

-----

## ✨ Features

  * **Natural Human-like Interaction:** The agent uses realistic facial expressions and body language to enhance the conversational experience.
  * **Real-time User Analysis:** The **Vision Agent** analyzes the user's emotional state, head movements, and eye gaze to provide real-time, context-aware responses.
  * **Multi-Modal Data Fusion:** Leverages **VideoMAE-v2** and **AudioCLIP** to seamlessly fuse visual and audio data, creating a comprehensive understanding of the user.
  * **Dynamic Synthesis:** The **Synthesis Agent** animates the digital human's avatar in real-time based on the agent's internal state and the conversation's flow.
  * **Core Conversational Intelligence:** The conversational logic is powered by a large-scale multimodal model, ensuring rich and contextually relevant dialogue.

-----

### 🧠 The Multimodal AI Stack (Inference Layer)

* **Inference Framework:** **FastAPI (Python)**. Chosen for its high speed and native support for asynchronous tasks, making it ideal for serving machine learning models.
* **Vision Analysis:** **VideoMAE-v2**. A masked autoencoder for video that excels at "Temporal Action Classification"—this allows the agent to recognize movements and facial changes over time rather than just static images.
* **Auditory Analysis:** **AudioCLIP**. A specialized model that maps audio signals to the same space as images and text, allowing the agent to "hear" the emotion in your voice.
* **Deep Learning Backend:** **PyTorch**. The engine that runs the actual model weights on the GPU.
* **Image Processing:** **OpenCV**. Used for real-time frame resizing, cropping, and normalization before feeding data into the AI.

---

### 🎨 The Digital Human (Synthesis Layer)

* **3D Rendering:** **Three.js** via **@react-three/fiber**. This is the core of the **Synthesis Agent**, rendering the 3D character in the browser using WebGL.
* **Helper Library:** **@react-three/drei**. Provides essential utilities for loading `.glb` (3D) models and managing camera controls easily.
* **Animation Technique:** **Morph Targets (Blend Shapes)**. Instead of traditional "bones," the avatar uses vertex-based morphing to create fluid, realistic facial expressions like smiling, blinking, and talking.

---

### 📡 Communication & Data Management

* **API Protocol:** **tRPC**. This is the "glue" of the project. It allows the Frontend to call functions on the Backend as if they were local, with full TypeScript autocompletion.
* **Validation:** **Zod**. Used to define schemas for the data moving between the frontend and backend, ensuring that every video frame and emotion tag is formatted correctly.
* **Database:** **MongoDB**. A NoSQL database used to store interaction logs, user preferences, and "memories" of previous conversations.
* **ODM:** **Mongoose**. Provides a structured way to interact with MongoDB within the Node.js environment.

---

### 🚀 DevOps & Infrastructure

* **Containerization:** **Docker**. Every part of the stack (the DB, the Node server, and the Python AI) is containerized to ensure it runs exactly the same on your machine as it would in production.
* **Orchestration:** **Docker Compose**. Allows you to spin up the entire multi-language ecosystem (Node + Python + Mongo) with a single command.
* **Styling:** **Tailwind CSS**. Used to build the "Command Center" UI overlay, handling the picture-in-picture webcam feed and chat interface.

---

### 📂 Final Development Path

With this stack, your development flow for **saadsalmanakram/Persona-Agent** looks like this:

1. **Capture** user data in the browser (Next.js).
2. **Transmit** it via a type-safe tunnel (tRPC).
3. **Analyze** the behavior using the GPU (Python/PyTorch).
4. **Synthesize** the response by animating the avatar (Three.js).

-----

## 🚀 Getting Started

### Prerequisites

  * Node.js (for Next.js)
  * Access to a massive multimodal model and other APIs

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/saadsalmanakram/Persona-Agent.git
    cd Persona-Agent
    ```
2.  **Set up the front-end:**
    ```bash
    npm install
    ```
3.  **Configure the backend:**
    Follow the instructions in the `backend/` directory to set up the agent services and connect them to the necessary models.

### Configuration

Create a `.env` file to store your API keys and model credentials.

### Usage

Run the Next.js server and the backend services to start the agent. You can then interact with it via the web interface, which will capture your visual and auditory data for analysis.

-----


