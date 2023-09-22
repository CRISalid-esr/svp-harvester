class Form {

    /**
     *
     * @param client {Client}
     * @param rootElement {HTMLElement}
     */
    constructor(client, rootElement) {
        this.rootElement = rootElement;
        this.client = client;
        this.addListeners();
    }

    addListeners() {
        this.rootElement.addEventListener("submit", this.handleSubmit.bind(this));
    }

    handleSubmit(event) {
        event.preventDefault();
        event.stopPropagation();
        this.client.postRetrieval({identifiers: ["test"]})
            .then((response) => {
                console.log(response);
            }).catch((error) => {
            console.log(error);
        });
    }

}

export default Form;
