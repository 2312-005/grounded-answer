
## 1. Project Approach
I decided to build "The Grounded Answer" as a policy-based question-answering system. It searches the supplied policy documents and gives answers only based on the retrieved evidence.

## 2. Tech Stack
Frontend - HTML, CSS, JavaScript
Backend - Python, FastAPI
RAG - Python, Sentence Transformers, Embeddings Database - ChromaDB
Dataset - Policy Manual, Amendment Document
Development and Testing - Python Virtual Environment, Powershell
versioning - Git, GitHub

## 3. RAG Approach
I chose RAG to retrieve relevant policy clauses before generating an answer. I rejected direct AI answering because it could provide information not supported by the policy.

## 4. Policy Document Handling
Used the complete policy-manual.md as the RAG corpus, split into clauses and stored as embeddings for section-wise retrieval and citations.

## 5. Surprise Challenge
handling amendments without losing the original policy rules. I solved this by keeping the policy and amendment as separate sources and applying the correct rule based on the claim date.

## 6. What was Rejected
Rejected direct AI answering and hardcoded topic-based answers because both could give unsupported answers or require manual updates for every new topic.

## 7. What Was Cut for Time
I kept the project focused on the main criteria. Advanced features like user accounts, chat history, and admin dashboards were left out to focus on the core requirements.

## 8. What the Solution Does Not Do
The system does not make up an answer when the policy evidence is not available. It asks the user to consult the relevant policy authority instead.

## 9. What I Would Fix First
I would first improve retrieval for difficult or differently worded questions and add more test cases covering all sections of the policy.