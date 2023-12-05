import BaseCollectFormClass from "../common/base_form";

class HistoryForm extends BaseCollectFormClass {
    constructor(env, rootElement) {
        super(env, rootElement);
    }
    //TODO:
    // 1 - Adjust to allow multiple identifier of same kind to be used

    // remainingIdentifiers() {
    //     // Return an array containing all identifiers from this.env.IDENTIFIERS
    //     return Object.values(this.env.IDENTIFIERS);
    // }
}

export default HistoryForm