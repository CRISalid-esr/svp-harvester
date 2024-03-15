import ejs from "ejs";
import TomSelect from "tom-select";
import DateRangePicker from "vanillajs-datepicker/DateRangePicker";
import stringToHTML from "../utils";
import identifier_field from "./templates/identifier_field";
import add_identifier_control from "./templates/add_identifier_control";
import TextFieldSelector from "../common/text_field_selector";
import SessionStorage from "../common/session_storage";

const IDENTIFIER_NULL_VALUE = "null";

class Form {
  constructor(env, rootElement) {
    this.env = env;
    this.rootElement = rootElement;
    this.formElement = rootElement.querySelector("#form-element");
    this.identifierFieldsContainer = this.formElement.querySelector(
      "#identifier-fields-container"
    );
    this.runRetrievalButton =
      this.formElement.querySelector("#run-retrieval-btn");
    this.stopRetrievalButton = this.formElement.querySelector(
      "#stop-retrieval-btn"
    );
    this.clearFormButton = this.formElement.querySelector("#clear-form-btn");
    this.handleReferenceTypesSelect();
    this.handleEventTypesSelect();
    this.handleDataSourcesSelect();
    this.handleIdentifiersSafeModeToggle();
    this.handleHistorySafeModeToggle();
    this.renewAddIdentifierControl();
    this.addSubmitListener();
    this.addClearFormListener();
    this.addStopRetrievalListener();
    this.addNameInputListener();
    this.sessionStorage = new SessionStorage(this);
    this.fillWithSessionStorage();
    this.updateSubmitButtonState();
  }

  retrieveFinished() {
    this.hideButton(this.stopRetrievalButton);
    this.showButton(this.runRetrievalButton);
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

  handleReferenceTypesSelect() {
    this.referenceTypeSelect = new TextFieldSelector("#reference-type-select", [
      "dropdown_input",
    ]);
  }

  handleEventTypesSelect() {
    this.eventTypeSelect = new TextFieldSelector("#event-type-select");
  }

  handleDataSourcesSelect() {
    this.harvestersSelect = new TextFieldSelector("#harvesters-select");
  }

  handleIdentifiersSafeModeToggle() {
    this.identifiersSafeModeToggle = this.formElement.querySelector(
      "#identifiers-safe-mode-toggle"
    );
  }

  handleHistorySafeModeToggle() {
    this.historySafeModeToggle = this.formElement.querySelector(
      "#history-safe-mode-toggle"
    );
  }

  handleStopRetrieval() {
    this.rootElement.dispatchEvent(new CustomEvent("entity_cancel"));
  }

  addSubmitListener() {
    this.formElement.addEventListener("submit", this.handleSubmit.bind(this));
  }

  addClearFormListener() {
    this.clearFormButton.addEventListener("click", this.clearForm.bind(this));
  }

  addStopRetrievalListener() {
    this.stopRetrievalButton.addEventListener(
      "click",
      this.handleStopRetrieval.bind(this)
    );
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
    this.updateSubmitButtonState();
  }

  handleSubmit(event) {
    event.preventDefault();
    event.stopPropagation();
    this.hideButton(this.runRetrievalButton);
    this.showButton(this.stopRetrievalButton);
    const entitySubmitEvent = new CustomEvent("entity_submit", {
      detail: {
        identifiers: this.getIdentifierFieldsContent(true),
        name: this.formElement.querySelector("#name-field-input").value,
        eventTypes: this.eventTypeSelect.getValue(),
        harvesters: this.harvestersSelect.getValue(),
        historySafeMode: this.historySafeModeToggle.checked,
        identifiersSafeMode: this.identifiersSafeModeToggle.checked,
      },
    });
    this.rootElement.dispatchEvent(entitySubmitEvent);
  }

  hideButton(element) {
    element.classList.add("d-none");
  }

  showButton(element) {
    element.classList.remove("d-none");
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
    this.updateSubmitButtonState();
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
        self.updateSubmitButtonState();
      } else {
        inputField.classList.add("is-invalid");
        validateIdentifierButton.setAttribute("disabled", true);
        identifierFieldElement.dataset.validData = false;
        self.updateSubmitButtonState();
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

  handleAddIdentifierAction() {
    if (this.addIdentifierButton.hasAttribute("disabled")) {
      return;
    }
    this.addIdentifierField(
      this.getIdentifierFieldContent(this.addIdentifierControlElement, false)
    );
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
    this.updateSubmitButtonState();
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

  updateSubmitButtonState() {
    if (this.getIdentifierFieldsContent(true).length > 0) {
      this.runRetrievalButton.removeAttribute("disabled");
    } else {
      this.runRetrievalButton.setAttribute("disabled", true);
    }
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
}

export default Form;
