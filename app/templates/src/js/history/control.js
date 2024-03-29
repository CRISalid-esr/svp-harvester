// TODO: Complete Control for History page. Refer to Control from retrieve as base
class Control {
    constructor(env, form, historyTable, rootElement, subPage, client) {
        this.env = env;
        this.form = form;
        this.historyTable = historyTable;
        this.rootElement = rootElement;
        this.subPage = subPage
        this.client = client
        this.addSubmitListener();
        this.addPageLoadedListener();
    }

    addPageLoadedListener() {
        // We send a default request to the server to get the latest data in the day
        window.addEventListener("load", (event) => {
            this.handleSubmit({
                detail: {
                    identifiers: [],
                    name: "",
                    eventTypes: ['created', 'updated', 'deleted', 'unchanged'],
                    harvesters: ['hal', 'idref', 'openalex', 'scanr', 'scopus'],
                    dateRange: [new Date().toISOString().split('T')[0], undefined],
                    textSearch: undefined
                }
            });
        })
    }

    addSubmitListener() {
        this.rootElement.addEventListener("entity_submit", this.handleSubmit.bind(this));
    }

    handleSubmit(event) {
        this.form.spinnerOn()
        const formIdentifiers = event.detail.identifiers;
        const formName = event.detail.name === "" ? null : event.detail.name;
        const eventTypes = event.detail.eventTypes;
        const harvesters = event.detail.harvesters;
        const dateRange = event.detail.dateRange;
        const identifiers = {}
        formIdentifiers.forEach(identifier => {
            identifiers[identifier.identifierType] = identifier.identifierValue

        })

        let params = {
            ...identifiers,
            name: formName,
            events: eventTypes,
            harvester: harvesters,
            date_start: dateRange[0],
            date_end: dateRange[1],
        }
        switch (this.subPage) {
            case "collection_history":
                this.client.getHistoryRetrieval(params).then((response) => {
                    const retrieval = response.data
                    this.historyTable.updateTable(retrieval);
                    this.form.spinnerOff()
                }).catch((error) => {
                    console.log(error);
                });
                break;
            case "publication_history":
                params = {
                    ...params,
                    text_search: event.detail.textSearch
                }
                this.client.getHistoryPublication(params).then((response) => {
                    const retrieval = response.data
                    this.historyTable.updateTable(retrieval);
                    this.form.spinnerOff()
                }).catch((error) => {
                    console.log(error);
                });
                break;
            default:
                throw new Error(`Unsupported subpage: ${this.subPage}`);

        }
    }

}

export default Control