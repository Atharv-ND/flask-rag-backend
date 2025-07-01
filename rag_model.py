from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
import os

from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

import google.generativeai as genai
import re

# --- Load environment variables and configure Gemini ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")
MONGO_URI = os.getenv("MONGO_URI")

# --- Flask app setup ---
app = Flask(__name__)
CORS(app)
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["Healthcare"]
collection = db["symptom"]

# --- Fetch knowledge base from MongoDB ---
kb_records = list(collection.find({}))
documents = [Document(page_content=rec["content"], metadata={"title": rec["department"]}) for rec in kb_records]

# --- Create FAISS vector index using Sentence Transformers ---
embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')
vector_store = FAISS.from_documents(documents, embedding_model)

# --- Semantic Retrieval + Generation ---
def retrieve_context(symptom_query: str, k=3):
    results = vector_store.similarity_search(symptom_query, k=k)
    if not results:
        return None
    return results

def generate_response(symptoms: str, age: int, gender: str):
    age_group = "Young" if age < 20 else "Adult" if age < 60 else "Elderly"
    profile = f"{age_group} {gender.capitalize()}"
    retrieved_docs = retrieve_context(symptoms, k=6)

    if not retrieved_docs:
        return {
            "department": "Not Identified",
            "answer": "I'm sorry, I couldn't find any relevant information for the symptoms provided. Please consult a doctor for a proper diagnosis.",
            "treatment": "- Seek medical attention\n- Avoid self-diagnosis\n- Maintain symptom log\n- Visit nearest hospital if symptoms worsen"
        }

    context = "\n\n".join([f"{doc.metadata['title']}:\n{doc.page_content}" for doc in retrieved_docs])

    prompt = f"""
You are a medical assistant AI helping to triage a patient based on symptoms and demographic information.

Patient's Symptoms: "{symptoms}"
Age and Gender: {profile}

Refer only to the following medical knowledge base:
{context}

Your task:
1. Analyze the symptoms individually.
2. Match each symptom with the most appropriate medical department from the knowledge base.
3. For each department, explain briefly why it's relevant.
4. Extract only relevant treatment steps from the context for that department.

Use the format shown in these examples:
Symptoms : Chest Pain , Knee Pain
---
Department: Cardiology
Explanation: The patient is experiencing chest pain, which may indicate heart-related issues. Cardiology specializes in diagnosing and treating such symptoms.
Treatment:
- Avoid physical exertion
- Monitor blood pressure regularly
- Schedule an ECG with a cardiologist
---

---
Department: Orthopedics
Explanation: Knee pain is typically treated under orthopedics, which deals with joint and musculoskeletal conditions.
Treatment:
- Rest and avoid weight-bearing activity
- Apply ice to reduce swelling
- Consult an orthopedic doctor for examination
---

Now analyze the patient's current symptoms. Repeat the format above for each relevant department.
NOTE:
For each symptom, please check for department. If you find different departments then give their answer separately.  
Do not mention the word "context" or how you found the result.
Do not mix treatments or explanations from different departments in one section.
Only output sections for departments clearly supported by the reference material.
"""

    response = model.generate_content(prompt, generation_config={"temperature": 0.3})
    output = response.text.strip()

    try:
        matches = re.findall(
            r"---\s*Department:\s*(.*?)\s*Explanation:\s*(.*?)\s*Treatment:\s*((?:- .+\n?)*)",
            output,
            re.DOTALL,
        )

        if not matches:
            return {
                "department": "Not Identified",
                "answer": output,
                "treatment": "No specific treatment found."
            }

        departments = []
        explanations = []
        treatment_blocks = []

        for dept, explanation, treatment_block in matches:
            departments.append(dept.strip())
            explanations.append(explanation.strip())

            treatments = "\n".join([
                f"- {line.strip('- ').strip()}"
                for line in treatment_block.strip().splitlines()
                if line.strip().startswith("-")
            ])
            treatment_section = f"\nDepartment: {dept.strip()}\n{treatments}"
            treatment_blocks.append(treatment_section)

        return {
            "department": ", ".join(departments),
            "answer": ", ".join(explanations),
            "treatment": "\n".join(treatment_blocks)
        }

    except Exception as e:
        return {
            "department": "Parsing Failed",
            "answer": output,
            "treatment": "Error extracting treatment information."
        }

# --- Flask API Endpoint ---
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        symptoms = data.get("symptoms", "").strip()
        age = int(data.get("age", 30))
        gender = data.get("gender", "Male")

        if not symptoms:
            return jsonify({"error": "No symptoms provided"}), 400

        result = generate_response(symptoms, age, gender)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Run server ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
