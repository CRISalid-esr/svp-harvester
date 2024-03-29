/* globals Chart:false, feather:false */
// Import our custom CSS
import '../scss/styles.scss'

// Import all of Bootstrap's JS
import * as bootstrap from 'bootstrap'
import 'bootstrap5-toggle/js/bootstrap5-toggle.ecmas.min'
// Import our custom JS
import env from "./env"
import Client from "./common/client"
import RetrievePage from "./retrieve/retrieve_page"
import HistoryPage from "./history/history_page"
import OverviewPage from "./overview/overview_page"

const enableTooltips = function () {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

}

const init = function () {
    enableTooltips();
    const pageIdentifier = document.getElementById("page-identifier").value;
    let client; // Declare client here
    const apiInformations = {
        apiHost: env.apiHost || document.getElementById("api-host")?.value,
        apiPath: env.apiPath || document.getElementById("api-path")?.value,
    }
    switch (pageIdentifier) {
        case "overview":
            client = new Client({...env, ...apiInformations});
            new OverviewPage(env, client, document.getElementById("overview-page-content"));
            break;
        case "retrieve":
            client = new Client({...env, ...apiInformations});
            new RetrievePage(env, client, document.getElementById("retrieve-page-content"));
            break;
        case "history":
            client = new Client({...env, ...apiInformations});
            const subpage = document.getElementById("subpage-identifier").value;
            new HistoryPage(env, client, document.getElementById("history-page-content",), subpage)
            break;
        case "settings":
            break;
    }

}
document.addEventListener("DOMContentLoaded", init);
