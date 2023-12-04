import DataTable from 'datatables.net-dt';

// TODO: Complete HistoryTable, check references_table as base
class HistoryTable{
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
                {"width": "15%", "title": "Date"},
                {"width": "15%", "title": "Nom de l'entité"},
                {"width": "20%", "title": "identifiants"},
                {"width": "15%", "title": "Type d'événements"},
                {"width": "15%", "title": "Sources de données"},
                {"width": "16%", "title": "Type de référence"},
                {"width": "5%", "title": "Nombre d'événements"},
                {"title": "Data", "visible": false}
            ]
        })

    }
}

export default HistoryTable