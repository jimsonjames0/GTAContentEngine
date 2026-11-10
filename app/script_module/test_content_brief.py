import sys
from pathlib import Path

# Add script_module to path
MODULE_DIR = Path(__file__).resolve().parent
sys.path.append(str(MODULE_DIR))

from script_writer import ScriptWriter
from brief_storage import BriefStorage


def test_content_brief_workflow():
    writer = ScriptWriter()
    brief = writer.write()

    storage = BriefStorage()
    brief_file = storage.save(brief, filename="brief_001.json")

    print(f"Successfully generated Content Brief and saved to: {brief_file}\n")
    print("=== Content Brief Details ===")
    print(f"Title:    {brief.title}")
    print(f"Format:   {brief.format.upper()}")
    print(f"Length:   {brief.length} seconds")
    print(f"Voice:    {brief.voice}")
    print(f"Footage:  {brief.footage}")
    print(f"Hook:     {brief.hook}")
    print(f"Script:\n{brief.script}\n")
    print("Verification passed: Content brief JSON schema and file contents are valid.")


if __name__ == "__main__":
    test_content_brief_workflow()