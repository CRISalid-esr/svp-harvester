import DataTable from "datatables.net-dt";
import {prettyPrintJson} from "pretty-print-json";
import * as bootstrap from "bootstrap";
import * as jsondiffpatch from "jsondiffpatch";
import * as annotatedFormatter from "jsondiffpatch/formatters/html";

const MAPPING_COLOR_STATE = {
    created: "badge-created",
    deleted: "badge-created",
    unchanged: "badge-updated",
    failed: "badge-failed",
};

const MAPPING_COLOR_EVENT = {
    created: "badge-created",
    deleted: "badge-deleted",
    updated: "badge-updated",
};

const SPINNER = `<div class='spinner-border' role='status'><span class='visually-hidden'>Chargement...</span></div>`;

class HistoryTable {
    constructor(env, rootElement, subpage, client) {
        this.env = env;
        this.rootElement = rootElement;
        this.subpage = subpage;
        this.client = client;
        const config = this.getDataTableConfig();
        this.dataTable = new DataTable("#references-table", config);
        this.addColapseListener();
    }

    getDataTableConfig() {
        const noDataMessage = document.getElementById(
            "datatables-no-data-available-history"
        ).value;
        const commonConfig = {
            language: {
                emptyTable: noDataMessage,
            },
            paging: false,
            searching: false,
            info: false,
        };

        switch (this.subpage) {
            case "collection_history":
                return {
                    ...commonConfig,
                    columns: [
                        {
                            width: "5%",
                            className: "dt-control",
                            orderable: false,
                            data: null,
                            defaultContent: "",
                        },
                        {width: "15%", title: "Date"},
                        {width: "15%", title: "Nom de l'entité"},
                        {width: "20%", title: "identifiants"},
                        {width: "15%", title: "Type d'événements"},
                        {width: "15%", title: "Sources de données"},
                        {width: "16%", title: "Type de référence"},
                        {width: "5%", title: "Nombre d'événements"},
                        {title: "id", visible: false},
                        {title: "Data", visible: false},
                    ],
                    columnDefs: [
                        {
                            targets: 1,
                            render: function (data, type, full) {
                                return type === "display"
                                    ? '<div title="' + full[1] + '">' + data
                                    : data;
                            },
                        },
                        {
                            targets: 2,
                            render: function (data, type, full) {
                                return type === "display"
                                    ? '<div title="' + full[2] + '">' + data
                                    : data;
                            },
                        },
                        {
                            targets: 3,
                            render: function (data, type, full) {
                                return type === "display"
                                    ? '<div title="' + full[3] + '">' + data
                                    : data;
                            },
                        },
                        {
                            targets: 6,
                            render: function (data, type, full) {
                                return type === "display"
                                    ? '<div title="' + full[6] + '">' + data
                                    : data;
                            },
                        },
                    ],
                };
            case "publication_history":
                return {
                    ...commonConfig,
                    columns: [
                        {
                            width: "5%",
                            className: "dt-control",
                            orderable: false,
                            data: null,
                            defaultContent: "",
                        },
                        {width: "20%", title: "Date"},
                        {width: "15%", title: "Source"},
                        {width: "30%", title: "Identifiant"},
                        {width: "15%", title: "Statut"},
                        {width: "20%", title: "Titre"},
                        {title: "id", visible: false},
                        {title: "Data", visible: false},
                    ],
                    columnDefs: [
                        {
                            targets: 1,
                            render: function (data, type, full) {
                                return type === "display"
                                    ? '<div title="' + full[1] + '">' + data
                                    : data;
                            },
                        },
                        {
                            targets: 5,
                            render: function (data, type, full) {
                                return type === "display"
                                    ? '<div title="' + full[5] + '">' + data
                                    : data;
                            },
                        },
                    ],
                };
            default:
                throw new Error(`Unsupported subpage: ${this.subpage}`);
        }
    }

    addColapseListener() {
        this.dataTable.on("click", "td.dt-control", this.handleCollapse.bind(this));
    }

