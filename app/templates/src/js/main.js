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

const enableTooltips = function () {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

}

const init = function () {
    enableTooltips();
    const pageIdentifier = document.getElementById("page-identifier").value;
    const apiInformations = {
        apiHost: env.apiHost || document.getElementById("api-host")?.value,
        apiPath: env.apiPath || document.getElementById("api-path")?.value,
    }
    switch (pageIdentifier) {
        case "overview":
            break;
        case "retrieve":
            const client = new Client({...env, ...apiInformations});
            new RetrievePage(env, client, document.getElementById("retrieve-page-content"));
            break;
        case "history":
            break;
    }

}
document.addEventListener("DOMContentLoaded", init);
