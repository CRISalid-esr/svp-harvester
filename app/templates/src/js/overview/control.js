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
            const fakeRetrievalByHarvesterData = response.data
            this.dashboard.updateRetrievalByHarvester(fakeRetrievalByHarvesterData);
        }).catch((error) => {
            console.log(error);
        });
    }
}

export default Control