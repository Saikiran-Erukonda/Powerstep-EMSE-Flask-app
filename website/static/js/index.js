$(document).ready(function () {
    initTooltips();
    initPopovers();
    initFormValidation();
    autoDismissAlerts();
    initDatePickers();
    initPrintButtons();
});

// ✅ Initialize Bootstrap tooltips
function initTooltips() {
    if ($('[data-toggle="tooltip"]').length) {
        $('[data-toggle="tooltip"]').tooltip();
    }
}

// ✅ Initialize Bootstrap popovers
function initPopovers() {
    if ($('[data-toggle="popover"]').length) {
        $('[data-toggle="popover"]').popover();
    }
}

// ✅ Form validation using Bootstrap classes
function initFormValidation() {
    $('form.needs-validation').on('submit', function (event) {
        if (this.checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
        }
        $(this).addClass('was-validated');
    });
}

// ✅ Auto-dismiss alerts after 5 seconds
function autoDismissAlerts() {
    setTimeout(function () {
        $('.alert').alert('close');
    }, 5000);
}

// ✅ Initialize datepicker if available
function initDatePickers() {
    if ($.fn.datepicker) {
        $('.datepicker').datepicker({
            format: 'yyyy-mm-dd',
            autoclose: true,
            todayHighlight: true
        });
    } else {
        console.warn("Datepicker plugin not loaded.");
    }
}

// ✅ Print salary slip or any printable section
function initPrintButtons() {
    $('.print-slip').click(function () {
        window.print(); // You can target a specific div if needed
    });
}

// ✅ Confirm before deleting
function confirmDelete() {
    return confirm('Are you sure you want to delete this record?');
}

function printSection(selector) {
    var content = document.querySelector(selector).innerHTML;
    var printWindow = window.open('', '', 'height=600,width=800');
    printWindow.document.write('<html><head><title>Print</title></head><body>');
    printWindow.document.write(content);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.print();
}
