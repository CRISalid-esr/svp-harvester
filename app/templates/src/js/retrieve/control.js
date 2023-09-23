class Control {


    constructor(env, form, rootElement, client) {
        this.env = env;
        this.form = form;
        this.rootElement = rootElement;
        this.client = client;
        this.addSubmitListener();
    }

    addSubmitListener() {
        this.rootElement.addEventListener("entity_submit", this.handleSubmit.bind(this));
    }

    handleSubmit(event) {
        console.log(event);
        const formFieldContent = this.form.getIdentifierFieldsContent()
        // Convert hash keys in array : "identifierType" to  "type" and "identifierValue" to "value"
        const identifiers = formFieldContent.map((identifier) => {
            return {
                type: identifier.identifierType,
                value: identifier.identifierValue
            }
        });

        this.client.postRetrieval({identifiers: identifiers})
            .then((response) => {
                console.log(response);
            }).catch((error) => {
            console.log(error);
        });
    }


}

export default Control;
