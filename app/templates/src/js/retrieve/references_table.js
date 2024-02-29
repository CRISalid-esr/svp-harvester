import DataTable from 'datatables.net-dt';
import {prettyPrintJson} from 'pretty-print-json';
import {capitalizeFirstLetter} from "../common/string_utils";


class ReferencesTable {
    constructor(env, rootElement) {
        this.env = env;
        this.rootElement = rootElement;
        this.dataTable = new DataTable("#references-table", {
            "paging": false,
            "searching": false,
            "info": false,
            "columns": [
                {
                    width: "5%",
                    className: 'dt-control',
                    orderable: false,
                    data: null,
                    defaultContent: ''
                },
                {"width": "5%", "title": "Source", data: "source"},
                {"width": "10%", "title": "Identifiant", data: "identifier"},
                {"width": "10%", "title": "Statut", data: "status"},
                {"width": "70%", "title": "Titre", "searchable": true, data: "title"},
                {"title": "Data", "visible": false, data: "data"}
            ],
            rowId: 'identifier'
        });
        this.openRows = []
        this.addCollapseListener();

    }

    addCollapseListener() {
        this.dataTable.on("click", 'td.dt-control', this.handleCollapse.bind(this));
    }

    handleCollapse(event) {
        if (event.target.classList.contains("dt-control")) {
            const tr = event.target.closest("tr");
            const rowId = this.dataTable.row(tr).id();
            if (!this.openRows.includes(rowId)) {
                this.openRows.push(rowId);
            } else {
                const index = this.openRows.indexOf(rowId);
                this.openRows.splice(index, 1);
            }
            this.updateOpenClosedRows();
        }
    }

    updateOpenClosedRows() {
        const self = this;
        this.dataTable.rows().every(function (rowIdx, tableLoop, rowLoop) {
            if (self.openRows.includes(this.id())) {
                const reference = this.data()['data'];
                this.child(reference).show();
            } else {
                this.child.hide()
            }
        })
        self.dataTable.draw();
    }

    updateTable(harvestings) {
        const data = [];
        for (const harvesting of harvestings) {
            for (const referenceEvent of harvesting.reference_events) {
                const reference = referenceEvent.reference;
                const row = [
                    "",
                    capitalizeFirstLetter(harvesting.harvester),
                    reference.source_identifier,
                    capitalizeFirstLetter(referenceEvent.type),
                    reference.titles && reference.titles[0] ? reference.titles[0].value : "No title available",
                    "<pre>" + prettyPrintJson.toHtml(reference) + "</pre>"
                ];
                const row = {
                    "source": capitalizeFirstLetter(harvesting.harvester),
                    "identifier": reference.source_identifier,
                    "status": capitalizeFirstLetter(referenceEvent.type),
                    "title": reference.titles && reference.titles[0] ? reference.titles[0].value : "No title",
                    "data": "<pre>" + prettyPrintJson.toHtml(reference) + "</pre>"
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
