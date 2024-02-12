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
                {"width": "5%", "title": "Source"},
                {"width": "10%", "title": "Identifiant"},
                {"width": "10%", "title": "Statut"},
                {"width": "70%", "title": "Titre", "searchable": true},
                {"title": "Data", "visible": false}
            ]
        });
        this.addCollapseListener();

    }

    addCollapseListener() {
        this.dataTable.on("click", 'td.dt-control', this.handleCollapse.bind(this));
    }

    handleCollapse(event) {
        console.log(event);
        if (event.target.classList.contains("dt-control")) {
            const tr = event.target.closest("tr");
            const row = this.dataTable.row(tr);
            if (row.child.isShown()) {
                row.child.hide();
                tr.classList.remove('shown');
            } else {
                const reference = row.data()[5];
                row.child(reference).show();
                tr.classList.add('shown');
            }
        }
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
                data.push(row);
            }
            this.dataTable.clear();
            this.dataTable.rows.add(data);
            this.dataTable.draw();
        }

    }
}

export default ReferencesTable;
