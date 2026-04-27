#!/usr/bin/env python3
"""
review_patches.py

CLI tool for reviewing and approving or rejecting persona patches
before they are applied to the living persona system.

Usage:
  python3 backend/scripts/review_patches.py --list
  python3 backend/scripts/review_patches.py --approve <id>
  python3 backend/scripts/review_patches.py --reject <id>
  python3 backend/scripts/review_patches.py --approve-all
  python3 backend/scripts/review_patches.py --summary
"""

import argparse
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "app" / "swarm" / "vuln_intel" / "intel.db"


def list_pending():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT id, persona_id, patch_type, confidence, "
            "source_name, rationale, content, created_at "
            "FROM persona_patches WHERE review_status = 'pending' "
            "ORDER BY created_at DESC"
        ).fetchall()
    if not rows:
        print("No pending patches.")
        return
    for r in rows:
        print(f"\n{'='*60}")
        print(f"ID:         {r[0]}")
        print(f"Persona:    {r[1]}")
        print(f"Type:       {r[2]}")
        print(f"Confidence: {r[3]}")
        print(f"Source:     {r[4]}")
        print(f"Rationale:  {r[5]}")
        print(f"Date:       {r[7]}")
        print(f"Content:\n{r[6]}")


def approve(patch_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE persona_patches SET review_status='approved', "
            "applied=1 WHERE id=?", (patch_id,)
        )
    print(f"Patch {patch_id} approved and applied.")


def reject(patch_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE persona_patches SET review_status='rejected', "
            "applied=0 WHERE id=?", (patch_id,)
        )
    print(f"Patch {patch_id} rejected.")


def approve_all():
    with sqlite3.connect(DB_PATH) as conn:
        n = conn.execute(
            "UPDATE persona_patches SET review_status='approved', "
            "applied=1 WHERE review_status='pending'"
        ).rowcount
    print(f"Approved and applied {n} pending patches.")


def summary():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT persona_id, COUNT(*) as total, "
            "SUM(applied) as applied, MAX(created_at) as last_update "
            "FROM persona_patches GROUP BY persona_id "
            "ORDER BY persona_id"
        ).fetchall()
    print(f"\n{'Persona':<30} {'Total':>6} {'Applied':>8} {'Last update'}")
    print("-" * 65)
    for r in rows:
        print(f"{r[0]:<30} {r[1]:>6} {r[2]:>8} {r[3][:10] if r[3] else 'N/A'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--list",        action="store_true")
    parser.add_argument("--approve",     type=int)
    parser.add_argument("--reject",      type=int)
    parser.add_argument("--approve-all", action="store_true")
    parser.add_argument("--summary",     action="store_true")
    args = parser.parse_args()

    if args.list:        list_pending()
    elif args.approve:   approve(args.approve)
    elif args.reject:    reject(args.reject)
    elif getattr(args, "approve_all", False): approve_all()
    elif args.summary:   summary()
    else:                parser.print_help()
