import DataTable from 'datatables.net-dt';
import { prettyPrintJson } from 'pretty-print-json';
import * as bootstrap from 'bootstrap'

const MAPPING_COLOR_STATE = {
    "created": "badge-created",
    "deleted": "badge-created",
    "unchanged": "badge-updated",
    "failed": "badge-failed"
}

const MAPPING_COLOR_EVENT = {
    "created": "badge-created",
    "deleted": "badge-deleted",
    "updated": "badge-updated",
}

const SPINNER = `<div class='spinner-border' role='status'><span class='visually-hidden'>Loading...</span></div>`;

class HistoryTable {
    constructor(env, rootElement, subpage, client) {
        this.env = env;
        this.rootElement = rootElement;
        this.subpage = subpage
        this.client = client
        const config = this.getDataTableConfig();
        this.dataTable = new DataTable("#references-table", config);
        this.addColapseListener();
    }

    getDataTableConfig() {
        const commonConfig = {
            "paging": false,
            "searching": false,
            "info": false,
        };

        switch (this.subpage) {
            case "collection_history":
                return {
                    ...commonConfig,
                    "columns": [
                        {
                            width: "5%",
                            className: 'dt-control',
                            orderable: false,
                            data: null,
                            defaultContent: ''
                        },
                        { "width": "15%", "title": "Date" },
                        { "width": "15%", "title": "Nom de l'entité" },
                        { "width": "20%", "title": "identifiants" },
                        { "width": "15%", "title": "Type d'événements" },
                        { "width": "15%", "title": "Sources de données" },
                        { "width": "16%", "title": "Type de référence" },
                        { "width": "5%", "title": "Nombre d'événements" },
                        { "title": "id", "visible": false },
                        { "title": "Data", "visible": false }
                    ]
                };
            case "publication_history":
                return {
                    ...commonConfig,
                    "columns": [
                        {
                            width: "5%",
                            className: 'dt-control',
                            orderable: false,
                            data: null,
                            defaultContent: ''
                        },
                        { "width": "20%", "title": "Date" },
                        { "width": "15%", "title": "Source" },
                        { "width": "30%", "title": "Identifiant" },
                        { "width": "15%", "title": "Statut" },
                        { "width": "20%", "title": "Titre" },
                        { "title": "id", "visible": false },
                        { "title": "Data", "visible": false }
                    ]
                };
            default:
                throw new Error(`Unsupported subpage: ${this.subpage}`);
        }
    }

    addColapseListener() {
        this.dataTable.on("click", 'td.dt-control', this.handleCollapse.bind(this));
    }

    async handleCollapse(event) {
        if (event.target.classList.contains("dt-control")) {
            const tr = event.target.closest("tr");
            const row = this.dataTable.row(tr);
            if (row.child.isShown()) {
                row.data()[(this.subpage === "collection_history") ? 9 : 7] = SPINNER;
                row.child.hide();
                tr.classList.remove('shown');
            } else {
                switch (this.subpage) {
                    case "collection_history":
                        row.child(row.data()[9]).show();
                        const retrieval = await this.client.getRetrieval(row.data()[8]);
                        row.data()[9] = "<pre>" + prettyPrintJson.toHtml(retrieval.data) + "</pre>";
                        row.child(row.data()[9]).show();
                        break;
                    case "publication_history":
                        row.child(row.data()[7]).show();
                        const reference = await this.client.getReference(row.data()[6]);
                        row.data()[7] = "<pre>" + prettyPrintJson.toHtml(reference.data) + "</pre>";
                        row.child(row.data()[7]).show();
                        break;
                    default:
                        throw new Error(`Unsupported subpage: ${this.subpage}`);
                }
                row.draw(false);
                tr.classList.add('shown');
            }
        }

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
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

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
                SPINNER
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
                SPINNER
            ];
            data.push(row);
        }
        this.dataTable.clear();
        this.dataTable.rows.add(data);
        this.dataTable.draw();
        const popoverTriggerList = this.rootElement.querySelectorAll('[data-bs-toggle="popover"]')
        const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))
    }

}

function formatSourceData(harvesting_state) {
    const sources = {};
    harvesting_state.forEach(harvesting => {
        const source = harvesting[0];
        if (!sources[source]) {
            sources[source] = {
                state: harvesting[1],
                event_type: new Set().add([harvesting[2], harvesting[3]]),
                count: harvesting[3]
            }
        } else {
            sources[source].event_type.add([harvesting[2], harvesting[3]]);
            sources[source].count += harvesting[3];
        }
    });
    // For each source, return a bootstrap badge with the source name and the count of events
    return Object.entries(sources).map(([source, data]) => {
        var classBadgeState;
        if (data.state === "failed") {
            classBadgeState = MAPPING_COLOR_STATE[data.state];
        } else {
            classBadgeState = MAPPING_COLOR_STATE["unchanged"];
            data.event_type.forEach(event => {
                if (event[0] !== "unchanged") {
                    classBadgeState = MAPPING_COLOR_STATE["created"];
                }
            });
        }

        const eventBadges = Array.from(data.event_type).map(event => {
            return `<span class='badge ${MAPPING_COLOR_EVENT[event[0]]}'>${event[1]}</span>`;
        }).join(' ');

        const preloader = data.state === "running" ? `<div class="spinner-border spinner-border-sm spinner-inline float-right" role="status"></div>` : '';

        return `<span class="badge badge-pill ${classBadgeState}" 
                data-bs-toggle="tooltip"
                data-bs-html="true" 
                data-bs-title="${eventBadges}">
                    ${source} ${data.count} ${preloader}
                </span>`;

    }).join(' ');
}

function formatIdentifiers(identifiers) {

    if (!Array.isArray(identifiers) || identifiers.length === 0) {
        return "Invalid input";
    }
    const formattedIdentifiers = identifiers.map(identifierPair => {
        const [type, value] = identifierPair;
        return `${type}(${value})`;
    });

    return formattedIdentifiers.join(' OR ');
}

function extractUniqueActions(data) {
    if (!Array.isArray(data) || data.length === 0) {
        return "Invalid input";
    }

    const uniqueActions = new Set(data.map(item => item[2]));

    return Array.from(uniqueActions).join(', ');
}

function formatDocumentType(documentType) {
    if (!Array.isArray(documentType) || documentType.length === 0) {
        return "Invalid input";
    }

    const filteredTypes = documentType.filter(type => type !== null);
    const result = filteredTypes.join(', ');

    return result;
}

export default HistoryTable