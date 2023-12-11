import DataTable from 'datatables.net-dt';

// TODO: Complete HistoryTable, check references_table as base
class HistoryTable{
    constructor(env, rootElement, subpage) {
        this.env = env;
        this.rootElement = rootElement;
        this.subpage = subpage
        const config = this.getDataTableConfig();
        this.dataTable = new DataTable("#references-table", config);
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
                        {"width": "15%", "title": "Date"},
                        {"width": "15%", "title": "Nom de l'entité"},
                        {"width": "20%", "title": "identifiants"},
                        {"width": "15%", "title": "Type d'événements"},
                        {"width": "15%", "title": "Sources de données"},
                        {"width": "16%", "title": "Type de référence"},
                        {"width": "5%", "title": "Nombre d'événements"},
                        {"title": "Data", "visible": false}
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
                        {"width": "20%", "title": "Date"},
                        {"width": "15%", "title": "Source"},
                        {"width": "30%", "title": "identifiant"},
                        {"width": "15%", "title": "Statut"},
                        {"width": "20%", "title": "Titre"},
                        {"title": "Data", "visible": false}
                    ]
                };
            default:
                throw new Error(`Unsupported subpage: ${this.subpage}`);
        }
    }
}

export default HistoryTable