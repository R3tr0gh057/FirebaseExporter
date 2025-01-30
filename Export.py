import os
import base64
import firebase_admin
from firebase_admin import credentials, firestore
from tqdm import tqdm
from rich.console import Console
from rich.progress import Progress
import imghdr

# Initialize Firebase Admin SDK
cred = credentials.Certificate(r"C:\Users\Niranjan\Downloads\temp\FirebaseExporter\confg.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()
console = Console()

# Reference the main collection (2025 in your case)
main_collection = db.collection("2025")

# Fetch all colleges
colleges = list(main_collection.stream())  # Convert to list for progress tracking

def fix_base64_padding(encoded_str):
    """Ensures Base64 string has proper padding"""
    missing_padding = len(encoded_str) % 4
    if missing_padding:
        encoded_str += '=' * (4 - missing_padding)
    return encoded_str

def extract_format_and_data(base64_string):
    """Extracts the format (png, jpg, etc.) and cleans Base64 data"""
    if base64_string.startswith("data:image"):
        mime_type, base64_data = base64_string.split(",", 1)  # Split at first comma
        image_format = mime_type.split("/")[1].split(";")[0]  # Extract format (jpeg, png, etc.)
    else:
        image_format = None
        base64_data = base64_string  # If no prefix, assume raw Base64

    return image_format, base64_data

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

            # Check if 'tImg' exists
            if 'tImg' in participant_data:
                try:
                    base64_string = participant_data['tImg'].strip()  # Remove accidental spaces

                    # ✅ Debugging: Print first few characters of base64 string
                    console.print(f"[cyan]Processing {participant_name} - Base64 starts with:[/] {base64_string[:30]}...")

                    # Extract format and clean Base64 data
                    image_format, base64_data = extract_format_and_data(base64_string)

                    # Ensure proper padding
                    base64_data = fix_base64_padding(base64_data)

                    # Decode Base64
                    image_data = base64.b64decode(base64_data)

                    # If no format is detected from the string, detect from image bytes
                    if not image_format:
                        image_format = imghdr.what(None, h=image_data)  # Detect format from bytes
                        if not image_format:
                            raise ValueError("❌ Decoded data is not a valid image format")

                    # Convert 'jpeg' to 'jpg' for correct file extension
                    if image_format == "jpeg":
                        image_format = "jpg"

                    # Save the image with the correct extension
                    image_path = os.path.join(college_path, f"{participant_name}.{image_format}")
                    with open(image_path, "wb") as image_file:
                        image_file.write(image_data)

                    console.print(f"[bold green]✔ Saved:[/] {image_path}")

                except Exception as e:
                    console.print(f"[bold red]❌ Error processing {participant_name} in {college_name}:[/] {e}")

console.print("[bold magenta]🎉 Process completed![/bold magenta]")
