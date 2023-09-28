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
        this.updateSubmitButtonState();
    }

    addSubmitListener() {
        this.formElement.addEventListener("submit", this.handleSubmit.bind(this));
    }

    handleSubmit(event) {
        event.preventDefault();
        event.stopPropagation();
        const entitySubmitEvent = new CustomEvent("entity_submit", {identifiers: this.getIdentifierFieldsContent(true)});
        this.rootElement.dispatchEvent(entitySubmitEvent);
    }

    renewAddIdentifierControl() {
        if (this.addIdentifierControlElement) {
            this.addIdentifierControlElement.remove();
        }
        this.addIdentifierControlElement = stringToHTML(ejs.render(add_identifier_control, {identifiers: this.remainingIdentifiers()}));
        this.identifierFieldsContainer.appendChild(this.addIdentifierControlElement);
        this.addIdentifierButton = this.formElement.querySelector("#add-identifier-control-button");
        this.addIdentifierInputField = this.formElement.querySelector("#add-identifier-control-input");
        this.addIdentifierSelectField = this.formElement.querySelector("#add-identifier-control-select");
        for (const eventType of ["input"]) {
            this.addIdentifierControlElement.addEventListener(eventType, this.updateAddIdentifierControlState.bind(this));
        }
        const self = this;
        this.addIdentifierControlElement.addEventListener('keypress', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                self.handleAddIdentifierAction();
            }
        });
        this.addIdentifierButton.addEventListener("click", this.handleAddIdentifierAction.bind(this));
        this.updateAddIdentifierControlState()
    }

    handleRemoveIdentifierButtonClick(event) {
        const identifierFieldElement = event.target.closest(".identifier-field-container");
        identifierFieldElement.remove();
        this.updateAddIdentifierControlState();
        this.renewAddIdentifierControl();
        this.updateSubmitButtonState();
    }

    handleEditIdentifierButtonClick(event) {
        const identifierFieldElement = event.target.closest(".identifier-field-container");
        const editIdentifierButton = identifierFieldElement.querySelector(".btn-edit-identifier");
        const validateIdentifierButton = identifierFieldElement.querySelector(".btn-validate-identifier");
        const inputField = identifierFieldElement.querySelector("input");
        const selectField = identifierFieldElement.querySelector("select");
        editIdentifierButton.classList.add("d-none");
        validateIdentifierButton.classList.remove("d-none");
        var self = this;
        inputField.addEventListener('input', function () {
            if (self.checkIdentifierFormat(selectField.value, inputField.value)) {
                inputField.classList.remove("is-invalid");
                validateIdentifierButton.removeAttribute("disabled");
                identifierFieldElement.dataset.validData = true;
                self.updateSubmitButtonState();
            } else {
                inputField.classList.add("is-invalid");
                validateIdentifierButton.setAttribute("disabled", true);
                identifierFieldElement.dataset.validData = false;
                self.updateSubmitButtonState();
            }
        });
        inputField.addEventListener('keypress', function (event) {
            if (event.key === 'Enter' && !validateIdentifierButton.hasAttribute("disabled")) {
                event.preventDefault();
                self.handleIdentifierValidation(event);
            }
        });
        validateIdentifierButton.addEventListener("click", this.handleIdentifierValidation.bind(this));
        inputField.removeAttribute("disabled");
        inputField.focus();
    }

    handleIdentifierValidation(event) {
        const identifierFieldElement = event.target.closest(".identifier-field-container");
        const editIdentifierButton = identifierFieldElement.querySelector(".btn-edit-identifier");
        const validateIdentifierButton = identifierFieldElement.querySelector(".btn-validate-identifier");
        const inputField = identifierFieldElement.querySelector("input");
        const selectField = identifierFieldElement.querySelector("select");
        if (this.checkIdentifierFormat(selectField.value, inputField.value)) {
            inputField.setAttribute("disabled", true);
            inputField.classList.remove("is-invalid");
            editIdentifierButton.classList.remove("d-none");
            validateIdentifierButton.classList.add("d-none");
        } else {
            inputField.classList.add("is-invalid");
        }
    }

    updateAddIdentifierControlState = () => {
        const addIdentifierControlContent = this.getIdentifierFieldContent(this.addIdentifierControlElement);
        if (addIdentifierControlContent.identifierType) {
            this.addIdentifierInputField.removeAttribute("disabled");
            this.addIdentifierInputField.placeholder = this.env.IDENTIFIERS[addIdentifierControlContent.identifierType].placeholder;
        } else {
            this.addIdentifierInputField.setAttribute("disabled", true);
            this.addIdentifierInputField.placeholder = "";
        }
        if (addIdentifierControlContent.identifierType && addIdentifierControlContent.identifierValue) {
            if (this.checkIdentifierFormat(addIdentifierControlContent.identifierType, addIdentifierControlContent.identifierValue)) {
                this.addIdentifierButton.removeAttribute("disabled");
                this.addIdentifierInputField.classList.remove("is-invalid");
            } else {
                this.addIdentifierButton.setAttribute("disabled", true);
                this.addIdentifierInputField.classList.add("is-invalid");
            }
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
        if (this.addIdentifierButton.hasAttribute("disabled")) {
            return;
        }
        this.addIdentifierField(this.getIdentifierFieldContent(this.addIdentifierControlElement))
    }

    addIdentifierField(content) {
        content = {...content, identifierLabel: this.env.IDENTIFIERS[content.identifierType].label};
        this.identifierFieldElement = stringToHTML(ejs.render(identifier_field, content));
        this.identifierFieldsContainer.insertBefore(this.identifierFieldElement, this.addIdentifierControlElement);
        const removeIdentifierButton = this.identifierFieldElement.querySelector(".btn-remove-identifier");
        removeIdentifierButton.addEventListener("click", this.handleRemoveIdentifierButtonClick.bind(this));
        const editIdentifierButton = this.identifierFieldElement.querySelector(".btn-edit-identifier");
        editIdentifierButton.addEventListener("click", this.handleEditIdentifierButtonClick.bind(this));
        this.identifierFieldElement.dataset.validData = true;
        this.renewAddIdentifierControl();
        this.updateSubmitButtonState();
    }

    getIdentifierFieldsContent(validOnly = false) {
        const identifierFieldsContent = [];
        for (const identifierFieldElement of this.formElement.querySelectorAll(".identifier-field-container")) {
            if (validOnly && identifierFieldElement.dataset.validData === "false") {
                continue;
            }
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
        if (this.getIdentifierFieldsContent(true).length > 0) {
            this.runRetrievalButton.removeAttribute("disabled");
        } else {
            this.runRetrievalButton.setAttribute("disabled", true);
        }
    }

    checkIdentifierFormat(identifierType, identifierValue) {
        return new RegExp(this.env.IDENTIFIERS[identifierType].format).test(identifierValue);
    }
}

export default Form;
