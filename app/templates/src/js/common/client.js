class Client {

    const
    axios = require('axios');

    constructor(env) {
        this.env = env;
    }

    async postRetrieval(identifiers) {
        return await this.axios.post(this.apiUrl() + "/references/retrieval", identifiers);
    }

    async getHarvestingState(retrievalUrl) {
        return await this.axios.get(retrievalUrl);
    }

    apiUrl() {
        return this.env.apiHost + this.env.apiPath;
    }
}

export default Client;
