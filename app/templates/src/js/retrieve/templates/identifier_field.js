const identifier_field = `<div class="input-group mt-3 mb-3 identifier-field-container">
                    <div style="width: max-content;">
                        <select disabled class="form-select rounded-end-0 identifier-control-select" aria-label="Example select with button addon">
                            <option selected value="<%= identifierType %>"><%= identifierLabel %></option>
                        </select>
                    </div>
                    <input type="text" class="form-control rounded-0 identifier-control-input" disabled value="<%= identifierValue %>">                 
                    <button type="button" class="btn btn-success rounded-start-0  rounded-end-0 btn-validate-identifier d-none"><i class="bi bi-check-circle"></i></button>                  
                    <button type="button" class="btn btn-warning rounded-start-0  rounded-end-0 btn-edit-identifier"><i class="bi bi-pencil"></i></button>                  
                    <button type="button" class="btn btn-danger rounded-start-0 btn-remove-identifier"><i class="bi bi-x-circle"></i></button>                  
                </div>`
export default identifier_field;