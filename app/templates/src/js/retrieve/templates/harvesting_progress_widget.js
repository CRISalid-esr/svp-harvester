const harvesting_progress_widget = `<li class="list-group-item">
                            <%= harvester %>
                            <div class="clearfix">
                                <strong role="status" class="float-start"><%= state %> (<%= reference_events.length %> results)</strong>
                                <% if(state=="running"){ %>
                                    <div class="spinner-border spinner-border-sm ms-auto float-end" aria-hidden="true"></div>
                                <% } else if(state=="completed") { %>  
                                    <i class="bi bi-check-circle float-end"></i>
                                <% } else if(state=="canceled") { %>  
                                    <i class="bi bi-slash-circle float-end"></i>
                                <% } else if(state=="failed") { %>
                                    <i tabindex=0 
                                         class="bi bi-x-circle float-end" 
                                         data-bs-toggle="popover"
                                         data-bs-title="Errors:" 
                                         data-bs-trigger="focus"
                                         data-bs-html="true"
                                         data-bs-sanitize="false"
                                         data-bs-content='
                                            <div class="popover fs-6" role="tooltip"><div class="popover-body">
                                                <% for (const er of error) { %>
                                                    <h6><%= er.name %></h6>
                                                    <p><%= er.message %></p>
                                                <% } %>
                                            </div></div>'
                                    ></i>
                                <% } %>                            
                            </div>
                            <div id="popover-content" class="d-none">
                                <h1>Hola</h1>
                            </div>
                        </li>`;
export default harvesting_progress_widget;
