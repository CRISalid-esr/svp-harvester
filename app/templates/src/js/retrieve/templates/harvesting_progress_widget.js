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
                                    <i tabindex=0 class="bi bi-x-circle float-end" data-bs-toggle="popover" data-bs-title="<%= error.name %>" data-bs-content="<%= error.message %>" data-bs-trigger="focus"></i>
                                <% } %>                            
                            </div>
                        </li>`;
export default harvesting_progress_widget;
