import Form from "./form";
import Control from "./control";

class RetrievePage {

    constructor(env, client, rootElement) {
        const form = new Form(env, rootElement)
        new Control(env, form, rootElement, client);
    }
}

export default RetrievePage;
