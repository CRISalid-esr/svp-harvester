import HistoryForm from "./form";
import HistoryTable from "./history_table";
import Control from "./control";

class HistoryPage {
    constructor(env, client, rootElement, subpage) {
        const form = new HistoryForm(env, rootElement, subpage)
        const historyTable = new HistoryTable(env, rootElement, subpage, client);
        new Control(env, form, historyTable, rootElement, subpage, client);
    }
}

export default HistoryPage