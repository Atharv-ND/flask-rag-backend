from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
import os
import re
from functools import lru_cache

from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import google.generativeai as genai

# --- Load env and setup ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")
MONGO_URI = os.getenv("MONGO_URI")

app = Flask(__name__)
CORS(app)

# --- Mongo ---
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["Healthcare"]
collection = db["symptom"]

# --- FAISS loading optimized ---
@lru_cache(maxsize=1)
def get_vector_store():
    # ✅ Load ALL documents from MongoDB
    kb_records = list(collection.find({}))  # ← Removed .limit(20)
    
    documents = [
        Document(page_content=rec["content"], metadata={"title": rec["department"]})
        for rec in kb_records
    ]

    # ✅ You can continue using the efficient embedding model
    embedding_model = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

    return FAISS.from_documents(documents, embedding_model)

def retrieve_context(symptom_query: str, k=3):
    vector_store = get_vector_store()
    return vector_store.similarity_search(symptom_query, k=k)

# --- RAG logic ---
def generate_response(symptoms: str, age: int, gender: str):
    age_group = "Young" if age < 20 else "Adult" if age < 60 else "Elderly"
    profile = f"{age_group} {gender.capitalize()}"
    retrieved_docs = retrieve_context(symptoms, k=6)

    if not retrieved_docs:
        return {
            "department": "Not Identified",
            "answer": "No relevant information found.",
            "treatment": "- Visit a doctor\n- Avoid self-diagnosis\n- Keep symptom log"
        }

    context = "\n\n".join([f"{doc.metadata['title']}:\n{doc.page_content}" for doc in retrieved_docs])

    prompt = f"""
You are a medical assistant AI helping a patient who described the following symptoms: "{symptoms}"
Patient Profile: {profile}

ONLY use the medical information provided below to generate your response:
{context}

⚠️ VERY IMPORTANT:
- Do not mention "context", "documents", "knowledge base", or anything technical.
- Do not say things like "Based on the context" or "According to the retrieved information".
- Speak as if you are a doctor explaining directly to a patient.

Instructions:
1. Identify the department based on symptoms.
2. Give a brief explanation in plain, patient-friendly language.
3. List the treatment options extracted only from the provided information.

Format your output like this :
Department: <department name>
Explanation: <simple reason in plain language>
Treatment:
- bullet point
- bullet point
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
            return {"department": "Not Identified", "answer": output, "treatment": "No specific treatment found."}

        departments, explanations, treatment_blocks = [], [], []

        for dept, explanation, treatment_block in matches:
            departments.append(dept.strip())
            explanations.append(explanation.strip())

            # Clean and filter treatment lines (remove empty ones)
            treatments = "\n".join([
                f"- {line.strip('- ').strip()}"
                for line in treatment_block.strip().splitlines()
                if line.strip().startswith("-") and line.strip("- ").strip()  # ✅ Remove blank lines
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
            "treatment": f"Error: {str(e)}"
        }

# --- API Route ---
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

# --- Required for Render ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
