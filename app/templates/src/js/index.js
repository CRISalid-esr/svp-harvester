import env from "./env"
import Client from "./client"
import Form from "./form"


const init = function () {
    console.log(env)
    const client = new Client(env)
    const form = new Form(client, document.getElementById("form-element"))
}
document.addEventListener("DOMContentLoaded", init);
