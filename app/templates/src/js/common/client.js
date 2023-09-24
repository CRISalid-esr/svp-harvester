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
        return this.env.SVP_HARVESTER_API_HOST + ":" + this.env.SVP_HARVESTER_API_PORT + this.env.SVP_HARVESTER_API_PATH;
    }
}

export default Client;
