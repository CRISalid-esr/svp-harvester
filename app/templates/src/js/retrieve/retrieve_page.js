import Form from "./form";
import Control from "./control";
import HarvestingDashboard from "./harvestings_dashboard";

class RetrievePage {

    constructor(env, client, rootElement) {
        const form = new Form(env, rootElement)
        const harvestingDashboard = new HarvestingDashboard(env, rootElement);
        new Control(env, form, harvestingDashboard, rootElement, client);
    }
}

export default RetrievePage;
