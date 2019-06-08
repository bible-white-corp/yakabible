var qr = false;
var app = {
    // Application Constructor
    initialize: function () {
        document.addEventListener('deviceready', this.onDeviceReady.bind(this), false);
    },

    // deviceready Event Handler
    //
    // Bind any cordova events here. Common events are:
    // 'pause', 'resume', etc.
    onDeviceReady: function () {
        this.receivedEvent('deviceready');
    },

    // Update DOM on a Received Event
    receivedEvent: function (id) {

    }
};

app.initialize();

function displayContents(err, text) {
    if (!err) {
        // Send to server + verif authenticity
        // + better display than alert
        var lines = text.split('\n');
        if (lines.length != 5) {
            alert('Ce QRCode n\'est pas reconnu ' + lines.length);
            if (qr) {
                QRScanner.scan(displayContents);
            }
            return;
        }
        $(".m_obj").hide();
        $("#m_pk").html(lines[2]);
        $("#m_name").html("?");
        $("#m_username").html(lines[0]);
        $("#m_type").html("?");
        $("#m_event").html(lines[1]);
        $("#m_state").html("Inconnu");
        db.events.get(parseInt(lines[1], 10))
            .then(function (event) {
                if (event !== undefined) {
                    $("#m_event").html(event.title);
                }
            })
            .catch(function (err) {
                alert('Erreur : ' + err);
                if (qr) {
                    QRScanner.scan(displayContents);
                }
                return;
            });
        db.tickets.get(parseInt(lines[2], 10))
            .then(function (ticket) {
                if (ticket === undefined || ticket.username !== lines[0]) {
                    $("#ticket_not_found").show();
                } else {
                    $("#ticket_found").show();
                    $("#m_type").html(getType(ticket));
                    $("#m_name").html(ticket.firstname + " " + ticket.lastname);
                    $("#m_state").html(getState(ticket.state));
                    if (ticket.state === 1) {
                        $("#m_check_in").show();
                    }
                    if (ticket.state === 2) {
                        $("#m_check_out").show();
                        $("#m_go_break").show();
                    }
                    if (ticket.state === 3) {
                        $("#m_go_back").show();
                    }
                }
                $("#modal_scan").modal();
                var instance = M.Modal.getInstance($("#modal_scan"));
                instance.open();
            })
            .catch(function (err) {
                alert('Erreur : ' + err);
                if (qr) {
                    QRScanner.scan(displayContents);
                }
                return;
            });
        add_log(text);
    }
}

function show_qr(el) {
    if ($('#test-swipe-2').is(el)) {
        qr = true;
        QRScanner.scan(displayContents);
        QRScanner.show(function (status) {
            console.log(status);
        });
    } else {
        qr = false;
        QRScanner.destroy(function (status) {
            console.log(status);
        });
        if ($('#test-swipe-1').is(el)) {
            refreshEvents();
        }
        else if ($('#test-swipe-3').is(el)) {
            refreshLogs();
        }
    }
}

function download_all() {
    download_events();
    download_tickets();
}

function download_events() {
    $.get("http://yakabible.thetoto.fr/events.json", function (data) {
        add_events(data);
    });
}

function download_tickets() {
    $.get("http://yakabible.thetoto.fr/tickets.json", function (data) {
        add_tickets(data);
    });
}

function update_status(new_state) {
    t = $("#m_pk").html();
    $.get("http://yakabible.thetoto.fr/ticket/" + t + "/update?new_state=" + new_state, function() {
        db.tickets.get(parseInt(t, 10))
            .then(function (ticket) {
                if (ticket === undefined) {
                    M.toast({html: 'Erreur BDD !'});
                } else {
                    ticket.state = new_state;
                    db.tickets.put(ticket);
                    M.toast({html: 'Envoyé au server !'});
                }
            })
            .catch(function (err) {
                M.toast({html: 'Erreur BDD !'});
            });
    }).fail(function() {
        M.toast({html: 'Server non joignable !'});
    });
    if (qr) {
        QRScanner.scan(displayContents);
    }
}

$("#m_check_in").click(function () {
    update_status(2);
});
$("#m_check_out").click(function () {
    update_status(0);
});
$("#m_go_break").click(function () {
    update_status(3);
});
$("#m_go_back").click(function () {
    update_status(2);
});
$("#m_cancel").click(function () {
    if (qr) {
        QRScanner.scan(displayContents);
    }
});

var instance = M.Tabs.init($('.tabs'), {onShow: show_qr});
$('.collapsible').collapsible();