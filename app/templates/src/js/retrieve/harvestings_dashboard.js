import ejs from "ejs";
import stringToHTML from "../utils";
import harvesting_progress_widget from "./templates/harvesting_progress_widget";
import current_entity_identifier from "./templates/current_entity_identifier";

class HarvestingDashboard {
    constructor(env, rootElement) {
        this.env = env;
        this.rootElement = rootElement;
        this.widgetContainerElement = rootElement.querySelector("#harvesting-progress-widgets-container");
        this.identifiersContainerElement = rootElement.querySelector("#entity-identifiers-container");
    }

    updateIdentifiers(identifiers) {
        this.identifiersContainerElement.innerHTML = "";
        for (const identifier of identifiers) {
            const identifierElement = stringToHTML(ejs.render(current_entity_identifier, identifier));
            this.identifiersContainerElement.appendChild(identifierElement);
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
    }
}

export default HarvestingDashboard;
