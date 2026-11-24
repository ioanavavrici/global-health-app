export const DEFAULT_INDICATOR = "WHOSIS_000001";
export const FALLBACK_INDICATOR = "SP.DYN.IMRT.IN";
export const DEFAULT_REGION = "Europe & Central Asia";
export const DEFAULT_COUNTRIES = ["ROU", "FRA", "DEU", "ITA", "ESP"];
export const MAX_SELECTED_COUNTRIES = 8;

export class ColorSlots {
    constructor(maxSlots = 8) {
        this._maxSlots = maxSlots;
        this._assigned = new Map();
    }

    update(selectedIso3s) {
        const active = new Set(selectedIso3s);
        for (const iso3 of this._assigned.keys()) {
            if (!active.has(iso3)) {
                this._assigned.delete(iso3);
            }
        }
        for (const iso3 of selectedIso3s) {
            if (!this._assigned.has(iso3)) {
                const used = new Set(this._assigned.values());
                for (let slot = 1; slot <= this._maxSlots; slot++) {
                    if (!used.has(slot)) {
                        this._assigned.set(iso3, slot);
                        break;
                    }
                }
            }
        }
    }

    slotOf(iso3) {
        return this._assigned.get(iso3) || 1;
    }
}

export function axisTitle(indicator) {
    if (!indicator) return "";
    return indicator.unit ? `${indicator.name} (${indicator.unit})` : indicator.name;
}

export function toTable(report) {
    return {
        headers: ["Country", ...report.periods.map((p) => p.label)],
        rows: report.series.map((s) => ({
            iso3: s.country_iso3,
            countryName: `${s.country_name} (${s.country_iso3})`,
            cells: s.averages,
        })),
    };
}

export function toChart(report, colorSlots) {
    return {
        labels: report.periods.map((p) => p.label),
        yTitle: axisTitle(report.indicator),
        lines: report.series.map((series) => ({
            label: series.country_name,
            values: series.averages,
            colorSlot: colorSlots.slotOf(series.country_iso3),
        })),
    };
}
