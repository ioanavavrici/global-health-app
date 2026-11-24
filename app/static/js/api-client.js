const API_ROOT = "/api";

export class ApiError extends Error {
    constructor(status, message) {
        super(message);
        this.name = "ApiError";
        this.status = status;
    }
}

async function errorDetail(response) {
    try {
        const payload = await response.json();
        if (payload && typeof payload.detail === "string") {
            return payload.detail;
        }
    } catch (_) {
        // Ignore JSON parse error on non-JSON body
    }
    return `HTTP ${response.status}`;
}

async function getJson(path, params = new URLSearchParams(), signal) {
    const query = params.toString();
    const url = query ? `${API_ROOT}${path}?${query}` : `${API_ROOT}${path}`;
    const response = await fetch(url, {
        headers: { Accept: "application/json" },
        signal,
    });
    if (!response.ok) {
        throw new ApiError(response.status, await errorDetail(response));
    }
    return response.json();
}

export function fetchRegions(signal) {
    return getJson("/regions", new URLSearchParams(), signal);
}

export function fetchCountries(region, signal) {
    const params = new URLSearchParams();
    if (region) {
        params.set("region", region);
    }
    return getJson("/countries", params, signal);
}

export function fetchIndicators(signal) {
    return getJson("/indicators", new URLSearchParams(), signal);
}

export function fetchPeriodAverages(query, signal) {
    const params = new URLSearchParams({
        first_year: String(query.firstYear),
        last_year: String(query.lastYear),
        period_years: String(query.periodYears),
    });
    if (query.sex) {
        params.set("sex", query.sex);
    }
    for (const iso3 of query.countryIso3s) {
        params.append("country", iso3);
    }
    const code = encodeURIComponent(query.indicatorCode);
    return getJson(`/indicators/${code}/period-averages`, params, signal);
}
