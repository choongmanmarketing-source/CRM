#!/usr/bin/env python3
"""Restaurant CRM with point accumulation using SQLite."""

from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DB_PATH = Path(__import__("os").environ.get("CRM_DB_PATH", "/tmp/crm.db"))


@dataclass
class Customer:
    id: int
    name: str
    phone: str
    points: int
    tier: str


class RestaurantCRM:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL UNIQUE,
                points INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                earned_points INTEGER NOT NULL,
                used_points INTEGER NOT NULL DEFAULT 0,
                note TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(customer_id) REFERENCES customers(id)
            );
            """
        )
        self.conn.commit()

    def add_customer(self, name: str, phone: str) -> Customer:
        ts = self._now()
        cur = self.conn.execute(
            "INSERT INTO customers (name, phone, created_at) VALUES (?, ?, ?)",
            (name, phone, ts),
        )
        self.conn.commit()
        return self.get_customer_by_id(cur.lastrowid)

    def get_customer_by_phone(self, phone: str) -> Customer | None:
        row = self.conn.execute(
            "SELECT id, name, phone, points FROM customers WHERE phone = ?", (phone,)
        ).fetchone()
        return self._row_to_customer(row) if row else None

    def get_customer_by_id(self, customer_id: int) -> Customer:
        row = self.conn.execute(
            "SELECT id, name, phone, points FROM customers WHERE id = ?", (customer_id,)
        ).fetchone()
        if not row:
            raise ValueError(f"Customer id={customer_id} not found")
        return self._row_to_customer(row)

    def list_customers(self) -> Iterable[Customer]:
        rows = self.conn.execute(
            "SELECT id, name, phone, points FROM customers ORDER BY points DESC, id ASC"
        ).fetchall()
        return [self._row_to_customer(row) for row in rows]

    def record_purchase(
        self,
        phone: str,
        amount: float,
        earn_rate: int = 10,
        use_points: int = 0,
        note: str | None = None,
    ) -> Customer:
        if amount < 0:
            raise ValueError("Purchase amount must be non-negative")
        if earn_rate <= 0:
            raise ValueError("earn_rate must be > 0")

        customer = self.get_customer_by_phone(phone)
        if not customer:
            raise ValueError("Customer not found. Please add customer first.")

        earned = int(amount // earn_rate)
        if use_points < 0:
            raise ValueError("use_points must be non-negative")
        if use_points > customer.points:
            raise ValueError("Not enough points")

        new_points = customer.points + earned - use_points
        ts = self._now()
        self.conn.execute(
            "UPDATE customers SET points = ? WHERE id = ?", (new_points, customer.id)
        )
        self.conn.execute(
            """
            INSERT INTO transactions (customer_id, amount, earned_points, used_points, note, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (customer.id, amount, earned, use_points, note, ts),
        )
        self.conn.commit()
        return self.get_customer_by_id(customer.id)

    def _row_to_customer(self, row: sqlite3.Row) -> Customer:
        points = int(row["points"])
        return Customer(
            id=int(row["id"]),
            name=str(row["name"]),
            phone=str(row["phone"]),
            points=points,
            tier=self._tier_from_points(points),
        )

    @staticmethod
    def _tier_from_points(points: int) -> str:
        if points >= 1000:
            return "Platinum"
        if points >= 500:
            return "Gold"
        if points >= 200:
            return "Silver"
        return "Member"

    @staticmethod
    def _now() -> str:
        return datetime.now(tz=timezone.utc).isoformat()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Restaurant CRM (Point System)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    add_customer = sub.add_parser("add-customer", help="Add a new customer")
    add_customer.add_argument("--name", required=True)
    add_customer.add_argument("--phone", required=True)

    purchase = sub.add_parser("purchase", help="Record purchase and update points")
    purchase.add_argument("--phone", required=True)
    purchase.add_argument("--amount", type=float, required=True)
    purchase.add_argument("--earn-rate", type=int, default=10, help="X baht per 1 point")
    purchase.add_argument("--use-points", type=int, default=0)
    purchase.add_argument("--note", default=None)

    profile = sub.add_parser("profile", help="Show customer profile")
    profile.add_argument("--phone", required=True)

    sub.add_parser("list-customers", help="List all customers")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    crm = RestaurantCRM()

    try:
        if args.cmd == "add-customer":
            customer = crm.add_customer(args.name, args.phone)
            print(
                f"Added customer #{customer.id}: {customer.name} ({customer.phone}) | "
                f"points={customer.points} | tier={customer.tier}"
            )

        elif args.cmd == "purchase":
            customer = crm.record_purchase(
                phone=args.phone,
                amount=args.amount,
                earn_rate=args.earn_rate,
                use_points=args.use_points,
                note=args.note,
            )
            print(
                f"Updated: {customer.name} ({customer.phone}) | "
                f"points={customer.points} | tier={customer.tier}"
            )

        elif args.cmd == "profile":
            customer = crm.get_customer_by_phone(args.phone)
            if not customer:
                raise ValueError("Customer not found")
            print(
                f"Customer #{customer.id}: {customer.name} ({customer.phone}) | "
                f"points={customer.points} | tier={customer.tier}"
            )

        elif args.cmd == "list-customers":
            customers = list(crm.list_customers())
            if not customers:
                print("No customers yet")
            for c in customers:
                print(
                    f"#{c.id} {c.name:<20} phone={c.phone:<15} "
                    f"points={c.points:<4} tier={c.tier}"
                )

    except sqlite3.IntegrityError:
        print("Error: phone number already exists")
    except ValueError as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
