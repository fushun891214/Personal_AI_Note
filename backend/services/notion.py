import logging
from notion_client import Client
from config import settings

# Initialize Notion Client
notion = Client(auth=settings.NOTION_API_KEY) if settings.NOTION_API_KEY else None

def create_notion_page(title: str, content_markdown: str):
    """Create a new page in the Notion database."""
    if not notion or not settings.NOTION_DATABASE_ID:
        return "Error: Notion credentials not found."

    try:
        # Create the page
        notion.pages.create(
            parent={"database_id": settings.NOTION_DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": title}}]},
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content_markdown[:2000]}}]
                    }
                }
            ]
        )
        return "Success: Page created in Notion!"
    except Exception as e:
        logging.error(f"Notion Error: {e}")
        return f"Error creating Notion page: {e}"
