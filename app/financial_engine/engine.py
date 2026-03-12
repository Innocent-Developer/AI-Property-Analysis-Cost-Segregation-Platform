from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, List


Number = float | int | Decimal


@dataclass
class AssetInput:
    name: str
    quantity: Number
    unit_replacement_cost: Number


@dataclass
class AssetFinancialBreakdown:
    name: str
    quantity: Decimal
    unit_replacement_cost: Decimal
    replacement_cost: Decimal
    allocation_factor: Decimal
    final_asset_value: Decimal


def _to_decimal(value: Number) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def compute_financial_breakdown(
    assets: Iterable[AssetInput],
    improvement_basis: Number,
) -> List[AssetFinancialBreakdown]:
    """Compute financial breakdown per asset.

    Formulas:
        replacement_cost = unit_cost * quantity
        allocation_factor = improvement_basis / total_replacement_cost
        final_asset_value = replacement_cost * allocation_factor
    """
    inputs = list(assets)
    if not inputs:
        return []

    improvement_basis_dec = _to_decimal(improvement_basis)

    replacement_costs: list[Decimal] = []
    for asset in inputs:
        qty = _to_decimal(asset.quantity)
        unit_cost = _to_decimal(asset.unit_replacement_cost)
        replacement_costs.append(qty * unit_cost)

    total_replacement_cost = sum(replacement_costs)
    if total_replacement_cost == 0:
        # Avoid division by zero; allocate zero to all assets
        allocation_factor = Decimal("0")
    else:
        allocation_factor = improvement_basis_dec / total_replacement_cost

    breakdowns: list[AssetFinancialBreakdown] = []
    for asset, replacement_cost in zip(inputs, replacement_costs):
        qty = _to_decimal(asset.quantity)
        unit_cost = _to_decimal(asset.unit_replacement_cost)
        final_value = replacement_cost * allocation_factor

        breakdowns.append(
            AssetFinancialBreakdown(
                name=asset.name,
                quantity=qty,
                unit_replacement_cost=unit_cost,
                replacement_cost=replacement_cost,
                allocation_factor=allocation_factor,
                final_asset_value=final_value,
            )
        )

    return breakdowns

