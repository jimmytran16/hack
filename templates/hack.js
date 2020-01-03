$(document).ready(function () {
    $('#dtVerticalScrollExample').DataTable({
    "scrollY": "200px",
    "scrollCollapse": true,
    });
    $('.dataTables_length').addClass('bs-select');
    });




// function validateForm() {
//     var un = document.loginform.usr.value;
//     var pw = document.loginform.pword.value;
//     var username = "username"; 
//     var password = "password";
//     var check = getUsers();
//     return check;
// }

// // using node to connect to database

// var mysql = require('mysql');

// var con = mysql.createConnection({
//   host: "localhost",
//   user: "yourusername",
//   password: "yourpassword"
// });

// con.connect(function(err) {
//   if (err) throw err;
//   console.log("Connected!");
// });