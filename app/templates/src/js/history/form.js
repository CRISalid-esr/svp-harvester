import EventTypeSelector from "../common/event_type_selector";
import TomSelect from "tom-select";
import DateRangePicker from "vanillajs-datepicker/DateRangePicker";

class HistoryForm {
    constructor(env, rootElement) {
        this.rootElement = rootElement;
        this.formElement = rootElement.querySelector("#form-element");
        this.handleEventTypesSelect();
        this.handleDatePickers();
        this.handleDataSourcesSelect();
    }

    handleEventTypesSelect() {
        this.eventTypeSelect = new EventTypeSelector("#event-type-select");
    }

    handleDataSourcesSelect() {
        this.harvestersSelect = new TomSelect("#harvesters-select", {
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
}

export default HistoryForm