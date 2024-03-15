import TextFieldSelector from "../common/text_field_selector";
import TomSelect from "tom-select";
import DateRangePicker from "vanillajs-datepicker/DateRangePicker";
import add_identifier_control from "../retrieve/templates/add_identifier_control";
import identifier_field from "../retrieve/templates/identifier_field";
import stringToHTML from "../utils";
import th from "vanillajs-datepicker/locales/th";
import SessionStorage from "../common/session_storage";

const IDENTIFIER_NULL_VALUE = "null";
const SPINNER =
  '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';

class HistoryForm {
  constructor(env, rootElement, subpage) {
    this.env = env;
    this.rootElement = rootElement;
    this.subpage = subpage;
    this.formElement = rootElement.querySelector("#form-element");
    this.identifierFieldsContainer = this.formElement.querySelector(
      "#identifier-fields-container"
    );
    this.runSearchButton = this.formElement.querySelector("#run-history-btn");
    this.clearFormButton = this.formElement.querySelector("#clear-form-btn");
    this.handleEventTypesSelect();
    this.handleDatePickers();
    this.handleDataSourcesSelect();
    this.renewAddIdentifierControl();
    this.addSubmitListener();
    this.addNameInputListener();
    this.sessionStorage = new SessionStorage(this);
    this.fillWithSessionStorage();
    this.addClearFormListener();
  }

  fillWithSessionStorage() {
    this.sessionStorage.fillForm();
  }

  addNameInputListener() {
    this.formElement
      .querySelector("#name-field-input")
      .addEventListener("input", (event) => {
        this.sessionStorage.setItem("name", event.target.value);
      });
  }

  handleEventTypesSelect() {
    this.eventTypeSelect = new TextFieldSelector("#event-type-select");
  }

  handleDataSourcesSelect() {
    this.harvestersSelect = new TextFieldSelector("#harvesters-select");
  }

  handleDatePickers() {
    this.dateRangePicker = new DateRangePicker(
      this.formElement.querySelector("#date-range-picker-container"),
      {
        buttonClass: "btn",
        clearButton: "true",
        allowOneSidedRange: "true",
      }
    );
    this.dateRangePicker.setDates([Date.now() - 1000 * 60 * 60 * 24, null]);
  }

  addSubmitListener() {
    this.formElement.addEventListener("submit", this.searchSubmit.bind(this));
  }

  addClearFormListener() {
    this.clearFormButton.addEventListener("click", this.clearForm.bind(this));
  }

  clearForm() {
    this.formElement.reset();
    this.sessionStorage.clear();
    this.removeAllIdentifierFields();
    this.eventTypeSelect.setValues([
      "created",
      "updated",
      "deleted",
      "unchanged",
    ]);
    this.harvestersSelect.setValues([
      "scanr",
      "hal",
      "idref",
      "openalex",
      "scopus",
    ]);
  }

  removeAllIdentifierFields() {
    const identifierFieldsElement = this.formElement.querySelectorAll(
      ".identifier-field-container"
    );
    for (const identifierFieldElement of identifierFieldsElement) {
      identifierFieldElement.remove();
    }
    this.updateAddIdentifierControlState();
    this.renewAddIdentifierControl();
  }

  renewAddIdentifierControl() {
    if (this.addIdentifierControlElement) {
      this.addIdentifierControlElement.remove();
    }
    this.addIdentifierControlElement = stringToHTML(
      ejs.render(add_identifier_control, {
        identifiers: this.remainingIdentifiers(),
      })
    );
    this.identifierFieldsContainer.appendChild(
      this.addIdentifierControlElement
    );
    this.addIdentifierButton = this.formElement.querySelector(
      "#add-identifier-control-button"
    );
    this.addIdentifierInputField = this.formElement.querySelector(
      "#add-identifier-control-input"
    );
    this.addIdentifierSelectField = this.formElement.querySelector(
      "#add-identifier-control-select"
    );
    this.addIdentifierInputField.addEventListener(
      "input",
      this.updateAddIdentifierControlState.bind(this)
    );
    this.addIdentifierSelectField.addEventListener(
      "change",
      this.updateAddIdentifierControlState.bind(this)
    );
    const self = this;
    this.addIdentifierControlElement.addEventListener(
      "keypress",
      function (event) {
        if (event.key === "Enter") {
          event.preventDefault();
          self.handleAddIdentifierAction();
        }
      }
    );
    this.addIdentifierButton.addEventListener(
      "click",
      this.handleAddIdentifierAction.bind(this)
    );
    this.updateAddIdentifierControlState();
  }

