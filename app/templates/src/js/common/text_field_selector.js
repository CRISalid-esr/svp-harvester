import TomSelect from "tom-select";

class TextFieldSelector {

    constructor(rootElementSelector, plugins = []) {
        this.defaultPlugins = ['checkbox_options', 'remove_button', 'clear_button']
        this.allowedPlugins = ['dropdown_input'].concat(this.defaultPlugins);

        // Filter the 'plugins' passed in to remove any plugins not part of 'allowedPlugins'
        const validPlugins = plugins.filter(plugin => this.allowedPlugins.includes(plugin))

        // Combine and deduplicate plugins from default and provided lists.
        const allPlugins = [...new Set([...this.defaultPlugins, ...validPlugins])];

        this.selector = new TomSelect(rootElementSelector, {
            sortField: {field: "text"},
            plugins: allPlugins,
        });
    }

    getValue() {
        return [].concat(this.selector.getValue());
    }
}

export default TextFieldSelector;
