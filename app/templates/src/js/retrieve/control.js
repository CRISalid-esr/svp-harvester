class Control {
    constructor(
        env,
        form,
        harvestingDashboard,
        referencesTable,
        rootElement,
        client
    ) {
        this.env = env;
        this.form = form;
        this.harvestingDashboard = harvestingDashboard;
        this.referencesTable = referencesTable;
        this.rootElement = rootElement;
        this.client = client;
        this.retrievalUrl = null;
        this.addSubmitListener();
        this.addCancelListener();
        this.timeoutID = null;
        this.cancelRetrieval = false;
    }

    addSubmitListener() {
        this.rootElement.addEventListener(
            "entity_submit",
            this.handleSubmit.bind(this)
        );
    }

    addCancelListener() {
        this.rootElement.addEventListener(
            "entity_cancel",
            this.cancelRetrieval.bind(this)
        );
    }

    handleSubmit(event) {
        const formIdentifiers = event.detail.identifiers;
        const formName = event.detail.name;
        const eventTypes = event.detail.eventTypes;
        const identifiersSafeMode = event.detail.identifiersSafeMode;
        const fetchEnhancements = event.detail.fetchEnhancements;
        const harvesters = event.detail.harvesters;
        // Convert hash keys in array : "identifierType" to  "type" and "identifierValue" to "value"
        // remove empty values
        const identifiers = formIdentifiers
            .filter(
                (identifier) => identifier.identifierType && identifier.identifierValue
            )
            .map((identifier) => {
                return {
                    type: identifier.identifierType,
                    value: identifier.identifierValue,
                };
            });
        const identifiersToNullify = formIdentifiers
            .filter((identifier) => !identifier.identifierValue)
            .map((identifier) => {
                return identifier.identifierType;
            });
        this.client
            .postRetrieval({
                person: {identifiers: identifiers, name: formName},
                nullify: identifiersToNullify,
                events: eventTypes,
                identifiers_safe_mode: identifiersSafeMode,
                fetch_enhancements: fetchEnhancements,
                harvesters: harvesters,
            })
            .then((response) => {
                this.retrievalUrl = response.data.retrieval_url;
                this.pollHarvestingState();
            })
            .catch((error) => {
                console.log(error);
            });
    }

    pollHarvestingState() {
        this.client
            .getHarvestingState(this.retrievalUrl)
            .then((response) => {
                const retrieval = response.data;
                this.harvestingDashboard.updateWidgets(retrieval.harvestings);
                // with optional chaining
                if (
                    retrieval.entity?.identifiers?.length > 0 ||
                    retrieval.entity.name.length > 0
                ) {
                    this.harvestingDashboard.updateEntityCard(retrieval.entity);
                }
                this.referencesTable.updateTable(retrieval.harvestings);
                if (this.cancelRetrieval) {
                    retrieval.harvestings.forEach((harvesting) => {
                        harvesting.state = "canceled";
                    });
                    this.harvestingDashboard.updateWidgets(retrieval.harvestings);
                    this.cancelRetrieval = false;
                    return;
                }
                if (!this.finished(retrieval)) {
                    this.timeoutID = setTimeout(this.pollHarvestingState.bind(this), 500);
                } else {
                    this.form.retrieveFinished();
                }
            })
            .catch((error) => {
                console.log(error);
                this.form.retrieveFinished();
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

    cancelRetrieval() {
        this.cancelRetrieval = true;
        this.form.retrieveFinished();
    }
}

export default Control;
