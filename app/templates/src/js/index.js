import env from "./env"
import Client from "./common/client"
import RetrievePage from "./retrieve/retrieve_page"

const init = function () {
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