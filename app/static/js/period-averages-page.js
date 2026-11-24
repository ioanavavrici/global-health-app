import {
    fetchCountries,
    fetchIndicators,
    fetchPeriodAverages,
    fetchRegions,
} from "./api-client.js";
import {
    ColorSlots,
    DEFAULT_COUNTRIES,
    DEFAULT_INDICATOR,
    DEFAULT_REGION,
    FALLBACK_INDICATOR,
    MAX_SELECTED_COUNTRIES,
    toChart,
    toTable,
} from "./period-averages-model.js";
import { PeriodAveragesView } from "./period-averages-view.js";

class PeriodAveragesPage {
    constructor() {
        this.selectedIso3s = [...DEFAULT_COUNTRIES];
        this.allRegionCountries = [];
        this.colorSlots = new ColorSlots(MAX_SELECTED_COUNTRIES);
        this.pendingRequest = null;

        this.view = new PeriodAveragesView({
            onFilterChange: () => this.refresh(),
            onRegionChange: () => this.onRegionChange(),
            onCountryToggle: (iso3, checked) => this.onCountryToggle(iso3, checked),
        });
    }

    currentQuery() {
        return {
            indicatorCode: this.view.indicatorEl.value,
            countryIso3s: this.selectedIso3s,
            firstYear: Number(this.view.indicatorEl.dataset.firstYear || 2000),
            lastYear: Number(this.view.indicatorEl.dataset.lastYear || 2023),
            periodYears: Number(this.view.periodYearsEl.value || 5),
            sex: this.view.sexEl.value || "BTSX",
        };
    }

    async start() {
        this.view.showStatus("Loading filters...");
        try {
            const [indicators, regions] = await Promise.all([
                fetchIndicators(),
                fetchRegions(),
            ]);

            const hasDefaultInd = indicators.some((i) => i.code === DEFAULT_INDICATOR);
            const chosenInd = hasDefaultInd
                ? DEFAULT_INDICATOR
                : indicators.find((i) => i.code === FALLBACK_INDICATOR)?.code || indicators[0]?.code;
            this.view.setIndicators(indicators, chosenInd);

            const chosenRegion = regions.includes(DEFAULT_REGION) ? DEFAULT_REGION : regions[0] || "";
            this.view.setRegions(regions, chosenRegion);

            await this.loadCountriesForRegion(chosenRegion, true);
            await this.refresh();
        } catch (error) {
            this.view.showStatus(`Failed to initialize page: ${error.message}`, { isError: true });
        }
    }

    async loadCountriesForRegion(region, keepDefaults = false) {
        const countries = await fetchCountries(region);
        this.allRegionCountries = countries;
        const available = new Set(countries.map((c) => c.iso3));

        if (keepDefaults) {
            this.selectedIso3s = DEFAULT_COUNTRIES.filter((c) => available.has(c));
        } else {
            this.selectedIso3s = this.selectedIso3s.filter((c) => available.has(c));
        }
        if (this.selectedIso3s.length === 0 && countries.length > 0) {
            this.selectedIso3s = countries.slice(0, 5).map((c) => c.iso3);
        }

        this.view.setCountries(countries, new Set(this.selectedIso3s), MAX_SELECTED_COUNTRIES);
    }

    async onRegionChange() {
        try {
            await this.loadCountriesForRegion(this.view.regionEl.value, false);
            await this.refresh();
        } catch (error) {
            this.view.showStatus(`Could not load countries: ${error.message}`, { isError: true });
        }
    }

    onCountryToggle(iso3, checked) {
        if (checked) {
            if (!this.selectedIso3s.includes(iso3) && this.selectedIso3s.length < MAX_SELECTED_COUNTRIES) {
                this.selectedIso3s.push(iso3);
            }
        } else {
            this.selectedIso3s = this.selectedIso3s.filter((c) => c !== iso3);
        }
        this.view.setCountries(
            this.allRegionCountries,
            new Set(this.selectedIso3s),
            MAX_SELECTED_COUNTRIES
        );
        this.refresh();
    }

    async refresh() {
        this.pendingRequest?.abort();

        if (this.selectedIso3s.length === 0) {
            this.view.clearResults();
            this.view.showStatus("Choose at least one country.");
            return;
        }

        const controller = new AbortController();
        this.pendingRequest = controller;
        this.view.showStatus("Loading chart and table...");

        try {
            const report = await fetchPeriodAverages(this.currentQuery(), controller.signal);
            this.colorSlots.update(this.selectedIso3s);
            this.view.renderTable(toTable(report));
            this.view.renderChart(toChart(report, this.colorSlots));
            this.view.showStatus(
                `Showing ${report.indicator.name} (${report.periods.length} periods, ${report.series.length} countries).`
            );
        } catch (error) {
            if (error.name !== "AbortError") {
                this.view.clearResults();
                this.view.showStatus(`Could not load the data: ${error.message}`, { isError: true });
            }
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    new PeriodAveragesPage().start();
});
