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
