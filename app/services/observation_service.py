from dataclasses import dataclass
import math
from app.domain import FilterOptions, ObservationCriteria, ObservationListItem, Option
from app.models import Sex
from app.repositories.observation_repository import ObservationRepository

DEFAULT_PAGE_SIZE = 25


@dataclass(frozen=True)
class ObservationPage:
    """One page of observations plus counts needed by the view."""

    items: list[ObservationListItem]
    number: int
    size: int
    total_items: int

    @property
    def total_pages(self) -> int:
        return max(1, math.ceil(self.total_items / self.size))

    @property
    def has_previous(self) -> bool:
        return self.number > 1

    @property
    def has_next(self) -> bool:
        return self.number < self.total_pages


class ObservationService:
    """Business rules for browsing and filtering observations."""

    def __init__(
        self,
        repository: ObservationRepository,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> None:
        if page_size < 1:
            raise ValueError(f"page_size must be at least 1, got {page_size}")
        self._repository = repository
        self._page_size = page_size

    def get_page(
        self, criteria: ObservationCriteria, number: int
    ) -> ObservationPage:
        """Return 1-based page ``number`` of matching observations."""
        if number < 1:
            raise ValueError(f"page numbers start at 1, got {number}")
        items = self._repository.find(
            criteria,
            limit=self._page_size,
            offset=(number - 1) * self._page_size,
        )
        return ObservationPage(
            items=items,
            number=number,
            size=self._page_size,
            total_items=self._repository.count(criteria),
        )

    def get_filter_options(self) -> FilterOptions:
        return FilterOptions(
            countries=self._repository.list_countries(),
            indicators=self._repository.list_indicators(),
            regions=self._repository.list_regions(),
            sexes=[Option(value=s.value, label=s.value) for s in Sex],
        )

    def list_countries(self, region: str | None = None) -> list[Option]:
        return self._repository.list_countries(region)

    def list_indicators(self) -> list[Option]:
        return self._repository.list_indicators()

    def list_regions(self) -> list[Option]:
        return self._repository.list_regions()
