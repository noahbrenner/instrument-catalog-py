'use strict';

// Show/hide the navigation menu
(function () {
    var nav = document.getElementById('nav');
    var toggles = document.getElementsByClassName('menu-toggle');

    function toggleMenu(event) {
        nav.classList.toggle('nav-closed');
        event.preventDefault();
    }

    Array.prototype.forEach.call(toggles, function (element) {
        element.addEventListener('click', toggleMenu);
    });

    // Now that the menu can be toggled, disable "no-JS" styling (hide the menu)
    document.querySelector('.nojs').classList.remove('nojs');
})();


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
    var MAX_ALT_INSTRUMENT_NAMES = 10;
    var form = document.forms.instrumentForm;
    var formFields;

    if (!form) {
        return;
    }

    formFields = form.elements;


    /* Enable creation of additional "alternate instrument name" fields */

    function addAltNameElement(event) {
        var listItems = formFields.altNames_fieldset.getElementsByTagName('li');
        var newIndex = listItems.length;
        var newListItem = listItems[0].cloneNode(true);
        var newLabel = newListItem.getElementsByTagName('label')[0]
        var newInput = newListItem.getElementsByTagName('input')[0];
        var deleteBtn = document.createElement('button');

        // Update and reset values of copied elements
        newLabel.setAttribute('for', 'altName' + newIndex);
        newInput.setAttribute('id', 'altName' + newIndex);
        newInput.setAttribute('name', 'alt_name_' + newIndex);
        newInput.value = '';

        // Add a delete button for generated fields (not for the original one)
        deleteBtn.setAttribute('type', 'button');
        deleteBtn.setAttribute('title', 'Delete this name');
        deleteBtn.innerText = 'X';
        deleteBtn.addEventListener('click', function () {
            newListItem.parentNode.removeChild(newListItem);

            if (listItems.length < MAX_ALT_INSTRUMENT_NAMES) {
                formFields.addAltName_btn.disabled = false;
            }
        });

        // Add the new elements to the DOM
        newListItem.appendChild(deleteBtn);
        listItems[0].parentNode.appendChild(newListItem);

        // Disable the "add name" button if we've reached the limit on names
        if (listItems.length >= MAX_ALT_INSTRUMENT_NAMES) {
            formFields.addAltName_btn.disabled = true;
        }

        return newInput;
    }

    // Add functionality to "Add another name" button
    formFields.addAltName_btn.addEventListener('click', function () {
        var newInputElement = addAltNameElement();
        newInputElement.focus();
    });


    /* Prefill instrument-editing form with the current values */

    // `window.instrument` is only (but not always) populated on form pages
    if (window.instrument) {
        // Single value data
        formFields.name.value = window.instrument.name;
        formFields['category' + window.instrument.category_id].checked = true;
        formFields.image.value = window.instrument.image;
        formFields.description.value = window.instrument.description;

        // Multiple value data
        window.instrument.alternate_names.forEach(function (name, index) {
            // Get or create the input element for this index
            var element = formFields['altName' + index] || addAltNameElement();
            element.value = name
        });
    } else {
        // Check whether a category ID was specified in the query string
        var queryCategory = window.location.search.match(/[?&]c=(\d+)/);

        if (queryCategory && formFields['category' + queryCategory[1]]) {
            formFields['category' + categorySearch[1]].checked = true;
        }
    }


    /* Validate form fields */

    // Utility function: ' one    two  ' --> 'one two'
    function collapseSpaces(string) {
        return string
            .trim()
            .replace(/\s+/, ' ');
    }

    // Alternate names do not duplicate earlier names or primary name
    // Use event delegation to catch events triggered by contained `<input>`s
    formFields.altNames_fieldset.addEventListener('input', function (event) {
        var uniqueNames = []; // Instrument names already used in the form
        var i, element, name; // Loop variables

        // Include the primary instrument name to prevent duplicating it
        uniqueNames.push(collapseSpaces(formFields.name.value));

        // Check all elements, up to our preset limit
        for (i = 0; i < MAX_ALT_INSTRUMENT_NAMES; i += 1) {
            element = formFields['altName' + i];

            if (!element) {
                break; // No more names to check
            }

            name = collapseSpaces(element.value);

            if (!name) {
                element.setCustomValidity('');
                continue;
            }

            if (uniqueNames.indexOf(name) === -1) {
                uniqueNames.push(name);
                element.setCustomValidity('');
            } else {
                element.setCustomValidity(
                    'Please enter a name not provided above on this page.'
                );
            }
        }
    });

    // Image URL starts with http(s)
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
