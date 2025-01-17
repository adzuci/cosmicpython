from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Set


class OutOfStock(Exception):
    """Raised when an operation on inventory fails."""


def allocate_order(order_line: OrderLine, available_batches: List[Batch]) -> str:
    for batch in sorted(available_batches):
        if batch.can_allocate(order_line):
            batch.allocate(order_line)
            return batch.reference
    raise OutOfStock(f"Unable to allocate SKU {order_line.sku}: out of stock")


@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    quantity: int


class Batch:
    def __init__(self, reference: str, sku: str, quantity: int, eta: Optional[date]):
        self.reference = reference
        self.sku = sku
        self.eta = eta
        self._initial_quantity = quantity
        self._allocations: Set[OrderLine] = set()

    def __repr__(self):
        return f"Batch(reference={self.reference}, sku={self.sku})"

    def __hash__(self):
        return hash(self.reference)

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return self.reference == other.reference

    def __lt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta < other.eta

    def allocate(self, order_line: OrderLine):
        if self.can_allocate(order_line):
            self._allocations.add(order_line)

    def deallocate(self, order_line: OrderLine):
        self._allocations.discard(order_line)

    @property
    def allocated_quantity(self) -> int:
        return sum(order.quantity for order in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._initial_quantity - self.allocated_quantity

    def can_allocate(self, order_line: OrderLine) -> bool:
        return self.sku
