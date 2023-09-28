import ejs from "ejs";
import stringToHTML from "../utils";
import identifier_field from "./templates/identifier_field";
import add_identifier_control from "./templates/add_identifier_control";

class Form {
    constructor(env, rootElement) {
        this.env = env;
        this.rootElement = rootElement;
        this.formElement = rootElement.querySelector("#form-element");
        this.identifierFieldsContainer = this.formElement.querySelector("#identifier-fields-container");
        this.runRetrievalButton = this.formElement.querySelector("#run-retrieval-btn");
        this.renewAddIdentifierControl();
        this.addSubmitListener();
        this.updateSubmitButtonState()
        this.addIdentifierField(
            {
                "identifierType": "id_hal_i",
                "identifierValue": "10227"
            }
        )
    }

    addSubmitListener() {
        this.formElement.addEventListener("submit", this.handleSubmit.bind(this));
    }

    handleSubmit(event) {
        event.preventDefault();
        event.stopPropagation();
        const entitySubmitEvent = new CustomEvent("entity_submit", {identifiers: this.getIdentifierFieldsContent()});
        this.rootElement.dispatchEvent(entitySubmitEvent);
    }

    renewAddIdentifierControl() {
        if (this.addIdentifierControlElement) {
            this.addIdentifierControlElement.remove();
        }
        this.addIdentifierControlElement = stringToHTML(ejs.render(add_identifier_control, {identifiers: this.remainingIdentifiers()}));
        for (const eventType of ["input"]) {
            this.addIdentifierControlElement.addEventListener(eventType, this.updateAddIdentifierButton.bind(this));
        }
        const self = this;
        this.addIdentifierControlElement.addEventListener('keypress', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                self.handleAddIdentifierAction();
            }
        });
        this.identifierFieldsContainer.appendChild(this.addIdentifierControlElement);
        this.handleAddIdentifierButton();
    }

    handleAddIdentifierButton() {
        this.addIdentifierButton = this.formElement.querySelector("#add-identifier-button");
        this.addIdentifierButton.addEventListener("click", this.handleAddIdentifierAction.bind(this));
        this.updateAddIdentifierButton()
    }

    handleRemoveIdentifierButtonClick(event) {
        const identifierFieldElement = event.target.closest(".identifier-field-container");
        identifierFieldElement.remove();
        this.updateAddIdentifierButton();
        this.renewAddIdentifierControl();
        this.updateSubmitButtonState();
    }

    handleEditIdentifierButtonClick(event) {
        const identifierFieldElement = event.target.closest(".identifier-field-container");
        const editIdentifierButton = identifierFieldElement.querySelector(".btn-edit-identifier");
        editIdentifierButton.setAttribute("disabled", true);
        const inputField = identifierFieldElement.querySelector("input");
        // validate input field content on keypress
        inputField.addEventListener('keypress', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                inputField.setAttribute("disabled", true);
                editIdentifierButton.removeAttribute("disabled");
            }
        });
        inputField.removeAttribute("disabled");
        inputField.focus();
    }

    updateAddIdentifierButton = () => {
        const newIdentifierFieldContent = this.getIdentifierFieldContent(this.addIdentifierControlElement);
        if (newIdentifierFieldContent.identifierType && newIdentifierFieldContent.identifierValue) {
            this.addIdentifierButton.removeAttribute("disabled");
        } else {
            this.addIdentifierButton.setAttribute("disabled", true);
        }
    }

    getIdentifierFieldContent(newIdentifierFieldElement) {
        const identifierType = newIdentifierFieldElement.querySelector("select").value;
        const identifierValue = newIdentifierFieldElement.querySelector("input").value;
        return {identifierType: identifierType, identifierValue: identifierValue};
    }

    handleAddIdentifierAction() {
        this.addIdentifierField(this.getIdentifierFieldContent(this.addIdentifierControlElement))
    }

    addIdentifierField(content) {
        content = {...content, identifierLabel: this.env.IDENTIFIERS[content.identifierType]};
        this.identifierFieldElement = stringToHTML(ejs.render(identifier_field, content));
        this.identifierFieldsContainer.insertBefore(this.identifierFieldElement, this.addIdentifierControlElement);
        const removeIdentifierButton = this.identifierFieldElement.querySelector(".btn-remove-identifier");
        removeIdentifierButton.addEventListener("click", this.handleRemoveIdentifierButtonClick.bind(this));
        const editIdentifierButton = this.identifierFieldElement.querySelector(".btn-edit-identifier");
        editIdentifierButton.addEventListener("click", this.handleEditIdentifierButtonClick.bind(this));
        this.renewAddIdentifierControl();
        this.updateSubmitButtonState();
    }

    getIdentifierFieldsContent() {
        const identifierFieldsContent = [];
        for (const identifierFieldElement of this.formElement.querySelectorAll(".identifier-field-container")) {
            identifierFieldsContent.push(this.getIdentifierFieldContent(identifierFieldElement));
        }
        return identifierFieldsContent;
    }

    remainingIdentifiers() {
        const remainingIdentifiers = {};
        for (const identifier of Object.entries(this.env.IDENTIFIERS)) {
            if (!this.getIdentifierFieldsContent().find((identifierFieldContent) => identifierFieldContent.identifierType === identifier[0])) {
                remainingIdentifiers[identifier[0]] = identifier[1];
            }
        }
        return remainingIdentifiers;
    }

    updateSubmitButtonState() {
        if (this.getIdentifierFieldsContent().length > 0) {
            this.runRetrievalButton.removeAttribute("disabled");
        } else {
            this.runRetrievalButton.setAttribute("disabled", true);
        }
    }
}

export default Form;
