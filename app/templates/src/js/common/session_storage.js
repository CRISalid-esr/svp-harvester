class SessionStorage {
  KEY_NAME = "name";
  KEY_EVENT_TYPE = "#event-type-select";
  KEY_HARVESTER = "#harvesters-select";
  KEYS_IDENTIFIER = [
    "id_hal_i",
    "id_hal_s",
    "idref",
    "orcid",
    "researcherid",
    "scopusid",
    "arxiv",
    "pubmed",
  ];

  constructor(form) {
    this.form = form;
  }

  setItem(key, value) {
    sessionStorage.setItem(key, value);
  }

  getItem(key) {
    return sessionStorage.getItem(key);
  }

  deleteItem(key) {
    sessionStorage.removeItem(key);
  }

  fillForm() {
    this.KEYS_IDENTIFIER.forEach((key) => {
      const value = this.getItem(key);
      if (value) {
        this.form.addIdentifierField({
          identifierType: key,
          identifierValue: value,
        });
      }
    });
    if (this.getItem(this.KEY_NAME)) {
      this.form.formElement.querySelector("#name-field-input").value =
        this.getItem(this.KEY_NAME);
    }
    if (this.getItem(this.KEY_EVENT_TYPE)) {
      const values = this.getItem(this.KEY_EVENT_TYPE).split(",");
      this.form.eventTypeSelect.setValues(values);
    }
    if (this.getItem(this.KEY_HARVESTER)) {
      const values = this.getItem(this.KEY_HARVESTER).split(",");
      this.form.harvestersSelect.setValues(values);
    }
  }

  clear() {
    sessionStorage.clear();
  }
}

export default SessionStorage;