    buildReferenceEventsList(events) {
        let listHtml =
            '<div class="list-group compact-list list-group-flush m-md-3 mx-5">';
        events.forEach((event) => {
            event.reference_events.forEach((refEvent) => {
                const title =
                    refEvent.reference.titles.length > 0
                        ? refEvent.reference.titles[0].value
                        : "No title available";
                const enhancedBadge = refEvent.enhanced ? "<span class='badge bg-success-subtle text-secondary ms-2'>enhanced &#9733;</span>" : "";
                listHtml += `
                <a href="#" class="list-group-item list-group-item-action" data-event-id="${refEvent.id}" data-detail-shown="false">
                    <div class="d-flex w-100 justify-content-between">
                        <h5 class="mb-1" title="${title}"><span class="badge badge-${refEvent.type} me-2 p-1">${refEvent.type}</span>${enhancedBadge}   ${title}</h5>                        
                    <span class="badge rounded-pill bg-light text-dark">${event.harvester}</span>
                    </div>
                    <p class="mb-1 text-end">${refEvent.reference.source_identifier}</p>
                </a>
            `;
            });
        });
        listHtml += "</div>";
        return listHtml;
    }

    async handleCollapse(event) {
        if (event.target.classList.contains("dt-control")) {
            const tr = event.target.closest("tr");
            const row = this.dataTable.row(tr);
            if (row.child.isShown()) {
                row.data()[this.subpage === "collection_history" ? 9 : 7] = SPINNER;
                row.child.hide();
                tr.classList.remove("shown");
            } else {
                switch (this.subpage) {
                    case "collection_history":
                        row.child(row.data()[9]).show();
                        const retrieval = await this.client.getRetrieval(row.data()[8]);
                        row.data()[9] = this.buildReferenceEventsList(
                            retrieval.data.harvestings
                        );
                        row.child(row.data()[9]).show();
                        row.child().on("click", async (event) => {
                            const link = event.target.closest("a.list-group-item");
                            if (!link) {
                                return;
                            }
                            event.preventDefault();
                            if (link.detailShown === true) {
                                link.detailShown = false;
                                link.nextSibling.remove();
                            } else {
                                link.insertAdjacentHTML("afterend", SPINNER);
                                const referenceEventId = event.target.closest("a").dataset.eventId;
                                const referenceEvent = await this.client.getReferenceEvent(
                                    referenceEventId
                                );
                                const type = referenceEvent?.data?.type;
                                const enhanced = referenceEvent?.data?.enhanced;
                                if (type === undefined) {
                                    console.log("No type found in reference event");
                                    return;
                                }
                                link.nextSibling.remove();
                                const currentReference = referenceEvent.data.reference;
                                this.sortReferenceContent(currentReference);
                                const referenceDisplay = `${prettyPrintJson.toHtml(currentReference)}`;
                                if (type === "updated" || enhanced) {
                                    const tabs = this.getDiffTabs(referenceEventId, referenceDisplay);
                                    link.detailShown = true;
                                    link.insertAdjacentHTML("afterend", tabs);
                                    let previousReferenceResponse = {data: "No previous data found"};
                                    const {harvester, source_identifier, version} = currentReference;
                                    const intVersion = parseInt(version, 10);
                                    if (intVersion >= 0) {
                                        const previousVersion = intVersion - 1;
                                        previousReferenceResponse = await this.client.getReferenceByHarversterSourceIdentifierVersion(
                                            harvester,
                                            source_identifier,
                                            previousVersion
                                        );
                                    }
                                    if (!previousReferenceResponse?.data?.titles) {
                                        console.log("No previous data found")
                                        return;
                                    }
                                    const previousReference = previousReferenceResponse.data;
                                    this.sortReferenceContent(previousReference)
                                    const previousReferenceDisplay = `${prettyPrintJson.toHtml(previousReference)}`;
                                    const delta = jsondiffpatch.diff(previousReference, currentReference);
                                    const deltaDisplay = `${annotatedFormatter.format(delta, currentReference)}`;
                                    document.getElementById(`previous-ref-${referenceEventId}`).innerHTML = `<pre>${previousReferenceDisplay}</pre>`;
                                    document.getElementById(`data-diff-${referenceEventId}`).innerHTML = `<pre>${deltaDisplay}</pre>`;
                                } else {
                                    link.insertAdjacentHTML(
                                        "afterend",
                                        "<pre class='slide-in'>" +
                                        referenceDisplay +
                                        "</pre>"
                                    );
                                    link.detailShown = true;
                                }
                            }
                        });

                        break;
                    case "publication_history":
                        row.child(row.data()[7]).show();
                        const reference = await this.client.getReference(row.data()[6]);
                        row.data()[7] =
                            "<pre>" + prettyPrintJson.toHtml(reference.data) + "</pre>";
                        row.child(row.data()[7]).show();
                        break;
                    default:
                        throw new Error(`Unsupported subpage: ${this.subpage}`);
                }
                row.draw(false);
                tr.classList.add("shown");
            }
        }
    }

