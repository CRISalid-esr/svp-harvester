import TextFieldSelector from "../common/text_field_selector";
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
}

export default HistoryForm