import HistoryForm from "./form";
import HistoryTable from "./history_table";
import Control from "./control";

class HistoryPage {
    constructor(env,client, rootElement, subpage) {
        const form = new HistoryForm(env, rootElement, subpage)
        const historyTable = new HistoryTable(env, rootElement, subpage);
        new Control(env, form, historyTable, rootElement, client);
    }
}

export default HistoryPage