//
// Define database
//
var db = new Dexie("yakabible");
db.version(1).stores({
    logs: '_id',
    events: '_id',
    tickets: '_id'
});

//
// Query Database
//

db.open().then(refreshAll);

function refreshAll() {
    refreshLogs();
    refreshEvents();
}

function refreshLogs() {
    return db.logs.toArray()
        .then(renderAllLogs);
}

function refreshEvents() {
    return db.events.toArray()
        .then(renderAllEvents);
}

function refreshTickets() {
    return db.tickets.toArray()
        .then(renderAllTickets);
}

function renderAllLogs(logs) {
    el = $("#logs_body");
    el.html('');
    logs.forEach(function (log) {
        el.append(logToHtml(log));
    });
}

function renderAllEvents(events) {
    el = $("#list_event");
    el.html('');
    events.forEach(function (event) {
        el.append(eventToHtml(event));
    });
    refreshTickets();
}

function renderAllTickets(tickets) {
    tickets.forEach(function (ticket) {
        $("#event_" + ticket.event_id).html('');
    });
    tickets.forEach(function (ticket) {
        $("#event_" + ticket.event_id).append(ticketToHtml(ticket));
    });
    $(".click-edit").click(function () {
        id = $(this).attr('value');
        console.log("edit " + id);
        db.tickets.get(parseInt(id, 10)).then(function (tick) {
            str = tick.username + "\n" + tick.event_id + "\n" + tick._id + "\n" + "email@nope" + "\n";
            displayContents(null, str);
        });
    });
}

function logToHtml(log) {
    return "<tr><td>" + log.text + "</td></tr>";
}

function getState(state) {
    if (state === 0) {
        return "Expiré";
    }
    if (state === 1) {
        return "Non utilisé";
    }
    if (state === 2) {
        return "Utilisé";
    }
    if (state === 3) {
        return "En pause";
    }
    return "Undefined"
}

function ticket_to_type_s(ticket) {
    if (ticket.category)
        return "S";
    else if (ticket.ionis)
        return "I";
    else
        return "E";
}
function getType(ticket) {
    if (ticket.category)
        return "Staff";
    else if (ticket.ionis)
        return "Interne";
    else
        return "Externe";
}

function ticketToHtml(ticket) {
    return "<li class=\"collection-item\">\n" +
        "      <span class=\"title\">" + ticket_to_type_s(ticket) + " : " + ticket.firstname + " " + ticket.lastname + "</span>\n" +
        "      <a value=\"" + ticket._id + "\" class=\"click-edit secondary-content\"><i class=\"material-icons\">border_color</i></a>\n" +
        "      <span style='margin-right: 10px;' class=\"secondary-content\">" + getState(ticket.state) + "</span>\n" +
        "    </li>";
}

function eventToHtml(event) {
    return '<li><div class="collapsible-header">'
        + event.title
        + '</div><div class="collapsible-body"><ul class="collection" id="event_'
        + event._id
        + '"></div></div></li>';
}

function add_log(text) {
    db.logs.put({ text: text, _id: String(Date.now()) })
        .then(refreshLogs);
}

function add_events(objs) {
    db.events.clear();
    $.each(objs, function (index, value) {
        db.events.put({ title: value.title, _id: value.id })
            .then(refreshEvents);
    });
}

function add_tickets(objs) {
    db.tickets.clear();
    $.each(objs, function (index, value) {
        db.tickets.put({ firstname: value.firstname, lastname: value.lastname, username: value.username, event_id: value.event, state: value.state, category: value.category, ionis: value.ionis, _id: value.id })
            .then(refreshTickets);
    });
}

function clear_all() {
    db.tickets.clear();
    db.events.clear();
    db.logs.clear();
    refreshAll();
}