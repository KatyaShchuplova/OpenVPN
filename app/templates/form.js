$(document).ready(function() {

$('form').on('submit', function(event) {

$.ajax({
data: {
unique_name: $('#uniqueNameInput').val()
},
type : 'POST',
url : '/process'

})


event.preventDefault();

});

});