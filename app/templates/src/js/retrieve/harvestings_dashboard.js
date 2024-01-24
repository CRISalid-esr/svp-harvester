import ejs from "ejs";
import stringToHTML from "../utils";
import harvesting_progress_widget from "./templates/harvesting_progress_widget";
import current_entity_card_identifier from "./templates/current_entity_card_identifier";
import current_entity_card_name from "./templates/current_entity_card_name";
import * as bootstrap from 'bootstrap'

class HarvestingDashboard {
    constructor(env, rootElement) {
        this.env = env;
        this.rootElement = rootElement;
        this.widgetContainerElement = rootElement.querySelector("#harvesting-progress-widgets-container");
        this.entityAttributesContainerElement = rootElement.querySelector("#entity-attributes-card-container");
    }

    updateEntityCard(entity) {
        this.entityAttributesContainerElement.innerHTML = "";

        if (entity.name?.length > 0) {
            const nameElement = stringToHTML(ejs.render(current_entity_card_name, { name: entity.name }));
            this.entityAttributesContainerElement.appendChild(nameElement);
        }

        if (entity.identifiers?.length > 0) {
            for (const identifier of entity.identifiers) {
                const identifierElement = stringToHTML(ejs.render(current_entity_card_identifier, identifier));
                this.entityAttributesContainerElement.appendChild(identifierElement);
            }
        }

    }

    updateWidgets(harvestings) {
        this.widgetContainerElement.innerHTML = "";
        //sort harvestings by harvester key alphabetically
        harvestings.sort((a, b) => {
            if (a.harvester < b.harvester) {
                return -1;
            }
            if (a.harvester > b.harvester) {
                return 1;
            }
            return 0;
        });
        for (const harvesting of harvestings) {
            const widgetElement = stringToHTML(ejs.render(harvesting_progress_widget, harvesting));
            this.widgetContainerElement.appendChild(widgetElement);
        }
        const popoverTriggerList = this.widgetContainerElement.querySelectorAll('[data-bs-toggle="popover"]')
        const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))
        // Listen for click events to close popovers
        document.addEventListener('click', (event) => {
            if (event.target.dataset.bsToggle !== 'popover') {
                popoverList.forEach(popover => {
                    popover.hide();
                });
            }
        });

    }
}

export default HarvestingDashboard;
