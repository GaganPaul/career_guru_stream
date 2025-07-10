import firebase_admin
from firebase_admin import credentials, firestore

# ----------- Initialize Firebase -----------
cred = credentials.Certificate("C:\\Users\\Gagan\\OneDrive\\Desktop\\career_guru_stream\\careerguru-f1540-firebase-adminsdk-fbsvc-e0a2a00921.json")  # Replace with your key file path
firebase_admin.initialize_app(cred)

db = firestore.client()

# ----------- 1. Create a user -----------
user_id = "user_001"
user_data = {
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": firestore.SERVER_TIMESTAMP
}
db.collection("users").document(user_id).set(user_data)

# ----------- 2. Add chat history for the user -----------
chat_data = {
    "user_id": user_id,
    "messages": [
        {"sender": "user", "text": "Tell me about software engineering"},
        {"sender": "Career Guru", "text": "Sure! Software engineering is..."}
    ],
    "timestamp": firestore.SERVER_TIMESTAMP
}
db.collection("chats").add(chat_data)

# ----------- 3. Add interview session -----------
interview_data = {
    "user_id": user_id,
    "role": "Software Developer",
    "questions": [
        {"q": "Tell me about yourself", "a": "I am a developer..."},
        {"q": "Why should we hire you?", "a": "Because..."}
    ],
    "timestamp": firestore.SERVER_TIMESTAMP
}
db.collection("interviews").add(interview_data)

# ----------- 4. Add resume analysis -----------
resume_data = {
    "user_id": user_id,
    "file_name": "john_doe_resume.pdf",
    "content": "John Doe\nSoftware Engineer\nExperience in Python, JavaScript...",
    "feedback": """- Improve formatting consistency.\n- Highlight key projects.\n- Emphasize achievements with metrics.\n- Add relevant tech keywords.""",
    "timestamp": firestore.SERVER_TIMESTAMP
}
db.collection("resumes").add(resume_data)

print("✅ Firebase setup completed and all sample data added.")
