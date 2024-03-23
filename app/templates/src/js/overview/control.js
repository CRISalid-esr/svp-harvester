// TODO: Complete Control for History page. Refer to Control from retrieve as base
class Control {
    constructor(env, rootElement, client, dashboard) {
        this.env = env;
        this.rootElement = rootElement;
        this.client = client;
        this.dashboard = dashboard;
        this.loadData();
    }

    loadData() {
        this.client.getReferencesByHarvesterMetrics().then((response) => {
            this.dashboard.updateRetrievalByHarvester(response.data);
        }).catch((error) => {
            console.log(error);
        });
        this.client.getReferenceEventsByDayAndTypeMetrics().then((response) => {
            this.dashboard.updateReferenceEventsByDayAndType(response.data);
        }).catch((error) => {
            console.log(error);
        });
    }
}

export default Control