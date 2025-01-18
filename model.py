from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Set


class OutOfStock(Exception):
    """Raised when an operation on inventory fails."""


def allocate_order(line: OrderLine, available_batches: List[Batch]) -> str:
    for batch in sorted(available_batches):
        if batch.can_allocate(line):
            batch.allocate(line)
            return batch.reference
    raise OutOfStock(f"Unable to allocate SKU {line.sku}: out of stock")


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

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        self._allocations.discard(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(order.quantity for order in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._initial_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.quantity
