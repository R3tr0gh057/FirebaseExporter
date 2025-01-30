import os
import base64
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate(r"C:\Users\AAGA SUSAN ELDOSE\Downloads\xact-db-firebase-adminsdk-aznal-96fd1b31f8.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

main_collection = db.collection("2025")

# Fetch all colleges
colleges = main_collection.stream()

for college in colleges:
    college_name = college.id  # Extract college name dynamically
    college_path = os.path.join(os.getcwd(), college_name)  # Folder path for the college

    # Create a folder for the college if not exists
    os.makedirs(college_path, exist_ok=True)

    # Navigate to Participants inside each college
    participants_ref = college.reference.collection("Participants")
    participants = participants_ref.stream()

    for participant in participants:
        participant_name = participant.id  # Extract participant name
        participant_data = participant.to_dict()  # Convert Firestore data to dict

        # Check if 'wNo' exists
        if 'wNo' in participant_data:
            try:
                # Decode base64 content
                image_data = base64.b64decode(participant_data['wNo'])

                # Save the image
                image_path = os.path.join(college_path, f"{participant_name}.png")
                with open(image_path, "wb") as image_file:
                    image_file.write(image_data)

                print(f"Saved: {image_path}")

            except Exception as e:
                print(f"Error processing {participant_name} in {college_name}: {e}")
