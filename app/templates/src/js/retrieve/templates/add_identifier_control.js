const add_identifier_control = `
<div class="input-group mt-3 mb-3" id="new_identifier-field">
                    <div style="width: max-content;">
                        <select class="form-select rounded-end-0" aria-label="Example select with button addon">
                            <option selected disabled value="">Sélectionnez un type d'identifiant</option>
                            <% Object.entries(identifiers).forEach(function(identifier){ %>
                                <option value="<%= identifier[0] %>"><%= identifier[1] %></option>
                            <% }); %>
                        </select>
                    </div>
                    <input type="text" class="form-control rounded-0" placeholder="Identifiant">
                    <button type="button" class="btn btn-success rounded-start-0" id="add-identifier-button">Ajouter</button>
                </div>
`
export default add_identifier_control;