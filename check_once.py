import scraper as sc
import requests
from state import load_state, save_state
from telegram_bot import send_message
from notifier import _format_message


def main():
    print("Checking CROUS...")

    try:
        current = sc.fetch_all_accommodations()
    except requests.RequestException as exc:
        print(f"CROUS check skipped: network error while fetching listings ({exc})")
        return
    current_ids = {a["id"] for a in current}

    print(f"Found {len(current)} matching accommodations.")

    known_ids = load_state()

    # First run: save existing listings without sending hundreds of alerts.
    if not known_ids:
        print("First run detected. Saving current listings without alerts.")
        save_state(current_ids, current)
        return

    new_items = [a for a in current if a["id"] not in known_ids]

    print(f"New listings: {len(new_items)}")

    for acc in new_items:
        print(f"NEW: {acc['name']} - {acc['price']}")

        send_message(
            _format_message(acc),
            image_url=acc.get("image_url"),
        )

    # Keep all previously known IDs + currently visible IDs.
    save_state(known_ids | current_ids, current)

    print("Done.")


if __name__ == "__main__":
    main()
