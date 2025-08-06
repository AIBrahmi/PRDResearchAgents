# Multi-Agent System for Product Requirements Document (PRD) Generation

This project demonstrates a multi-agent workflow using Llamaindex to automate the creation of a Product Requirements Document (PRD). The system uses three distinct agents: a **ResearchAgent**, a **WriteAgent**, and a **ReviewAgent**, who collaborate to produce a final document based on initial user requirements.

---

## 🤖 How It Works

1.  **ResearchAgent**: Receives the initial product idea and uses a Google Search tool to research the topic. It then compiles the findings into structured notes.
2.  **WriteAgent**: Takes the research notes and writes a complete PRD in markdown format. It is explicitly forbidden from doing its own research.
3.  **ReviewAgent**: Examines the generated PRD for quality and completeness. It can either approve the document or send it back to the WriteAgent with feedback for revision.

The workflow continues until the ReviewAgent approves the report.

---

## 🚀 Getting Started

Follow these instructions to set up and run the project on your local machine.

### 1. Prerequisites

* Python 3.9 or higher.
* A Google AI API Key. You can get one from **[Google AI Studio](https://aistudio.google.com/app/apikey)**.

### 2. Setup

First, clone the repository to your local machine:

```sh
git clone <your-repo-url>
cd <your-repo-directory>
```

Next, create and activate a virtual environment. This isolates the project's dependencies from your system.

* **On macOS/Linux:**
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

* **On Windows:**
    ```sh
    python -m venv venv
    .\venv\Scripts\activate
    ````

Install the required Python packages using the `requirements.txt` file:
```sh
pip install -r requirements.txt
```

### 3. Configuration

The script needs your Google AI API key to function.

Create a new file named .env in the root directory of the project.

Add your API key to the .env file as follows:
```sh
GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

Replace "YOUR_API_KEY_HERE" with your actual key. A .gitignore file should be included in your repository to prevent this file from being accidentally committed.

### 4. Usage

To run the multi-agent workflow, simply execute the main.py script from your terminal:
   ```sh
   python main.py
   ```

You will see the agents interacting in real-time in your terminal, including their research, writing, and review steps. The final PRD and the review comments will be printed at the end of the process.



# Demo / Example Output

Here’s an example of the workflow in action.

<img width="908" height="362" alt="1" src="https://github.com/user-attachments/assets/0c30a482-007a-4dbc-910d-5f3839ad1a4e" />







<img width="785" height="373" alt="2" src="https://github.com/user-attachments/assets/91841fff-028b-416a-b79a-d85a854ccdde" />



