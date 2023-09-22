class Client {

    const
    axios = require('axios');

    constructor(env) {
        this.env = env;
        console.log(this.apiUrl());
    }

    async postRetrieval(identifiers) {
        return await this.axios.post(this.apiUrl() + "/references/retrieval", identifiers);
    }

    apiUrl() {
        return this.env.SVP_HARVESTER_API_HOST + ":" + this.env.SVP_HARVESTER_API_PORT + this.env.SVP_HARVESTER_API_PATH;
    }
}

export default Client;
