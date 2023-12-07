import EventTypeSelector from "../common/event_type_selector";

class HistoryForm {
    constructor(env, rootElement) {
        this.handleEventTypesSelect();
    }
    handleEventTypesSelect() {
        this.eventTypeSelect = new EventTypeSelector("#event-type-select");
    }

}

export default HistoryForm