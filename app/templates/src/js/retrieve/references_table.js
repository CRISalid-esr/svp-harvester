import DataTable from "datatables.net-dt";
import {prettyPrintJson} from "pretty-print-json";
import {capitalizeFirstLetter} from "../common/string_utils";

class ReferencesTable {
    constructor(env, rootElement, client) {
        this.env = env;
        this.rootElement = rootElement;
        this.client = client;
        this.fetchedReferences = {};
        const noDataMessage = document.getElementById(
            "datatables-no-data-available-retrieval"
        ).value;
        this.dataTable = new DataTable("#references-table", {
            language: {
                emptyTable: noDataMessage,
            },
            paging: false,
            searching: false,
            info: false,
            columns: [
                {
                    width: "5%",
                    className: "dt-control",
                    orderable: false,
                    data: null,
                    defaultContent: "",
                },
                {width: "5%", title: "Source", data: "source"},
                {width: "10%", title: "Identifiant", data: "identifier"},
                {width: "10%", title: "Statut", data: "status"},
                {width: "70%", title: "Titre", searchable: true, data: "title"},
                {title: "Data", visible: false, data: "data"},
            ],
            columnDefs: [
                {
                    targets: 2,
                    render: function (data, type, full) {
                        return type === "display"
                            ? '<div title="' + full.identifier + '">' + data
                            : data;
                    },
                },
                {
                    targets: 3,
                    render: function (data, type, full) {
                        return type === "display"
                            ? '<div title="' + full.status + '">' + data
                            : data;
                    },
                },
                {
                    targets: 4,
                    render: function (data, type, full) {
                        return type === "display"
                            ? '<div title="' + full.title + '">' + data
                            : data;
                    },
                },
            ],
            rowId: "identifier",
        });
        this.openRows = [];
        this.addCollapseListener();
    }

    addCollapseListener() {
        this.dataTable.on("click", "td.dt-control", this.handleCollapse.bind(this));
    }

    handleCollapse(event) {
        if (event.target.classList.contains("dt-control")) {
            const tr = event.target.closest("tr");
            const row = this.dataTable.row(tr);
            const rowId = row.id();
            if (!this.openRows.includes(rowId)) {
                this.client
                    .getReferenceEvent(row.data().id)
                    .then((response) => {
                        this.fetchedReferences[row.data().id] = response.data["reference"];
                        row.data().data = this.jsonToHtml(response.data["reference"]);
                        this.updateOpenClosedRows();
                    })
                    .catch((error) => {
                        console.log(error);
                    });
                this.openRows.push(rowId);
            } else {
                const index = this.openRows.indexOf(rowId);
                this.openRows.splice(index, 1);
            }
            this.updateOpenClosedRows();
        }
    }

    jsonToHtml(json) {
        return "<pre>" + prettyPrintJson.toHtml(json) + "</pre>";
    }

    updateOpenClosedRows() {
        const self = this;
        this.dataTable.rows().every(function (rowIdx, tableLoop, rowLoop) {
            if (self.openRows.includes(this.id())) {
                const reference = this.data().data;
                this.child(reference).show();
            } else {
                this.child.hide();
            }
        });
        self.dataTable.draw();
    }

    updateTable(harvestings) {
        const data = [];
        const preloader_html =
            '<div class="spinner-border spinner-border-sm spinner-inline float-right" role="status"></div>';
        for (const harvesting of harvestings) {
            for (const referenceEvent of harvesting.reference_events) {
                const reference = referenceEvent.reference;
                const addStar = referenceEvent.enhanced ? " *" : "";
                const row = {
                    source: capitalizeFirstLetter(harvesting.harvester),
                    identifier: reference.source_identifier,
                    status: capitalizeFirstLetter(referenceEvent.type) + addStar,
                    title:
                        reference.titles && reference.titles[0]
                            ? reference.titles[0].value
                            : "No title",
                    data: this.fetchedReferences[referenceEvent.id]
                        ? this.jsonToHtml(this.fetchedReferences[referenceEvent.id])
                        : preloader_html,
                    id: referenceEvent.id,
                };
                data.push(row);
            }
            this.dataTable.clear();
            this.dataTable.rows.add(data);
            this.updateOpenClosedRows();
        }
    }
}

export default ReferencesTable;
