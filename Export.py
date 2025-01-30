import os
import base64
import firebase_admin
from firebase_admin import credentials, firestore
from tqdm import tqdm
from rich.console import Console
from rich.progress import Progress

# Initialize Firebase Admin SDK
cred = credentials.Certificate(r"C:\Users\AAGA SUSAN ELDOSE\Downloads\xact-db-firebase-adminsdk-aznal-96fd1b31f8.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()
console = Console()

# Reference the main collection (2025 in your case)
main_collection = db.collection("2025")

# Fetch all colleges
colleges = list(main_collection.stream())  # Convert to list for progress tracking

with Progress() as progress:
    college_task = progress.add_task("[cyan]Processing Colleges...", total=len(colleges))

    for college in colleges:
        college_name = college.id  # Extract college name dynamically
        college_path = os.path.join(os.getcwd(), college_name)  # Folder path for the college

        # Create a folder for the college if not exists
        os.makedirs(college_path, exist_ok=True)

        # Navigate to Participants inside each college
        participants_ref = college.reference.collection("Participants")
        participants = list(participants_ref.stream())  # Convert to list for tqdm

        progress.update(college_task, description=f"[green]College: {college_name}", advance=1)

        if not participants:
            console.print(f"[yellow]No participants found for {college_name}[/yellow]")
            continue

        # Progress bar for participants
        for participant in tqdm(participants, desc=f"[{college_name}] Processing Participants", leave=False):
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

                    console.print(f"[bold green]✔ Saved:[/] {image_path}")

                except Exception as e:
                    console.print(f"[bold red]❌ Error processing {participant_name} in {college_name}:[/] {e}")

console.print("[bold magenta]🎉 Process completed![/bold magenta]")