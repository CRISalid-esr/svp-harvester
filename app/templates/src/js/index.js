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
    switch (pageIdentifier) {
        case "overview":
            break;
        case "retrieve":
            const client = new Client(env);
            new RetrievePage(env, client, document.getElementById("retrieve-page-content"));
            break;
        case "history":
            break;
    }

}
document.addEventListener("DOMContentLoaded", init);