#!/usr/bin/env python3
"""
migrate_merge.py — Merge SQLite data into PostgreSQL (one-shot, production safe).

Usage (run from Render shell):
    python3 migrate_merge.py          # Dry-run (no changes)
    python3 migrate_merge.py --go     # Execute migration

What it does:
  1. Reads palabras + rankings from /mnt/data/palabras.db (SQLite)
  2. Inserts into PostgreSQL, skipping duplicates
  3. For duplicate rankings, keeps the HIGHER puntuacion
  4. Wraps everything in a transaction (rollback on error)
"""

import os
import sys
import sqlite3
from datetime import datetime

# --- Config ---
SQLITE_PATH = "/mnt/data/palabras.db"
DRY_RUN = "--go" not in sys.argv
BATCH_SIZE = 500


def main():
    if DRY_RUN:
        print("=" * 60)
        print("  DRY RUN — no changes will be made")
        print("  Run with --go to execute the migration")
        print("=" * 60)
    else:
        print("=" * 60)
        print("  LIVE MIGRATION — changes WILL be committed")
        print("=" * 60)

    # 1. Check SQLite file
    if not os.path.exists(SQLITE_PATH):
        print(f"\n[ERROR] SQLite file not found: {SQLITE_PATH}")
        sys.exit(1)

    # 2. Read SQLite data
    print(f"\n[1/4] Reading SQLite: {SQLITE_PATH}")
    sq = sqlite3.connect(SQLITE_PATH)
    sq_cur = sq.cursor()

    sq_cur.execute("SELECT palabra FROM palabra")
    sqlite_palabras = set()
    for row in sq_cur.fetchall():
        w = row[0].strip() if row[0] else ""
        if w:
            sqlite_palabras.add(w)
    print(f"       Palabras in SQLite: {len(sqlite_palabras)}")

    sq_cur.execute("SELECT palabra, puntuacion FROM ranking")
    sqlite_rankings = {}
    for row in sq_cur.fetchall():
        w = row[0].strip() if row[0] else ""
        p = row[1] if row[1] else 1
        if w:
            # Keep highest score if duplicate in SQLite itself
            if w not in sqlite_rankings or p > sqlite_rankings[w]:
                sqlite_rankings[w] = p
    print(f"       Rankings in SQLite: {len(sqlite_rankings)}")
    sq.close()

    # 3. Connect to PostgreSQL via Flask app
    print("\n[2/4] Connecting to PostgreSQL...")
    from app import create_app
    app = create_app()

    with app.app_context():
        from models import db, Palabra, Ranking

        # 4. Read existing PG data
        pg_palabras = set(r[0] for r in db.session.query(Palabra.palabra).all())
        pg_rankings = {r[0]: r[1] for r in db.session.query(Ranking.palabra, Ranking.puntuacion).all()}
        print(f"       PG palabras existing: {len(pg_palabras)}")
        print(f"       PG rankings existing: {len(pg_rankings)}")

        # 5. Calculate what needs to be inserted/updated
        new_palabras = sqlite_palabras - pg_palabras
        new_rankings = {}
        updated_rankings = {}

        for w, score in sqlite_rankings.items():
            if w not in pg_rankings:
                new_rankings[w] = score
            elif score > pg_rankings[w]:
                updated_rankings[w] = score

        print(f"\n[3/4] Migration plan:")
        print(f"       Palabras to INSERT:  {len(new_palabras)}")
        print(f"       Rankings to INSERT:  {len(new_rankings)}")
        print(f"       Rankings to UPDATE:  {len(updated_rankings)} (higher score from SQLite)")
        print(f"       Palabras skipped:    {len(sqlite_palabras) - len(new_palabras)} (already in PG)")
        print(f"       Rankings skipped:    {len(sqlite_rankings) - len(new_rankings) - len(updated_rankings)}")

        if DRY_RUN:
            print("\n[DRY RUN] No changes made. Run with --go to execute.")
            # Show sample
            if new_palabras:
                sample = list(new_palabras)[:5]
                print(f"\n  Sample new palabras: {sample}")
            if new_rankings:
                sample = list(new_rankings.items())[:5]
                print(f"  Sample new rankings: {sample}")
            return

        # 6. Execute migration in a transaction
        print(f"\n[4/4] Executing migration...")
        try:
            # Insert new palabras in batches
            count = 0
            batch = []
            for w in new_palabras:
                batch.append(Palabra(palabra=w))
                if len(batch) >= BATCH_SIZE:
                    db.session.bulk_save_objects(batch)
                    count += len(batch)
                    print(f"       Palabras inserted: {count}/{len(new_palabras)}", end="\r")
                    batch = []
            if batch:
                db.session.bulk_save_objects(batch)
                count += len(batch)
            print(f"       Palabras inserted: {count}/{len(new_palabras)}")

            # Insert new rankings in batches
            count = 0
            batch = []
            for w, score in new_rankings.items():
                batch.append(Ranking(palabra=w, puntuacion=score))
                if len(batch) >= BATCH_SIZE:
                    db.session.bulk_save_objects(batch)
                    count += len(batch)
                    print(f"       Rankings inserted: {count}/{len(new_rankings)}", end="\r")
                    batch = []
            if batch:
                db.session.bulk_save_objects(batch)
                count += len(batch)
            print(f"       Rankings inserted: {count}/{len(new_rankings)}")

            # Update rankings with higher scores
            count = 0
            for w, score in updated_rankings.items():
                db.session.query(Ranking).filter_by(palabra=w).update({"puntuacion": score})
                count += 1
            print(f"       Rankings updated:  {count}")

            # Commit
            db.session.commit()
            print("\n[OK] Migration committed successfully!")

            # Final counts
            final_p = Palabra.query.count()
            final_r = Ranking.query.count()
            print(f"\n  Final PG palabras: {final_p}")
            print(f"  Final PG rankings: {final_r}")
            print(f"  Users (unchanged): {db.session.execute(db.text('SELECT COUNT(*) FROM users')).scalar()}")

        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] Migration failed, ROLLED BACK: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
