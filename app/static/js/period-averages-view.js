const MISSING = "?";
const numberFormat = new Intl.NumberFormat(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
});

export class PeriodAveragesView {
    constructor(handlers) {
        this.handlers = handlers;
        this.indicatorEl = document.getElementById("indicator");
        this.regionEl = document.getElementById("region");
        this.sexEl = document.getElementById("sex");
        this.periodYearsEl = document.getElementById("period-years");
        this.countryListEl = document.getElementById("country-list");
        this.countrySummaryEl = document.getElementById("country-summary");
        this.statusEl = document.getElementById("status");
        this.tableEl = document.getElementById("averages-table");
        this.chartCanvas = document.getElementById("averages-chart");
        this.chart = null;

        this.indicatorEl.addEventListener("change", () => handlers.onFilterChange());
        this.regionEl.addEventListener("change", () => handlers.onRegionChange());
        this.sexEl.addEventListener("change", () => handlers.onFilterChange());
        this.periodYearsEl.addEventListener("change", () => handlers.onFilterChange());
    }

    setIndicators(indicators, selectedCode) {
        this.indicatorEl.replaceChildren();
        for (const ind of indicators) {
            const opt = document.createElement("option");
            opt.value = ind.code;
            opt.textContent = ind.name;
            if (ind.code === selectedCode) opt.selected = true;
            this.indicatorEl.append(opt);
        }
    }

    setRegions(regions, selectedRegion) {
        this.regionEl.replaceChildren();
        const allOpt = document.createElement("option");
        allOpt.value = "";
        allOpt.textContent = "All regions";
        this.regionEl.append(allOpt);
        for (const r of regions) {
            const opt = document.createElement("option");
            opt.value = r;
            opt.textContent = r;
            if (r === selectedRegion) opt.selected = true;
            this.regionEl.append(opt);
        }
    }

    setCountries(countries, selectedSet, maxCountries) {
        this.countryListEl.replaceChildren();
        for (const c of countries) {
            const li = document.createElement("li");
            const label = document.createElement("label");
            label.className = "country-opt";
            const cb = document.createElement("input");
            cb.type = "checkbox";
            cb.value = c.iso3;
            cb.checked = selectedSet.has(c.iso3);
            if (!cb.checked && selectedSet.size >= maxCountries) {
                cb.disabled = true;
            }
            cb.addEventListener("change", () => {
                this.handlers.onCountryToggle(c.iso3, cb.checked);
            });
            const span = document.createElement("span");
            span.textContent = c.name;
            label.append(cb, span);
            li.append(label);
            this.countryListEl.append(li);
        }
        this.updateCountrySummary(selectedSet.size, maxCountries);
    }

    updateCountrySummary(count, maxCountries) {
        this.countrySummaryEl.textContent = `Countries (${count}/${maxCountries} selected)`;
    }

    showStatus(message, { isError = false } = {}) {
        this.statusEl.textContent = message;
        this.statusEl.className = isError ? "status-banner status-error" : "status-banner";
    }

    clearResults() {
        this.tableEl.replaceChildren();
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    renderTable(tableModel) {
        this.tableEl.replaceChildren();
        const thead = document.createElement("thead");
        const headRow = document.createElement("tr");
        tableModel.headers.forEach((text, idx) => {
            const th = document.createElement("th");
            if (idx > 0) th.className = "num";
            th.textContent = text;
            headRow.append(th);
        });
        thead.append(headRow);

        const tbody = document.createElement("tbody");
        for (const row of tableModel.rows) {
            const tr = document.createElement("tr");
            const nameTd = document.createElement("td");
            const strong = document.createElement("strong");
            strong.textContent = row.countryName;
            nameTd.append(strong);
            tr.append(nameTd);

            for (const val of row.cells) {
                const td = document.createElement("td");
                td.className = "num";
                td.textContent = val === null ? MISSING : numberFormat.format(val);
                tr.append(td);
            }
            tbody.append(tr);
        }
        this.tableEl.append(thead, tbody);
    }

    renderChart(chartModel) {
        const styles = getComputedStyle(document.documentElement);
        const datasets = chartModel.lines.map((line) => {
            const color = styles.getPropertyValue(`--series-${line.colorSlot}`).trim() || "#6c5ce7";
            return {
                label: line.label,
                data: line.values,
                borderColor: color,
                backgroundColor: color,
                borderWidth: 2.5,
                tension: 0.28,
                pointRadius: 4,
                pointHoverRadius: 6,
                spanGaps: false,
            };
        });

        if (this.chart) {
            this.chart.destroy();
        }

        this.chart = new Chart(this.chartCanvas, {
            type: "line",
            data: {
                labels: chartModel.labels,
                datasets,
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: {
                    legend: { position: "bottom" },
                },
                scales: {
                    y: {
                        title: { display: true, text: chartModel.yTitle },
                    },
                },
            },
        });
    }
}
