class Control {


    constructor(env, form, harvestingDashboard, referencesTable, rootElement, client) {
        this.env = env;
        this.form = form;
        this.harvestingDashboard = harvestingDashboard;
        this.referencesTable = referencesTable;
        this.rootElement = rootElement;
        this.client = client;
        this.retrievalUrl = null;
        this.addSubmitListener();
    }

    addSubmitListener() {
        this.rootElement.addEventListener("entity_submit", this.handleSubmit.bind(this));
    }

    handleSubmit(event) {
        console.log(event);
        const formFieldContent = this.form.getIdentifierFieldsContent(true)
        // Convert hash keys in array : "identifierType" to  "type" and "identifierValue" to "value"
        const identifiers = formFieldContent.map((identifier) => {
            return {
                type: identifier.identifierType,
                value: identifier.identifierValue
            }
        });
        this.client.postRetrieval({identifiers: identifiers})
            .then((response) => {
                this.retrievalUrl = response.data.retrieval_url;
                this.pollHarvestingState();
            }).catch((error) => {
            console.log(error);
        });
    }

    pollHarvestingState() {
        this.client.getHarvestingState(this.retrievalUrl)
            .then((response) => {
                const retrieval = response.data
                this.harvestingDashboard.updateWidgets(retrieval.harvestings);
                this.referencesTable.updateTable(retrieval.harvestings);

                if (!this.finished(retrieval)) {
                    setTimeout(this.pollHarvestingState.bind(this), 500);
                }
            }).catch((error) => {
            console.log(error);
        });
    }

    finished(retrieval) {
        let completed = true;
        for (const harvesting of retrieval.harvestings) {
            if (["completed", "failed"].indexOf(harvesting.state) === -1) {
                completed = false;
            }
        }
        return completed;
    }


}

export default Control;
