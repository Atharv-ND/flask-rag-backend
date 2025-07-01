from pymongo import MongoClient
cardiology_documents=[
  {
    "department": "ENT - Ear Pain (Young Male)",
    "content": "Commonly due to infections or wax buildup. First aid: Apply warm compress, avoid inserting objects in ear, consult ENT if persists."
  },
  {
    "department": "ENT - Ear Pain (Young Female)",
    "content": "Often caused by ear infections or colds. First aid: Use warm cloth near ear, avoid loud noise, and consult for antibiotics if needed."
  },
  {
    "department": "ENT - Hearing Loss (Adult Male)",
    "content": "May result from noise exposure or infection. First aid: Avoid loud sounds, clear earwax gently, and get hearing tested by a specialist."
  },
  {
    "department": "ENT - Hearing Loss (Adult Female)",
    "content": "Can be due to aging or fluid buildup. First aid: Stay away from water exposure, avoid using earbuds, and consult ENT for diagnosis."
  },
  {
    "department": "ENT - Sore Throat (Elderly Male)",
    "content": "Often viral or due to acid reflux. First aid: Gargle with salt water, drink warm fluids, and use throat lozenges."
  },
  {
    "department": "ENT - Sore Throat (Elderly Female)",
    "content": "May result from dry mouth or infection. First aid: Drink warm water, avoid smoking or cold drinks, and consult if it lasts more than 3 days."
  },
  {
    "department": "ENT - Nasal Congestion (Adult Male)",
    "content": "Caused by colds or allergies. First aid: Use saline spray, inhale steam, and avoid cold environments."
  },
  {
    "department": "ENT - Nasal Congestion (Adult Female)",
    "content": "Common in sinus infections or rhinitis. First aid: Use decongestants, stay hydrated, and rest in an upright position."
  },
  {
    "department": "ENT - Ringing in Ears (Elderly Male)",
    "content": "Known as tinnitus, may be age-related. First aid: Reduce caffeine, avoid loud noise, and consult audiologist."
  },
  {
    "department": "ENT - Ringing in Ears (Elderly Female)",
    "content": "Can result from hearing loss or medications. First aid: Avoid silence, play white noise, and consult ENT."
  },
  {
    "department": "Ophthalmology - Blurry Vision (Young Male)",
    "content": "May be due to eye strain or refractive error. First aid: Rest eyes, reduce screen time, and get an eye exam."
  },
  {
    "department": "Ophthalmology - Blurry Vision (Young Female)",
    "content": "Often linked to uncorrected vision or dryness. First aid: Use lubricating drops, blink frequently, and visit optometrist."
  },
  {
    "department": "Ophthalmology - Eye Redness (Adult Male)",
    "content": "Caused by conjunctivitis or irritation. First aid: Avoid rubbing eyes, use sterile drops, and maintain eye hygiene."
  },
  {
    "department": "Ophthalmology - Eye Redness (Adult Female)",
    "content": "Often from dryness or infection. First aid: Apply cold compress, avoid cosmetics, and use artificial tears."
  },
  {
    "department": "Ophthalmology - Eye Pain (Elderly Male)",
    "content": "May indicate glaucoma or dry eye. First aid: Avoid bright light, rest eyes, and seek immediate attention if sudden pain occurs."
  },
  {
    "department": "Ophthalmology - Eye Pain (Elderly Female)",
    "content": "Can result from chronic dry eye or strain. First aid: Use prescribed eye drops, protect from wind, and consult ophthalmologist."
  },
  {
    "department": "Ophthalmology - Itchy Eyes (Adult Male)",
    "content": "Usually due to allergy or dryness. First aid: Use antihistamine drops, avoid rubbing, and limit pollen exposure."
  },
  {
    "department": "Ophthalmology - Itchy Eyes (Adult Female)",
    "content": "Caused by dust, allergy, or eye makeup. First aid: Rinse with clean water, use anti-allergy drops, and avoid contact lenses."
  },
  {
    "department": "Ophthalmology - Sensitivity to Light (Young Male)",
    "content": "May indicate inflammation or migraine. First aid: Wear sunglasses, avoid screens, and rest in a dark room."
  },
  {
    "department": "Ophthalmology - Sensitivity to Light (Young Female)",
    "content": "Linked to infection or dryness. First aid: Stay in low light, wear UV protection, and use lubricating drops."
  },
  {
    "department": "Psychiatry - Persistent Sadness (Adult Male)",
    "content": "Could be a sign of depression. First aid: Talk to a trusted person, practice deep breathing, and seek professional counseling."
  },
  {
    "department": "Psychiatry - Persistent Sadness (Adult Female)",
    "content": "Often linked to emotional stress or hormonal changes. First aid: Maintain routine, express feelings, and consult therapist."
  },
  {
    "department": "Psychiatry - Anxiety (Young Male)",
    "content": "Can arise from academic or peer pressure. First aid: Practice mindfulness, deep breathing, and avoid stimulants."
  },
  {
    "department": "Psychiatry - Anxiety (Young Female)",
    "content": "May relate to school or social stress. First aid: Talk to parents, maintain sleep hygiene, and reduce screen time."
  },
  {
    "department": "Psychiatry - Insomnia (Elderly Male)",
    "content": "Often due to aging or medication. First aid: Avoid caffeine, keep regular sleep schedule, and try relaxation techniques."
  },
  {
    "department": "Psychiatry - Insomnia (Elderly Female)",
    "content": "Caused by menopause or anxiety. First aid: Limit screen time before bed, use calming music, and consult for sleep aids."
  },
  {
    "department": "Psychiatry - Panic Attacks (Adult Male)",
    "content": "Triggered by stress or trauma. First aid: Sit down, take slow deep breaths, and remind self it will pass."
  },
  {
    "department": "Psychiatry - Panic Attacks (Adult Female)",
    "content": "May occur in crowded or stressful situations. First aid: Grounding techniques, slow breathing, and avoid triggering environments."
  },
  {
    "department": "Psychiatry - Mood Swings (Young Male)",
    "content": "Often seen during puberty or stress. First aid: Encourage open communication, journaling, and provide emotional support."
  },
  {
    "department": "Psychiatry - Mood Swings (Young Female)",
    "content": "Related to hormonal shifts or social pressure. First aid: Maintain a routine, avoid isolation, and consult if persistent."
  }
]

# ✅ Your Atlas connection string
MONGO_URI = "mongodb+srv://rag:rag_21@cluster0.os6ipa0.mongodb.net/"

# Connect to the cluster and insert
client = MongoClient(MONGO_URI)
db = client["Healthcare"]
collection = db["symptom"]

# Insert all documents
collection.insert_many(cardiology_documents)

print("✅ Successfully inserted Cardiology documents into MongoDB.")