  updateAddIdentifierControlState = () => {
    const addIdentifierControlContent = this.getIdentifierFieldContent(
      this.addIdentifierControlElement,
      true
    );
    if (addIdentifierControlContent.identifierType) {
      this.addIdentifierInputField.removeAttribute("disabled");
      this.addIdentifierInputField.placeholder =
        this.env.identifiers[
          addIdentifierControlContent.identifierType
        ].placeholder;
    } else {
      this.addIdentifierInputField.setAttribute("disabled", true);
      this.addIdentifierInputField.placeholder = "";
    }
    if (
      addIdentifierControlContent.identifierType &&
      addIdentifierControlContent.identifierValue
    ) {
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
  };

  handleRemoveIdentifierButtonClick(event) {
    const identifierFieldElement = event.target.closest(
      ".identifier-field-container"
    );
    this.sessionStorage.deleteItem(
      identifierFieldElement.querySelector("option").value
    );
    identifierFieldElement.remove();
    this.updateAddIdentifierControlState();
    this.renewAddIdentifierControl();
  }

  addIdentifierField(content) {
    content = {
      ...content,
      identifierLabel: this.env.identifiers[content.identifierType].label,
    };
    this.identifierFieldElement = stringToHTML(
      ejs.render(identifier_field, content)
    );
    this.identifierFieldsContainer.insertBefore(
      this.identifierFieldElement,
      this.addIdentifierControlElement
    );
    const removeIdentifierButton = this.identifierFieldElement.querySelector(
      ".btn-remove-identifier"
    );
    removeIdentifierButton.addEventListener(
      "click",
      this.handleRemoveIdentifierButtonClick.bind(this)
    );
    const editIdentifierButton = this.identifierFieldElement.querySelector(
      ".btn-edit-identifier"
    );
    editIdentifierButton.addEventListener(
      "click",
      this.handleEditIdentifierButtonClick.bind(this)
    );
    this.identifierFieldElement.dataset.validData = true;
    this.renewAddIdentifierControl();
  }

  handleEditIdentifierButtonClick(event) {
    const identifierFieldElement = event.target.closest(
      ".identifier-field-container"
    );
    const editIdentifierButton = identifierFieldElement.querySelector(
      ".btn-edit-identifier"
    );
    const validateIdentifierButton = identifierFieldElement.querySelector(
      ".btn-validate-identifier"
    );
    const inputField = identifierFieldElement.querySelector("input");
    editIdentifierButton.classList.add("d-none");
    validateIdentifierButton.classList.remove("d-none");
    const self = this;
    inputField.addEventListener("keyup", function () {
      if (self.checkIdentifierFormat(identifierFieldElement)) {
        inputField.classList.remove("is-invalid");
        validateIdentifierButton.removeAttribute("disabled");
        identifierFieldElement.dataset.validData = true;
      } else {
        inputField.classList.add("is-invalid");
        validateIdentifierButton.setAttribute("disabled", true);
        identifierFieldElement.dataset.validData = false;
      }
    });
    inputField.addEventListener("keypress", function (event) {
      if (
        event.key === "Enter" &&
        !validateIdentifierButton.hasAttribute("disabled")
      ) {
        event.preventDefault();
        self.handleIdentifierValidation(event);
      }
    });
    validateIdentifierButton.addEventListener(
      "click",
      this.handleIdentifierValidation.bind(this)
    );
    inputField.removeAttribute("disabled");
    inputField.focus();
  }

  handleIdentifierValidation(event) {
    const identifierFieldElement = event.target.closest(
      ".identifier-field-container"
    );
    const editIdentifierButton = identifierFieldElement.querySelector(
      ".btn-edit-identifier"
    );
    const validateIdentifierButton = identifierFieldElement.querySelector(
      ".btn-validate-identifier"
    );
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

  handleAddIdentifierAction() {
    if (this.addIdentifierButton.hasAttribute("disabled")) {
      return;
    }
    this.addIdentifierField(
      this.getIdentifierFieldContent(this.addIdentifierControlElement, false)
    );
  }

  getIdentifierFieldContent(newIdentifierFieldElement, explicitNullValue) {
    const identifierType = newIdentifierFieldElement.querySelector(
      "select.identifier-control-select"
    ).value;
    const identifierValue = newIdentifierFieldElement.querySelector(
      "input.identifier-control-input"
    ).value;
    //if identifier value il an empty or blank string, return the explicit "null" value
    // user are allowed to clear an identifier value this way
    if (identifierValue.match(/^\s*$/)) {
      return {
        identifierType: identifierType,
        identifierValue: explicitNullValue ? IDENTIFIER_NULL_VALUE : "",
      };
    }
    return { identifierType: identifierType, identifierValue: identifierValue };
  }

  remainingIdentifiers() {
    const remainingIdentifiers = {};
    for (const identifier of Object.entries(this.env.identifiers)) {
      if (
        !this.getIdentifierFieldsContent().find(
          (identifierFieldContent) =>
            identifierFieldContent.identifierType === identifier[0]
        )
      ) {
        remainingIdentifiers[identifier[0]] = identifier[1];
      }
    }
    return remainingIdentifiers;
  }

  getIdentifierFieldsContent(validOnly = false) {
    const identifierFieldsContent = [];
    for (const identifierFieldElement of this.formElement.querySelectorAll(
      ".identifier-field-container"
    )) {
      if (validOnly && identifierFieldElement.dataset.validData === "false") {
        continue;
      }
      var content = this.getIdentifierFieldContent(
        identifierFieldElement,
        false
      );
      this.sessionStorage.setItem(
        content.identifierType,
        content.identifierValue
      );
      identifierFieldsContent.push(content);
    }
    return identifierFieldsContent;
  }

  checkIdentifierFormat(identifierFieldElement) {
    // return true if the value is an empty or blank string to allow the user to clear the field
    const identifierElementContent = this.getIdentifierFieldContent(
      identifierFieldElement,
      true
    );
    if (identifierElementContent.identifierValue === IDENTIFIER_NULL_VALUE) {
      return true;
    }
    return new RegExp(
      this.env.identifiers[identifierElementContent.identifierType].format
    ).test(identifierElementContent.identifierValue);
  }

  spinnerOn() {
    this.runSearchButton.setAttribute("disabled", true);
    this.runSearchButton.removeChild(this.runSearchButton.firstChild);
    let spinner = document.createElement("span");
    spinner.classList.add(
      "spinner-border",
      "spinner-border-sm",
      "spinner-inline"
    );
    spinner.setAttribute("role", "status");
    this.runSearchButton.insertBefore(spinner, this.runSearchButton.firstChild);
  }

  spinnerOff() {
    this.runSearchButton.removeAttribute("disabled");
    this.runSearchButton.removeChild(this.runSearchButton.firstChild);
    let lookup = document.createElement("i");
    lookup.classList.add("bi", "bi-search");
    this.runSearchButton.insertBefore(lookup, this.runSearchButton.firstChild);
  }

  searchSubmit(event) {
    if (event !== undefined) {
      event.preventDefault();
      event.stopPropagation();
    }
    var textSearch;
    var hideEmptyCollection;
    if (this.subpage === "publication_history") {
      textSearch = this.formElement.querySelector(
        "#publication-history-search-bar"
      ).value;
    }
    if (this.subpage === "collection_history") {
      hideEmptyCollection = this.formElement.querySelector(
        "#hide_empty_results_checkbox"
      ).checked;
    }
    const entitySubmitEvent = new CustomEvent("entity_submit", {
      detail: {
        subpage: this.subpage,
        eventTypes: this.eventTypeSelect.getValue(),
        harvesters: this.harvestersSelect.getValue(),
        identifiers: this.getIdentifierFieldsContent(true),
        name: this.formElement.querySelector("#name-field-input").value,
        dateRange: this.dateRangePicker.getDates("yyyy-mm-dd"),
        textSearch: textSearch,
        hideEmptyCollection: hideEmptyCollection,
      },
    });
    this.rootElement.dispatchEvent(entitySubmitEvent);
  }
}

export default HistoryForm;
