'use strict';

// Add "back" functionality when the page has an element with id="back-link"
// Thanks to https://stackoverflow.com/a/46163215 for inspiration
(function () {
    var backLink = document.getElementById('backLink');
    if (backLink && window.history.length > 1) {
        // Show the URL that the user would go back to, if possible (we might
        // not have access to the referrer even if there is a browser history)
        backLink.href = document.referrer || '#';

        // Go back using the history instead of following the link forward
        backLink.addEventListener('click', function (event) {
            event.preventDefault();
            window.history.back();
        });
    }
})();


// Instrument form functionality
(function () {
    var form = document.forms.instrumentForm;
    var formFields;

    if (!form) {
        return;
    }

    formFields = form.elements;

    // Prefill instrument-editing form with the current values
    // (`window.instrument` is only populated on the "edit instrument" page)
    if (window.instrument) {
        formFields.name.value = window.instrument.name;
        formFields.altNames.value = window.instrument.alternate_names.join('\n');
        formFields['category' + window.instrument.category_id].checked = true;
        formFields.image.value = window.instrument.image;
        formFields.description.value = window.instrument.description;
    }

    // Display custom message for invalid form input
    formFields.image.addEventListener('input', function (event) {
        var element = event.target;

        if (element.validity.typeMismatch || element.validity.patternMismatch) {
            element.setCustomValidity(
                'Please enter a URL starting with "https" or "http".'
            );
        } else {
            element.setCustomValidity('');
        }
    });
})();
