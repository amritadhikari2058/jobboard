/* JobBoard progressive enhancement.
   Everything here is optional: the pages work without JavaScript, this only
   removes friction. */
(function () {
    "use strict";

    /* ---------------------------------------------------------------------
       Auto-dismiss
       Only alerts marked data-jb-autodismiss (success and info) are removed.
       Warnings and errors stay until the visitor dismisses them, because
       silently deleting a message the visitor still needs is worse than one
       that lingers.
       --------------------------------------------------------------------- */
    document.querySelectorAll('[data-jb-autodismiss="true"]').forEach(function (alert) {
        window.setTimeout(function () {
            window.bootstrap.Alert.getOrCreateInstance(alert).close();
        }, 6000);
    });

    /* ---------------------------------------------------------------------
       Confirmations
       Any form carrying data-confirm asks before submitting, so destructive
       buttons on list pages do not need a separate page.
       --------------------------------------------------------------------- */
    document.addEventListener("submit", function (event) {
        var message = event.target.getAttribute("data-confirm");

        if (message && !window.confirm(message)) {
            event.preventDefault();
        }
    });

    /* ---------------------------------------------------------------------
       Dynamic inline formsets
       Adds a row built from the <template data-formset-empty> clone and
       re-indexes the TOTAL_FORMS counter, which is what the server reads.
       --------------------------------------------------------------------- */
    document.querySelectorAll("[data-formset]").forEach(function (form) {
        var addButton = form.querySelector("[data-formset-add]");
        var rows = form.querySelector("[data-formset-rows]");
        var emptyTemplate = form.querySelector("[data-formset-empty]");
        var totalForms = form.querySelector("[id$='-TOTAL_FORMS']");

        if (!addButton || !rows || !emptyTemplate || !totalForms) {
            return;
        }

        addButton.addEventListener("click", function () {
            var nextIndex = parseInt(totalForms.value, 10) || 0;
            var markup = emptyTemplate.innerHTML.replace(/__prefix__/g, nextIndex);

            rows.insertAdjacentHTML("beforeend", markup);
            totalForms.value = nextIndex + 1;
            addButton.focus();
        });
    });
})();
