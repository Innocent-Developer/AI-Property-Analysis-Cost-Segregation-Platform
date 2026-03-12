from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd

from app.financial_engine.engine import AssetFinancialBreakdown
from app.rules_engine.rules_engine import AssetClassification


def _ensure_reports_dir() -> Path:
    project_root = Path(__file__).resolve().parents[2]
    reports_dir = project_root / "storage" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir


def _to_decimal_str(value: Decimal | float | int | None) -> Optional[Decimal]:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def generate_excel_report(
    property_info: dict,
    asset_classifications: Iterable[AssetClassification],
    financial_breakdown: Iterable[AssetFinancialBreakdown],
    tax_rate: float | Decimal | None = None,
) -> Path:
    """Generate an Excel cost segregation report with multiple sections.

    Sections:
      - Property Summary
      - Detected Assets
      - Replacement Cost Table
      - Allocation Table
      - Depreciation Schedule
      - Tax Savings
    """
    reports_dir = _ensure_reports_dir()
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    property_id = property_info.get("id") or "unknown"
    filename = f"property_{property_id}_{timestamp}.xlsx"
    file_path = reports_dir / filename

    # Property Summary
    property_df = pd.DataFrame(
        [
            {
                "Property ID": property_info.get("id"),
                "Address": property_info.get("address"),
                "Type": property_info.get("property_type"),
                "Improvement Basis": property_info.get("improvement_basis"),
                "Created At": property_info.get("created_at"),
            }
        ]
    )

    # Detected Assets (classifier output)
    assets_df = pd.DataFrame(
        [
            {
                "Label": ac.label,
                "Normalized Label": ac.normalized_label,
                "Category": ac.category,
                "Asset Life (years)": ac.asset_life_years,
                "Description": ac.description,
                "Detection Confidence": ac.confidence,
            }
            for ac in asset_classifications
        ]
    )

    # Replacement Cost & Allocation Table from financial engine
    financial_df = pd.DataFrame(
        [
            {
                "Asset Name": fb.name,
                "Quantity": fb.quantity,
                "Unit Replacement Cost": fb.unit_replacement_cost,
                "Replacement Cost": fb.replacement_cost,
                "Allocation Factor": fb.allocation_factor,
                "Final Asset Value": fb.final_asset_value,
            }
            for fb in financial_breakdown
        ]
    )

    # Depreciation Schedule (simplified straight-line over asset life)
    depreciation_rows: List[dict] = []
    for ac in asset_classifications:
        matching_fb = next((fb for fb in financial_breakdown if fb.name == ac.normalized_label), None)
        if not matching_fb:
            continue

        asset_value = _to_decimal_str(matching_fb.final_asset_value) or Decimal("0")
        life_years = Decimal(str(ac.asset_life_years or 1))
        annual_depr = asset_value / life_years if life_years > 0 else Decimal("0")

        depreciation_rows.append(
            {
                "Asset": ac.normalized_label,
                "Category": ac.category,
                "Asset Life (years)": ac.asset_life_years,
                "Allocated Basis": asset_value,
                "Annual Depreciation": annual_depr,
            }
        )

    depreciation_df = pd.DataFrame(depreciation_rows)

    # Tax Savings (simple: annual depreciation * tax_rate)
    tax_df = pd.DataFrame()
    if tax_rate is not None and not depreciation_df.empty:
        tax_rate_dec = _to_decimal_str(tax_rate) or Decimal("0")
        tax_rows: List[dict] = []
        for _, row in depreciation_df.iterrows():
            annual_depr = _to_decimal_str(row["Annual Depreciation"]) or Decimal("0")
            annual_tax_savings = annual_depr * tax_rate_dec
            tax_rows.append(
                {
                    "Asset": row["Asset"],
                    "Annual Depreciation": annual_depr,
                    "Tax Rate": tax_rate_dec,
                    "Estimated Annual Tax Savings": annual_tax_savings,
                }
            )
        tax_df = pd.DataFrame(tax_rows)

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        property_df.to_excel(writer, sheet_name="Property Summary", index=False)
        assets_df.to_excel(writer, sheet_name="Detected Assets", index=False)
        financial_df.to_excel(writer, sheet_name="Replacement & Allocation", index=False)
        depreciation_df.to_excel(writer, sheet_name="Depreciation Schedule", index=False)
        if not tax_df.empty:
            tax_df.to_excel(writer, sheet_name="Tax Savings", index=False)

    return file_path

