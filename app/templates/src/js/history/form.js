import DateRangePicker from "vanillajs-datepicker/DateRangePicker";
import stringToHTML from "../utils";
import ejs from "ejs";

//TODO: move identifier control into common/template
import add_identifier_control from "../retrieve/templates/add_identifier_control";

//TODO: complete Form for History page
class Form{

    constructor(env, rootElement) {
        this.env = env;
        this.rootElement = rootElement;
        this.formElement = rootElement.querySelector("#form-element");
        this.identifierFieldsContainer = this.formElement.querySelector("#identifier-fields-container");
        this.runRetrievalHistoryButton = this.formElement.querySelector("#run-retrieval-history-btn");
        this.renewAddIdentifierControl();
        this.handleDatePickers();
    }

    //TODO: Add functionalities of identifier control while checking to only get the needed (use retrieve form as base)
    renewAddIdentifierControl(){
        if (this.addIdentifierControlElement) {
            this.addIdentifierControlElement.remove();
        }
        this.addIdentifierControlElement = stringToHTML(ejs.render(add_identifier_control, {identifiers: this.getIdentifierList()}));
        this.identifierFieldsContainer.appendChild(this.addIdentifierControlElement);
    }

    getIdentifierList() {
    // Return an array containing all identifiers from this.env.IDENTIFIERS
    return Object.values(this.env.IDENTIFIERS);
}

    handleDatePickers() {
    this.dateRangePicker = new DateRangePicker(this.formElement.querySelector("#date-range-picker-container"), {
        buttonClass: 'btn',
        clearButton: 'true',
    })
    }

}

export default Form