    sortReferenceContent(currentReference) {
        function compareRanks(a, b) {
            if (a === null && b === null) return 0;
            if (a === null) return 1;
            if (b === null) return -1;
            return a - b;
        }

        currentReference.document_type.sort((a, b) => a.uri < b.uri ? -1 : a.uri > b.uri ? 1 : 0);
        currentReference.contributions.sort((a, b) => {
            const rankComparison = compareRanks(a.rank, b.rank);
            if (rankComparison !== 0) return rankComparison;
            const sourceA = a.contributor.source_identifier;
            const sourceB = b.contributor.source_identifier;
            return sourceA.localeCompare(sourceB);
        });
        currentReference.identifiers.sort((a, b) => a.type < b.type ? -1 : a.type > b.type ? 1 : 0);
        currentReference.contributions.forEach((contribution) => {
                contribution.affiliations.sort((a, b) => a.source_identifier < b.source_identifier ? -1 : a.source_identifier > b.source_identifier ? 1 : 0);
                // sort affiliations identifiers by type
                contribution.affiliations.forEach((affiliation) => {
                        //sort affiliations identifiers by type and value
                        affiliation.identifiers.sort((a, b) => a.type < b.type ? -1 : a.type > b.type ? 1 : a.value < b.value ? -1 : a.value > b.value ? 1 : 0);
                    }
                );
            }
        );
    }

    getDiffTabs(referenceEventId, referenceDisplay) {
        const tabs = `<div>
                            <ul class="nav nav-tabs" id="updated-data-display-switch" role="tablist"> 
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link active" id="current-ref-display-tab-${referenceEventId}" data-bs-toggle="tab" data-bs-target="#current-ref-${referenceEventId}" type="button" role="tab" aria-controls="current-ref" aria-selected="true">Version actuelle</button>
                                </li>
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link" id="current-ref-tab-${referenceEventId}" data-bs-toggle="tab" data-bs-target="#previous-ref-${referenceEventId}" type="button" role="tab" aria-controls="previous-ref" aria-selected="false">Version précédente</button>
                                </li>
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link" id="data-diff-tab-${referenceEventId}" data-bs-toggle="tab" data-bs-target="#data-diff-${referenceEventId}" type="button" role="tab" aria-controls="data-diff" aria-selected="false">Différentiel</button>
                                </li>
                            </ul>
                            <div class="tab-content" id="updated-data-display-content-${referenceEventId}">
                                <div class="tab-pane fade show active" id="current-ref-${referenceEventId}" role="tabpanel" aria-labelledby="current-ref-tab">
                                    <pre class='slide-in'>${referenceDisplay}</pre>
                                </div>
                                <div class="tab-pane fade" id="previous-ref-${referenceEventId}" role="tabpanel" aria-labelledby="previous-ref-tab">
                                    <pre>${SPINNER}</pre>
                                </div>
                                <div class="tab-pane fade" id="data-diff-${referenceEventId}" role="tabpanel" aria-labelledby="data-diff-tab">
                                    <pre>${SPINNER}</pre>
                                </div>
                            </div>
                        </div>`;
        return tabs;
    }

