import Form from "./form";
import HistoryTable from "./history_table";
import Control from "./control";

class HistoryPage {
    constructor(env,client, rootElement) {
        const form = new Form(env, rootElement)
        const historyTable = new HistoryTable(env, rootElement);
        new Control(env, form, historyTable, rootElement, client);
    }
}

export default HistoryPage