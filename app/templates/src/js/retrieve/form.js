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
        this.renewAddIdentifierControl();
        this.addSubmitListener();
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
        this.identifierFieldsContainer.appendChild(this.addIdentifierControlElement);
        this.handleAddIdentifierButton();
    }

    handleAddIdentifierButton() {
        this.addIdentifierButton = this.formElement.querySelector("#add-identifier-button");
        this.addIdentifierButton.addEventListener("click", this.handleAddIdentifierButtonClick.bind(this));
        this.updateAddIdentifierButton()
    }

    handleRemoveIdentifierButtonClick(event) {
        const identifierFieldElement = event.target.closest(".identifier-field-container");
        identifierFieldElement.remove();
        this.updateAddIdentifierButton();
        this.renewAddIdentifierControl();
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

    handleAddIdentifierButtonClick() {
        this.addIdentifierField(this.getIdentifierFieldContent(this.addIdentifierControlElement))
    }

    addIdentifierField(content) {
        console.log(content)
        content = {...content, identifierLabel: this.env.IDENTIFIERS[content.identifierType]};
        this.identifierFieldElement = stringToHTML(ejs.render(identifier_field, content));
        this.identifierFieldsContainer.insertBefore(this.identifierFieldElement, this.addIdentifierControlElement);
        const removeIdentifierButton = this.identifierFieldElement.querySelector(".btn-remove-identifier");
        removeIdentifierButton.addEventListener("click", this.handleRemoveIdentifierButtonClick.bind(this));
        this.renewAddIdentifierControl();
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
}

export default Form;