    updateTable(history) {
        switch (this.subpage) {
            case "collection_history":
                this.updateCollectionHistoryTable(history);
                break;
            case "publication_history":
                this.updatePublicationHistoryTable(history);
                break;
        }
        const tooltipTriggerList = document.querySelectorAll(
            '[data-bs-toggle="tooltip"]'
        );
        const tooltipList = [...tooltipTriggerList].map(
            (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl)
        );
    }

    updatePublicationHistoryTable(history) {
        const data = [];
        for (const reference of history) {
            const row = [
                "",
                reference.timestamp,
                reference.harvester,
                reference.source_identifier,
                reference.event_type,
                reference.titles,
                reference.id,
                SPINNER,
            ];
            data.push(row);
        }
        this.dataTable.clear();
        this.dataTable.rows.add(data);
        this.dataTable.draw();
    }

    updateCollectionHistoryTable(history) {
        const data = [];
        for (const retrieval of history) {
            const row = [
                "",
                retrieval.timestamp,
                retrieval.entity_name,
                formatIdentifiers(retrieval.identifier_type),
                extractUniqueActions(retrieval.harvesting_state),
                formatSourceData(retrieval.harvesting_state),
                formatDocumentType(retrieval.document_type),
                retrieval.event_count,
                retrieval.id,
                SPINNER,
            ];
            data.push(row);
        }
        this.dataTable.clear();
        this.dataTable.rows.add(data);
        this.dataTable.draw();
        const popoverTriggerList = this.rootElement.querySelectorAll(
            '[data-bs-toggle="popover"]'
        );
        const popoverList = [...popoverTriggerList].map(
            (popoverTriggerEl) => new bootstrap.Popover(popoverTriggerEl)
        );
    }
}

function formatSourceData(harvesting_state) {
    const sources = {};
    harvesting_state.forEach((harvesting) => {
        const source = harvesting[0];
        if (!sources[source]) {
            sources[source] = {
                state: harvesting[1],
                event_type: new Set().add([harvesting[2], harvesting[3]]),
                count: harvesting[3],
            };
        } else {
            sources[source].event_type.add([harvesting[2], harvesting[3]]);
            sources[source].count += harvesting[3];
        }
    });
    // For each source, return a bootstrap badge with the source name and the count of events
    return Object.entries(sources)
        .map(([source, data]) => {
            var classBadgeState;
            if (data.state === "failed") {
                classBadgeState = MAPPING_COLOR_STATE[data.state];
            } else {
                classBadgeState = MAPPING_COLOR_STATE["unchanged"];
                data.event_type.forEach((event) => {
                    if (event[0] !== "unchanged") {
                        classBadgeState = MAPPING_COLOR_STATE["created"];
                    }
                });
            }

            const eventBadges = Array.from(data.event_type)
                .map((event) => {
                    return `<span class='badge ${MAPPING_COLOR_EVENT[event[0]]}'>${
                        event[1]
                    }</span>`;
                })
                .join(" ");

            const preloader =
                data.state === "running"
                    ? `<div class="spinner-border spinner-border-sm spinner-inline float-right" role="status"></div>`
                    : "";

            return `<span class="badge badge-pill ${classBadgeState}" 
                data-bs-toggle="tooltip"
                data-bs-html="true" 
                data-bs-title="${eventBadges}">
                    ${source} ${data.count} ${preloader}
                </span>`;
        })
        .join(" ");
}

function formatIdentifiers(identifiers) {
    if (!Array.isArray(identifiers) || identifiers.length === 0) {
        return "Invalid input";
    }
    const formattedIdentifiers = identifiers.map((identifierPair) => {
        const [type, value] = identifierPair;
        return `${type}(${value})`;
    });

    return formattedIdentifiers.join(" OR ");
}

function extractUniqueActions(data) {
    if (!Array.isArray(data) || data.length === 0) {
        return "Invalid input";
    }

    const uniqueActions = new Set(data.map((item) => item[2]));

    return Array.from(uniqueActions).join(", ");
}

function formatDocumentType(documentType) {
    if (!Array.isArray(documentType) || documentType.length === 0) {
        return "Invalid input";
    }

    const filteredTypes = documentType.filter((type) => type !== null);
    const result = filteredTypes.join(", ");

    return result;
}

export default HistoryTable;
