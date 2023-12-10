import TextFieldSelector from "../common/text_field_selector";
import TomSelect from "tom-select";
import DateRangePicker from "vanillajs-datepicker/DateRangePicker";
import th from "vanillajs-datepicker/locales/th";

class HistoryForm {
    constructor(env, rootElement, subpage) {
        this.env = env;
        this.rootElement = rootElement;
        this.subpage = subpage
        this.formElement = rootElement.querySelector("#form-element");
        this.handleEventTypesSelect();
        this.handleDatePickers();
        this.handleDataSourcesSelect();

        this.addSubmitListener();
    }

    handleEventTypesSelect() {
        this.eventTypeSelect = new TextFieldSelector("#event-type-select");
    }

    handleDataSourcesSelect() {
        this.harvestersSelect = new TextFieldSelector("#harvesters-select");
    }

    handleDatePickers() {
        this.dateRangePicker = new DateRangePicker(this.formElement.querySelector("#date-range-picker-container"), {
            buttonClass: 'btn',
            clearButton: 'true',
        })
    }

    addSubmitListener() {
        this.formElement.addEventListener("submit", this.handleSubmit.bind(this));
    }

    handleSubmit(event){
        event.preventDefault();
        event.stopPropagation();
        const entitySubmitEvent = new CustomEvent("entity_submit",
            {
                detail:
                    {
                        subpage: this.subpage,
                        eventTypes: this.eventTypeSelect.getValue(),
                        harvesters: this.harvestersSelect.getValue(),
                        //TODO: Complete the base event
                    }
            }
            );
        this.rootElement.dispatchEvent(entitySubmitEvent)
    }
}

export default HistoryForm