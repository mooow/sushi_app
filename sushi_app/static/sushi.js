function normalize_day(date) {
        var day = date.getDay();
        return day == 0 ? 7 : day;
}

function _submit() {
        var value = [];
        var idx = 0;
        $( "button.active" ).each(function( index ) {
          value[idx++] = $(this).text();
        });

        value = JSON.stringify(value);

        $('input#days').attr('value', value);
        $('#form').submit();
}

function select_all() {
        $( "button.day" ).each(function( index ) {
          $(this).addClass("active");
        });
}

function deselect_all() {
        $( "button.day" ).each(function( index ) {
          $(this).removeClass("active");
        });
}

function invert_selection() {
        $( "button.day" ).each(function( index ) {
          $(this).toggleClass("active");
        });
}

function calendar(year, month) {
        var cal = $('#calendar');
        var giorni = ["", "L", "Ma", "Me", "G", "V", "S", "D"];
        var mesi = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"];
        // Title
        $("#title").text("Sushi " + mesi[month] + " " + year);

        // Header row
        var row = $("<div class=row >");
        for(var i = 1; i <= 7; i++) {
            var div = $('<div class="col text-primary font-weight-bold">');
            div.text(giorni[i]);
            row.append(div);
        }
        cal.append(row);

        // First row
        var day = 1;
        var date = new Date(year, month, day);
        weekday = normalize_day(date);

        var row = $("<div class=row >");
        for (var i = 1; i <= 7; i++) {
                var div = $('<button data-toggle="button" type="button" class="btn btn-light col" >');
                //div.text( i < weekday ? "" : day++ );
                if (i >= weekday) {
                        div.text(day++);
                        div.attr("name", day);
                        div.addClass("day");
                } else {
                        div.addClass("disabled");
                }
                row.append(div);
                date = new Date(year, month, day);
        }
        cal.append(row);

        while (date.getMonth() == month) {
                var row = $("<div class=row >");
                for (var i = 1; i <= 7; i++) {
                        var div = $('<button data-toggle="button" type="button" class="btn btn-light col" >');
                        //div.text(date.getMonth() == month ? day++ : "");
                        if (date.getMonth() == month) {
                                div.text(day++);
                                div.attr("name", day);
                                div.addClass("day");
                        } else {
                                div.addClass("disabled");
                        }
                        row.append(div);
                        date = new Date(year, month, day);
                }
                cal.append(row);
        }
}
