from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx


@dataclass(frozen=True)
class DatasetResource:
    resource_id: str
    title: str
    url: str
    format: str


@dataclass(frozen=True)
class DatasetInfo:
    dataset_id: str
    last_update: str
    resources: list[DatasetResource]


class EphyDatasetClient:
    def __init__(self, dataset_api_url: str, timeout: float = 30.0) -> None:
        self._dataset_api_url = dataset_api_url
        self._timeout = timeout

    def get_dataset_info(self) -> DatasetInfo:
        with httpx.Client(timeout=self._timeout, follow_redirects=True) as client:
            response = client.get(self._dataset_api_url)
            response.raise_for_status()
            payload: Dict[str, Any] = response.json()

        resources: list[DatasetResource] = []
        for res in payload.get("resources", []):
            resources.append(
                DatasetResource(
                    resource_id=res.get("id", ""),
                    title=res.get("title", ""),
                    url=res.get("url", ""),
                    format=res.get("format", ""),
                )
            )

        return DatasetInfo(
            dataset_id=payload.get("id", ""),
            last_update=payload.get("last_update", ""),
            resources=resources,
        )

    def pick_utf8_zip(self, info: DatasetInfo) -> Optional[DatasetResource]:
        for res in info.resources:
            title_lower = res.title.lower()
            if res.format == "zip" and "utf8" in title_lower:
                return res
        for res in info.resources:
            if res.format == "zip":
                return res
        return None
