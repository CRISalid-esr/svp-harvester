const identifier_field = `<div class="input-group mt-3 mb-3 identifier-field-container">
                    <div style="width: max-content;">
                        <select disabled class="form-select rounded-end-0" aria-label="Example select with button addon">
                            <option selected value="<%= identifierType %>"><%= identifierLabel %></option>
                        </select>
                    </div>
                    <input type="text" class="form-control rounded-0" placeholder="Identifiant" value="<%= identifierValue %>">                 
                    <button type="button" class="btn btn-danger rounded-start-0 btn-remove-identifier">Supprimer</button>
                </div>`
export default identifier_field;