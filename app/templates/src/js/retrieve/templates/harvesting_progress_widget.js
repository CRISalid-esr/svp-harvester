const harvesting_progress_widget = `<li class="list-group-item">
                            <%= harvester %>
                            <div class="clearfix">
                                <strong role="status" class="float-start"><%= state %></strong>
                                <% if(state=="running"){ %>
                                    <div class="spinner-border spinner-border-sm ms-auto float-end" aria-hidden="true"></div>
                                 <% } else if(state=="completed") { %>  
                                    <i class="bi bi-check-circle float-end"></i>
                                <% } else if(state=="failed") { %>
                                    <i class="bi bi-x-circle float-end"></i>
                                <% } %>                            
                            </div>
                        </li>`
export default harvesting_progress_widget;