import TomSelect from "tom-select";

class EventTypeSelector {

    constructor(rootElementSelector) {
        this.selector = new TomSelect(rootElementSelector, {
            sortField: {field: "text"},
            plugins: ['checkbox_options', 'remove_button', 'clear_button'],
        });
    }

    getValue() {
        return [].concat(this.selector.getValue());
    }
}

export default EventTypeSelector;
