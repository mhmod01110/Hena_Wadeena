"""Business logic for analytics dashboards and exports."""

from __future__ import annotations

import csv
import io
from collections import Counter, defaultdict
from datetime import date, datetime, time, timezone
from typing import Any
from uuid import uuid4

from models import MetricEvent
from repositories.metric_event_repository import SqlAlchemyMetricEventRepository


class MetricEventService:

    def __init__(self, repository: SqlAlchemyMetricEventRepository):
        self._repository = repository

    async def ingest_event(
        self,
        *,
        event_type: str,
        actor_id: str | None,
        actor_role: str | None,
        entity_type: str | None,
        entity_id: str | None,
        amount: float | None,
        city: str | None,
        payment_method: str | None,
        price: float | None,
        query: str | None,
        results_count: int | None,
        occurred_at: datetime | None,
    ) -> MetricEvent:
        event = MetricEvent(
            title=f"{event_type}:{uuid4()}",
            status="recorded",
            event_type=event_type,
            actor_id=actor_id,
            actor_role=actor_role,
            entity_type=entity_type,
            entity_id=entity_id,
            amount=amount,
            city=city,
            payment_method=payment_method,
            list_price=price,
            search_query=query,
            results_count=results_count,
        )

        if occurred_at is not None:
            if occurred_at.tzinfo is None:
                occurred_at = occurred_at.replace(tzinfo=timezone.utc)
            event.created_at = occurred_at
            event.updated_at = occurred_at

        return await self._repository.create_event(event)

    async def platform_overview(self, date_from: date, date_to: date) -> dict[str, Any]:
        events = [self._normalize_event(event) for event in await self._events_between(date_from, date_to)]

        users = {event["actor_id"] for event in events if event["actor_id"]}
        listings = [event for event in events if event["event_type"].startswith("market.listing")]
        bookings = [event for event in events if event["event_type"].startswith("guide.booking")]
        revenue_amount = sum(self._safe_amount(event.get("amount")) for event in events if event["event_type"].startswith("payment."))

        return {
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "total_events": len(events),
            "users": {
                "active_users": len(users),
                "new_users": sum(1 for event in events if event["event_type"] in {"auth.user.created", "user.created", "user.registered"}),
            },
            "listings": {
                "created": sum(1 for event in listings if event["event_type"].endswith("created")),
                "updated": sum(1 for event in listings if event["event_type"].endswith("updated")),
                "verified": sum(1 for event in listings if event["event_type"].endswith("verified")),
            },
            "bookings": {
                "requested": sum(1 for event in bookings if event["event_type"].endswith("requested")),
                "completed": sum(1 for event in bookings if event["event_type"].endswith("completed")),
                "cancelled": sum(1 for event in bookings if event["event_type"].endswith("cancelled")),
            },
            "revenue": {"total_amount": round(revenue_amount, 2)},
        }

    async def user_analytics(self, date_from: date, date_to: date, role: str | None) -> dict[str, Any]:
        events = [self._normalize_event(event) for event in await self._events_between(date_from, date_to)]

        users_seen = set()
        role_counter = Counter()
        new_users = 0

        for event in events:
            actor_id = event["actor_id"]
            if actor_id:
                users_seen.add(actor_id)

            event_role = str(event.get("actor_role") or "unknown")
            if actor_id:
                role_counter[event_role] += 1

            if event["event_type"] in {"auth.user.created", "user.created", "user.registered"}:
                if role and event_role != role:
                    continue
                new_users += 1

        if role:
            active_users = len({event["actor_id"] for event in events if event["actor_id"] and str(event.get("actor_role") or "unknown") == role})
        else:
            active_users = len(users_seen)

        return {
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "new_users": new_users,
            "active_users": active_users,
            "events_by_role": dict(role_counter),
        }

    async def listing_analytics(self, date_from: date, date_to: date, city: str | None) -> dict[str, Any]:
        events = [self._normalize_event(event) for event in await self._events_between(date_from, date_to)]

        listing_events = [event for event in events if event["event_type"].startswith("market.listing")]
        if city:
            city_lower = city.lower()
            listing_events = [event for event in listing_events if str(event.get("city") or "").lower() == city_lower]

        prices = [self._safe_amount(event.get("price")) for event in listing_events if event.get("price") is not None]
        prices = [value for value in prices if value > 0]

        return {
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "city": city,
            "created": sum(1 for event in listing_events if event["event_type"].endswith("created")),
            "updated": sum(1 for event in listing_events if event["event_type"].endswith("updated")),
            "verified": sum(1 for event in listing_events if event["event_type"].endswith("verified")),
            "views": sum(1 for event in listing_events if event["event_type"].endswith("viewed")),
            "avg_price": round(sum(prices) / len(prices), 2) if prices else 0.0,
        }

    async def booking_analytics(self, date_from: date, date_to: date) -> dict[str, Any]:
        events = [self._normalize_event(event) for event in await self._events_between(date_from, date_to)]

        booking_events = [event for event in events if event["event_type"].startswith("guide.booking")]
        requested = sum(1 for event in booking_events if event["event_type"].endswith("requested"))
        confirmed = sum(1 for event in booking_events if event["event_type"].endswith("confirmed"))
        completed = sum(1 for event in booking_events if event["event_type"].endswith("completed"))
        cancelled = sum(1 for event in booking_events if event["event_type"].endswith("cancelled"))

        completion_rate = round((completed / requested) * 100, 2) if requested else 0.0
        confirmation_rate = round((confirmed / requested) * 100, 2) if requested else 0.0

        return {
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "requested": requested,
            "confirmed": confirmed,
            "completed": completed,
            "cancelled": cancelled,
            "confirmation_rate": confirmation_rate,
            "completion_rate": completion_rate,
        }

    async def revenue_analytics(self, date_from: date, date_to: date, method: str | None) -> dict[str, Any]:
        events = [self._normalize_event(event) for event in await self._events_between(date_from, date_to)]

        payment_events = [event for event in events if event["event_type"].startswith("payment.")]
        if method:
            method_lower = method.lower()
            payment_events = [event for event in payment_events if str(event.get("payment_method") or "").lower() == method_lower]

        amounts = [self._safe_amount(event.get("amount")) for event in payment_events]
        total = round(sum(amounts), 2)
        tx_count = len(payment_events)
        by_method = defaultdict(float)
        for event in payment_events:
            payment_method = str(event.get("payment_method") or "unknown").lower()
            by_method[payment_method] += self._safe_amount(event.get("amount"))

        return {
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "method": method,
            "transaction_count": tx_count,
            "total_amount": total,
            "average_amount": round(total / tx_count, 2) if tx_count else 0.0,
            "by_method": {key: round(value, 2) for key, value in by_method.items()},
        }

    async def search_analytics(self, date_from: date, date_to: date, top_n: int) -> dict[str, Any]:
        events = [self._normalize_event(event) for event in await self._events_between(date_from, date_to)]

        search_events = [
            event for event in events if event["event_type"].startswith("search.") or event["event_type"] == "search"
        ]

        query_counter = Counter()
        no_result_count = 0
        for event in search_events:
            query = str(event.get("query") or "").strip()
            if query:
                query_counter[query.lower()] += 1
            if event.get("results_count") == 0:
                no_result_count += 1

        return {
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "total_searches": len(search_events),
            "zero_result_searches": no_result_count,
            "top_queries": [{"query": query, "count": count} for query, count in query_counter.most_common(max(1, top_n))],
        }

    async def market_heatmap(self, date_from: date, date_to: date) -> dict[str, Any]:
        events = [self._normalize_event(event) for event in await self._events_between(date_from, date_to)]

        heat = Counter()
        for event in events:
            if not event["event_type"].startswith("market.listing"):
                continue
            city = str(event.get("city") or "unknown").strip() or "unknown"
            heat[city] += 1

        return {
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "points": [{"city": city, "score": score} for city, score in heat.most_common()],
        }

    async def kpis(self, date_from: date, date_to: date) -> dict[str, Any]:
        overview = await self.platform_overview(date_from, date_to)
        bookings = await self.booking_analytics(date_from, date_to)
        search = await self.search_analytics(date_from, date_to, top_n=10)

        total_events = int(overview.get("total_events", 0))
        total_searches = int(search.get("total_searches", 0))

        return {
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "active_users": overview["users"]["active_users"],
            "new_users": overview["users"]["new_users"],
            "booking_completion_rate": bookings["completion_rate"],
            "booking_confirmation_rate": bookings["confirmation_rate"],
            "search_share": round((total_searches / total_events) * 100, 2) if total_events else 0.0,
            "revenue_total": overview["revenue"]["total_amount"],
        }

    async def export_report(
        self,
        *,
        report_type: str,
        date_from: date,
        date_to: date,
        fmt: str,
    ) -> dict[str, Any]:
        if report_type == "overview":
            payload = await self.platform_overview(date_from, date_to)
        elif report_type == "users":
            payload = await self.user_analytics(date_from, date_to, role=None)
        elif report_type == "listings":
            payload = await self.listing_analytics(date_from, date_to, city=None)
        elif report_type == "bookings":
            payload = await self.booking_analytics(date_from, date_to)
        elif report_type == "revenue":
            payload = await self.revenue_analytics(date_from, date_to, method=None)
        elif report_type == "search":
            payload = await self.search_analytics(date_from, date_to, top_n=20)
        elif report_type == "market_heatmap":
            payload = await self.market_heatmap(date_from, date_to)
        else:
            payload = await self.kpis(date_from, date_to)

        rows = self._rows_from_payload(payload)
        export_job_id = str(uuid4())

        output: str | dict[str, Any]
        if fmt == "csv":
            output = self._to_csv(rows)
        else:
            output = payload

        return {
            "job_id": export_job_id,
            "status": "completed",
            "format": fmt,
            "report_type": report_type,
            "row_count": len(rows),
            "output": output,
        }

    async def _events_between(self, date_from: date, date_to: date) -> list[MetricEvent]:
        start = datetime.combine(date_from, time.min).replace(tzinfo=timezone.utc)
        end = datetime.combine(date_to, time.max).replace(tzinfo=timezone.utc)
        return await self._repository.list_events(date_from=start, date_to=end)

    def _normalize_event(self, event: MetricEvent) -> dict[str, Any]:
        return {
            "id": str(event.id),
            "event_type": str(event.event_type),
            "actor_id": event.actor_id,
            "actor_role": event.actor_role,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "amount": event.amount,
            "city": event.city,
            "payment_method": event.payment_method,
            "price": event.list_price,
            "query": event.search_query,
            "results_count": event.results_count,
            "created_at": event.created_at,
        }

    @staticmethod
    def _safe_amount(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _rows_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for key, value in payload.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    rows.append({"metric": f"{key}.{sub_key}", "value": sub_value})
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    for row in value:
                        normalized_row = {"metric": key}
                        normalized_row.update(row)
                        rows.append(normalized_row)
                else:
                    rows.append({"metric": key, "value": value})
            else:
                rows.append({"metric": key, "value": value})
        return rows

    @staticmethod
    def _to_csv(rows: list[dict[str, Any]]) -> str:
        if not rows:
            return ""

        keys = sorted({key for row in rows for key in row.keys()})
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
        return stream.getvalue()
