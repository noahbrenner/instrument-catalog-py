'use strict';

// Add "back" functionality if the current page has a link with id 'back-link'
(function () {
    // Thanks for inspiration goes to: https://stackoverflow.com/a/46163215
    var backLink = document.getElementById('backLink');
    if (backLink && window.history.length > 1) {
        // Show the URL that the user would go back to
        // We might not have a referrer if the user manually typed in the URL
        backLink.href = document.referrer || '#';

        // Go back using the history instead of following the link forward
        backLink.onclick = function (event) {
            event.preventDefault();
            window.history.back();
        };
    }
})();


// Prefill instrument-editing form with the current values
(function () {
    if (window.instrument && document.forms.instrumentForm) {
        var instrument = window.instrument;
        var fields = document.forms.instrumentForm.elements;

        // Set form values
        fields.name.value = instrument.name;
        fields.altNames.value = instrument.alternate_names.join('\n');
        fields['category' + instrument.category_id].checked = true;
        fields.image.value = instrument.image;
        fields.description.value = instrument.description;
    }
})();


// Display custom message for invalid form input
(function () {
    if (document.forms.instrumentForm) {
        var imageElement = document.forms.instrumentForm.elements.image;
        var validity = imageElement.validity;
        var errMessage = 'Please enter a URL starting with "https" or "http".';

        imageElement.addEventListener('input', function (event) {
            if (validity.typeMismatch || validity.patternMismatch) {
                imageElement.setCustomValidity(errMessage);
            } else {
                imageElement.setCustomValidity('');
            }
        });
    }
})();
