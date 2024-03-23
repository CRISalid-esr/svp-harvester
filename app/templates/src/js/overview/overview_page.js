import Control from "./control";
import Dashboard from "./dashboard";

class OverViewPage {

    constructor(env, client, rootElement) {
        const dashboard = new Dashboard(env, rootElement)
        new Control(env, rootElement, client, dashboard);
    }
}

export default OverViewPage;
