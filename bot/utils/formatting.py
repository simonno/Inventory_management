"""Response formatters and message utilities for the Telegram inventory bot."""

from typing import List, Optional
from collections import defaultdict


def split_message(text: str, limit: int = 4096) -> List[str]:
    if len(text) <= limit:
        return [text]
    chunks = []
    current = []
    current_len = 0
    for line in text.splitlines(keepends=True):
        if current_len + len(line) > limit and current:
            chunks.append("".join(current))
            current = []
            current_len = 0
        current.append(line)
        current_len += len(line)
    if current:
        chunks.append("".join(current))
    return chunks


def format_condition_flag(condition: str) -> str:
    return " ⚠️" if condition != "Good" else ""


def format_live_stock(dresses) -> str:
    if not dresses:
        return "No dresses currently in stock."

    grouped = defaultdict(list)
    for d in dresses:
        grouped[d.model_number].append(d)

    lines = ["📦 *Live Stock*\n"]
    for model in sorted(grouped):
        lines.append(f"*Model {model}*")
        for d in grouped[model]:
            flag = format_condition_flag(d.dress_condition.value)
            lines.append(
                f"  • Size {d.size}, Cup {d.cup_size.value} — "
                f"{d.storage_location.value} — "
                f"{d.dress_condition.value}{flag}"
            )
        lines.append("")

    total = len(dresses)
    lines.append(f"Total: {total} dress{'es' if total != 1 else ''} in stock")
    return "\n".join(lines)


def format_future_stock(result: dict) -> str:
    dresses = result.get("dresses", [])
    new_orders = result.get("new_orders", [])

    if not dresses and not new_orders:
        return "All inventory is currently in-house. No future stock pending."

    lines = ["🔮 *Future Stock*\n"]

    status_order = ["In Sewing", "Out to Bride", "Abroad"]
    by_status = defaultdict(list)
    for d in dresses:
        by_status[d.status.value].append(d)

    for status_label in status_order:
        group = by_status.get(status_label, [])
        if not group:
            continue
        lines.append(f"*{status_label}*")
        for d in group:
            linked = d.orders[0] if d.orders else None
            if linked:
                date_info = f"→ wedding {linked.wedding_date} (bride: {linked.bride_name})"
            else:
                date_info = "→ return est. unknown"
            lines.append(
                f"  • #{d.item_id} Model {d.model_number}, "
                f"Size {d.size}, Cup {d.cup_size.value} {date_info}"
            )
        lines.append("")

    if new_orders:
        lines.append("*New Orders (not yet received)*")
        for o in new_orders:
            lines.append(
                f"  • Order #{o.order_id} — Model {o.model_number}, "
                f"Size {o.size}, Cup {o.cup_size.value} — "
                f"{o.bride_name} — wedding {o.wedding_date}"
            )

    return "\n".join(lines)


def format_dress_detail(dresses) -> str:
    if not dresses:
        return None

    lines = [f"👗 *Model {dresses[0].model_number}*\n"]
    for d in dresses:
        flag = format_condition_flag(d.dress_condition.value)
        lines.append(
            f"*#{d.item_id}* Size {d.size}, Cup {d.cup_size.value} — "
            f"{d.storage_location.value} — {d.status.value} — "
            f"{d.dress_condition.value}{flag}"
        )
        if d.orders:
            for o in d.orders:
                lines.append(f"   └ Linked order: {o.bride_name}, wedding {o.wedding_date}")
        lines.append("")

    total = len(dresses)
    lines.append(f"Total: {total} record{'s' if total != 1 else ''}")
    return "\n".join(lines)


def format_orders(orders, days: Optional[int] = None) -> str:
    header = f"next {days} days" if days is not None else "all orders"
    if not orders:
        if days is not None:
            return f"No orders with weddings in the next {days} days."
        return "No active orders found."

    lines = [f"📋 *Active Orders ({header})*\n"]
    for i, o in enumerate(orders, 1):
        lines.append(
            f"{i}. {o.bride_name} — Model {o.model_number}, "
            f"Size {o.size}, Cup {o.cup_size.value} — "
            f"wedding {o.wedding_date} [{o.order_type.value}]"
        )

    total = len(orders)
    lines.append(f"\nTotal: {total} order{'s' if total != 1 else ''}")
    return "\n".join(lines)


def format_status_update(old_status: str, dress) -> str:
    return (
        f"✅ *Updated Dress #{dress.item_id}*\n\n"
        f"Model: {dress.model_number} | Size: {dress.size} | Cup: {dress.cup_size.value}\n"
        f"Status: {old_status} → {dress.status.value}\n"
        f"Location: {dress.storage_location.value}"
    )


def format_dress_added(dress) -> str:
    return (
        f"✅ *Dress Added*\n\n"
        f"#{dress.item_id} Model {dress.model_number}, "
        f"Size {dress.size}, Cup {dress.cup_size.value}\n"
        f"Status: {dress.status.value} | Location: {dress.storage_location.value} | "
        f"Condition: {dress.dress_condition.value}"
    )


HELP_TEXT = (
    "🤖 *Bridal Inventory Bot — Commands*\n\n"
    "/stock — Show all available dresses (In Stock & Display)\n"
    "/future — Show dresses expected back \\+ new orders pending\n"
    "/dress <model> — Look up all records for a model number\n"
    "/orders \\[days\\] — List active orders (optional: next N days)\n"
    "/status <id> <status> — Update a dress status\n"
    "/add <model> <size> <cup> <location> — Add a new dress\n"
    "/help — Show this help message"
)

VALID_STATUSES = [
    "in stock", "display", "abroad", "in sewing", "out to bride"
]

VALID_STATUSES_TEXT = "\n".join(f"  • {s}" for s in VALID_STATUSES)
