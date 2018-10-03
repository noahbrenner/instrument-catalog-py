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


    // Enable creation of additional "alternate instrument name" fields

    function addAltNameElement(event) {
        var MAX_ALT_NAMES = 10;
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

            if (listItems.length < MAX_ALT_NAMES) {
                formFields.addAltName_btn.disabled = false;
            }
        });

        // Add the new elements to the DOM
        newListItem.appendChild(deleteBtn);
        listItems[0].parentNode.appendChild(newListItem);

        // Disable the "add name" button if we've reached MAX_ALT_NAMES
        if (listItems.length >= MAX_ALT_NAMES) {
            formFields.addAltName_btn.disabled = true;
        }

        return newInput;
    }

    // Add functionality to "Add another name" button
    formFields.addAltName_btn.addEventListener('click', function () {
        var newInputElement = addAltNameElement();
        newInputElement.focus();
    });


    // Prefill instrument-editing form with the current values
    // (`window.instrument` is only populated on the "edit instrument" page)
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
