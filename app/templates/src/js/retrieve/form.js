import ejs from "ejs";
import TomSelect from "tom-select";
import DateRangePicker from 'vanillajs-datepicker/DateRangePicker';
import stringToHTML from "../utils";
import identifier_field from "./templates/identifier_field";
import add_identifier_control from "./templates/add_identifier_control";


const IDENTIFIER_NULL_VALUE = "null";

class Form {
    constructor(env, rootElement) {
        this.env = env;
        this.rootElement = rootElement;
        this.formElement = rootElement.querySelector("#form-element");
        this.identifierFieldsContainer = this.formElement.querySelector("#identifier-fields-container");
        this.runRetrievalButton = this.formElement.querySelector("#run-retrieval-btn");
        this.handleReferenceTypesSelect();
        this.handleEventTypesSelect();
        this.handleDataSourcesSelect();
        this.handleDatePickers();
        this.handleIdentifiersSafeModeToggle();
        this.handleHistorySafeModeToggle();
        this.renewAddIdentifierControl();
        this.addSubmitListener();
        this.updateSubmitButtonState();
    }

    handleReferenceTypesSelect() {
        this.referenceTypeSelect = new TomSelect("#reference-type-select", {
            sortField: {field: "text"},
            plugins: ['checkbox_options', 'dropdown_input', 'remove_button', 'clear_button'],
        });
    }

    handleEventTypesSelect() {
        this.eventTypeSelect = new TomSelect("#event-type-select", {
            sortField: {field: "text"},
            plugins: ['checkbox_options', 'remove_button', 'clear_button'],
        });
    }

    handleDataSourcesSelect() {
        this.dataSourcesTypeSelect = new TomSelect("#data-sources-select", {
            sortField: {field: "text"},
            plugins: ['checkbox_options', 'remove_button', 'clear_button'],
        });
    }

    handleDatePickers() {
        this.dateRangePicker = new DateRangePicker(this.formElement.querySelector("#date-range-picker-container"), {
            buttonClass: 'btn',
            clearButton: 'true',
        })
    }

    handleIdentifiersSafeModeToggle() {
        this.identifiersSafeModeToggle = this.formElement.querySelector("#identifiers-safe-mode-toggle");
    }

    handleHistorySafeModeToggle() {
        this.historySafeModeToggle = this.formElement.querySelector("#history-safe-mode-toggle");
    }

    addSubmitListener() {
        this.formElement.addEventListener("submit", this.handleSubmit.bind(this));
    }

    handleSubmit(event) {
        event.preventDefault();
        event.stopPropagation();
        const entitySubmitEvent = new CustomEvent("entity_submit",
            {
                detail:
                    {
                        identifiers: this.getIdentifierFieldsContent(true),
                        name: this.formElement.querySelector("#name-field-input").value,
                        eventTypes: this.eventTypeSelect.getValue(),
                        historySafeMode: this.historySafeModeToggle.checked,
                        identifiersSafeMode: this.identifiersSafeModeToggle.checked,
                    }
            }
        );
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
        this.addIdentifierInputField.addEventListener("input", this.updateAddIdentifierControlState.bind(this));
        this.addIdentifierSelectField.addEventListener("change", this.updateAddIdentifierControlState.bind(this));
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
        editIdentifierButton.classList.add("d-none");
        validateIdentifierButton.classList.remove("d-none");
        const self = this;
        inputField.addEventListener('keyup', function () {
            if (self.checkIdentifierFormat(identifierFieldElement)) {
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
        if (this.checkIdentifierFormat(identifierFieldElement)) {
            inputField.setAttribute("disabled", true);
            inputField.classList.remove("is-invalid");
            editIdentifierButton.classList.remove("d-none");
            validateIdentifierButton.classList.add("d-none");
        } else {
            inputField.classList.add("is-invalid");
        }
    }

    updateAddIdentifierControlState = () => {
        const addIdentifierControlContent = this.getIdentifierFieldContent(this.addIdentifierControlElement, true);
        if (addIdentifierControlContent.identifierType) {
            this.addIdentifierInputField.removeAttribute("disabled");
            this.addIdentifierInputField.placeholder = this.env.IDENTIFIERS[addIdentifierControlContent.identifierType].placeholder;
        } else {
            this.addIdentifierInputField.setAttribute("disabled", true);
            this.addIdentifierInputField.placeholder = "";
        }
        if (addIdentifierControlContent.identifierType && addIdentifierControlContent.identifierValue) {
            if (this.checkIdentifierFormat(this.addIdentifierControlElement)) {
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

    getIdentifierFieldContent(newIdentifierFieldElement, explicitNullValue) {
        const identifierType = newIdentifierFieldElement.querySelector("select.identifier-control-select").value;
        const identifierValue = newIdentifierFieldElement.querySelector("input.identifier-control-input").value;
        //if identifier value il an empty or blank string, return the explicit "null" value
        // user are allowed to clear an identifier value this way
        if (identifierValue.match(/^\s*$/)) {
            return {identifierType: identifierType, identifierValue: explicitNullValue ? IDENTIFIER_NULL_VALUE : ""};
        }
        return {identifierType: identifierType, identifierValue: identifierValue};
    }

    handleAddIdentifierAction() {
        if (this.addIdentifierButton.hasAttribute("disabled")) {
            return;
        }
        this.addIdentifierField(this.getIdentifierFieldContent(this.addIdentifierControlElement, false))
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
            identifierFieldsContent.push(this.getIdentifierFieldContent(identifierFieldElement, false));
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

    checkIdentifierFormat(identifierFieldElement) {
        // return true if the value is an empty or blank string to allow the user to clear the field
        const identifierElementContent = this.getIdentifierFieldContent(identifierFieldElement, true);
        if (identifierElementContent.identifierValue === IDENTIFIER_NULL_VALUE) {
            return true;
        }
        return new RegExp(this.env.IDENTIFIERS[identifierElementContent.identifierType].format).test(identifierElementContent.identifierValue);
    }
}

export default Form;
