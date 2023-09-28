const add_identifier_control = `
<div class="input-group mt-3 mb-3" id="add-identifier-control">
                    <div style="width: max-content;">
                        <select class="form-select rounded-end-0" aria-label="Example select with button addon" id="add-identifier-control-select">
                            <option selected disabled value="">Sélectionnez un type d'identifiant</option>
                            <% Object.entries(identifiers).forEach(function(identifier){ %>
                                <option value="<%= identifier[0] %>"><%= identifier[1] %></option>
                            <% }); %>
                        </select>
                    </div>
                    <input type="text" class="form-control rounded-0" placeholder="Identifiant" id="add-identifier-control-input">
                    <button type="button" class="btn btn-success rounded-start-0" id="add-identifier-control-button"><i class="bi bi-plus-circle"></i></button>
                </div>
`
export default add_identifier_control;