var db = new Dexie("TestDatabase3");

db.version(1).stores({
  user: "id,externalId,name",
  buttons: "++id,displayName,icon,size,color"
});

db.open();

db.user.get(100).then(function (user) {
  alert('Found ' + user.name);
}).catch( function(error) {
    alert("Error: " + error);
});