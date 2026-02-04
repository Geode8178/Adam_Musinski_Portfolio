# rsp_status_specs.py
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class StatusUISpec:
    # Texts that must appear somewhere within the status cell
    must_contain: tuple[str, ...] = ()

    # CSS selectors for icons/badges that must exist in the cell
    required_icon_selectors: tuple[str, ...] = ()


STATUS_UI_SPECS: dict[str, StatusUISpec] = {
# Dismissed Requirement
    "Dismissed": StatusUISpec(
        must_contain=("Dismissed", "Dismissed"),
        required_icon_selectors=("i.bi-dash-circle-fill.text-secondary",),
    ),

    # Expired Requirement
    "Expired": StatusUISpec(
        must_contain=("Ineligible", "Expired"),
        required_icon_selectors=("i.bi-x-circle-fill.text-danger",),
    ),

    # Exported Requirement
    "Exported": StatusUISpec(
        must_contain=("Submitted", "Exported"),
        required_icon_selectors=("i.bi-dash-circle-fill.text-secondary",),
    ),

    # Incomplete Requirement
    "Incomplete Requirements": StatusUISpec(
        must_contain=("Incomplete", "Incomplete Requirements"),
        required_icon_selectors=("i.bi-exclamation.text-warning",),
    ),

    # Ineligible Requirement
    "Ineligible": StatusUISpec(
        must_contain=("Ineligible", "Ineligible"),
        required_icon_selectors=("i.bi-x-circle-fill.text-danger",),
    ),

    # Ready Requirement
    "Ready": StatusUISpec(
        must_contain=("Submitted", "Ready"),
        required_icon_selectors=("i.bi-check-circle-fill.text-success",)
    ),

    # Unassigned requirement
    "Unassigned": StatusUISpec(
        must_contain=("Incomplete", "Unassigned"),
        required_icon_selectors=("i.bi-exclamation.text-danger",),
    ),
}
