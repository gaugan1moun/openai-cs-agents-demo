# Customer Service Agents Demo

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![NextJS](https://img.shields.io/badge/Built_with-NextJS-blue)
![OpenAI API](https://img.shields.io/badge/Powered_by-OpenAI_API-orange)

This repository contains a demo of a Customer Service interface built on top of the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/).

It is composed of two parts:

1. A python backend that handles the agent orchestration logic, implementing the Agents SDK [customer service example](https://github.com/openai/openai-agents-python/tree/main/examples/customer_service)

2. A Next.js UI allowing the visualization of the agent orchestration process and providing a chat interface. It uses [ChatKit](https://openai.github.io/chatkit-js/) to provide a high-quality chat interface.

![Demo Screenshot](screenshot.jpg)

> **Personal fork note:** I'm using this project to learn the OpenAI Agents SDK. My main area of interest is the triage/routing logic and how handoffs between agents work.

## How to use

### Setting your OpenAI API key

You can set your OpenAI API key in your environment variables by running the following command in your terminal:

```bash
export OPENAI_API_KEY=your_api_key
```

You can also follow [these instructions](https://platform.openai.com/docs/libraries#create-and-export-an-api-key) to set your OpenAI key at a global level.

Alternatively, you can set the `OPENAI_API_KEY` environment variable in an `.env` file at the root of the `python-backend` folder. You will need to install the `python-dotenv` package to load the environment variables from the `.env` file. And then, add these lines of code to your app:

```bash
from dotenv import load_dotenv

load_dotenv()
```

### Install dependencies

Install the dependencies for the backend by running the following commands:

```bash
cd python-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For the UI, you can run:

```bash
cd ui
npm install
```

### Run the app

You can either run the backend independently if you want to use a separate UI, or run both the UI and backend at the same time.

#### Run the backend independently

From the `python-backend` folder, run:

```bash
python -m uvicorn main:app --reload --port 8000
```

The backend will be available at: [http://localhost:8000](http://localhost:8000)

#### Run the UI & backend simultaneously

From the `ui` folder, run:

```bash
npm run dev
```

The frontend will be available at: [http://localhost:3000](http://localhost:3000)

This command will also start the backend.

## Customization

This app is designed for demonstration purposes. Feel free to update the agent prompts, guardrails, and tools to fit your own customer service workflows or experiment with new use cases! The modular structure makes it easy to extend or modify the orchestration logic for your needs.

## Agents included

- **Triage Agent**: entry point that routes to specialists.
- **Sales Agent**: handles product inquiries and purchase-related questions.
- **Refund Agent**: handles refund and return requests.
- **FAQ Agent**: answers common questions using a knowledge base.

> **Note (personal):** The handoff mechanism between the Triage Agent and the specialist agents is the most interesting part to study — see `python-backend/agents/` for the routing logic.
