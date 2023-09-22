import env from "./env"
import Client from "./client"
import Form from "./form"


const init = function () {
    const client = new Client(env)
    new Form(client, document.getElementById("form-element"))
}
document.addEventListener("DOMContentLoaded", init);