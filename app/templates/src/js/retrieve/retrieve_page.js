import Form from "./form";
import Control from "./control";
import HarvestingDashboard from "./harvestings_dashboard";
import ReferencesTable from "./references_table";

class RetrievePage {

    constructor(env, client, rootElement) {
        const form = new Form(env, rootElement)
        const referencesTable = new ReferencesTable(env, rootElement, client);
        const harvestingDashboard = new HarvestingDashboard(env, rootElement);
        new Control(env, form, harvestingDashboard, referencesTable, rootElement, client);
    }
}

export default RetrievePage;
