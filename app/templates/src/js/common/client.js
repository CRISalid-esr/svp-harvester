import qs from 'qs';

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

    async getHistoryRetrieval(params) {
        return await this.axios.get(this.apiUrl() + "/retrievals/summary", {
            params: params, paramsSerializer: params => { return qs.stringify(params, { arrayFormat: 'repeat' }) }
        });
    }

    async getHistoryPublication(params) {
        return await this.axios.get(this.apiUrl() + "/references/summary", {
            params: params, paramsSerializer: params => { return qs.stringify(params, { arrayFormat: 'repeat' }) }
        });
    }

    async getReference(referenceId) {
        return await this.axios.get(this.apiUrl() + "/references/" + referenceId);
    }

    async getRetrieval(retrievalId) {
        return await this.axios.get(this.apiUrl() + "/retrievals/" + retrievalId);
    }

    async getReferencesByHarvesterMetrics() {
        return await this.axios.get(this.apiUrl() + "/metrics/references/by_harvester");
    }

    apiUrl() {
        return this.env.apiHost + this.env.apiPath;
    }
}

export default Client;
