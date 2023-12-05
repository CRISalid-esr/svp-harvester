import BaseCollectFormClass from "../common/base_form";
import TomSelect from "tom-select";

class RetrieveForm extends BaseCollectFormClass {
    constructor(env, rootElement) {
        super(env, rootElement);
        // form-specific setup
        this.handleIdentifiersSafeModeToggle();
        this.handleHistorySafeModeToggle();
        this.handleReferenceTypesSelect();
    }

    handleReferenceTypesSelect() {
        this.referenceTypeSelect = new TomSelect("#reference-type-select", {
            sortField: {field: "text"},
            plugins: ['checkbox_options', 'dropdown_input', 'remove_button', 'clear_button'],
        });
    }

    handleIdentifiersSafeModeToggle() {
        this.identifiersSafeModeToggle = this.formElement.querySelector("#identifiers-safe-mode-toggle");
    }

    handleHistorySafeModeToggle() {
        this.historySafeModeToggle = this.formElement.querySelector("#history-safe-mode-toggle");
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
                        harvesters: this.harvestersSelect.getValue(),
                        historySafeMode: this.historySafeModeToggle.checked,
                        identifiersSafeMode: this.identifiersSafeModeToggle.checked,
                    }
            }
        );
        this.rootElement.dispatchEvent(entitySubmitEvent);
    }
}

export default RetrieveForm
