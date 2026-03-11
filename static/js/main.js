/* =============================
UPLOAD CSV
============================= */

function uploadFile(){

let fileInput=document.getElementById('file-input');
let status=document.getElementById('upload-status');

if(fileInput.files.length===0){
alert('Select a CSV file');
return;
}

let formData=new FormData();
formData.append('file',fileInput.files[0]);

fetch('/upload',{
method:'POST',
body:formData
})

.then(res=>res.json())

.then(data=>{
status.innerText=data.error || `Uploaded. ${data.genera_count} taxa found.`;
});

}


/* =============================
FETCH GBIF DATA
============================= */

function fetchGbifData(){

let status=document.getElementById('fetch-status');

let bounds=leafletMap.getBounds();

let bbox={
lat_min:bounds.getSouth(),
lat_max:bounds.getNorth(),
lon_min:bounds.getWest(),
lon_max:bounds.getEast()
};

fetch('/fetch_gbif',{
method:'POST',
headers:{'Content-Type':'application/json'},
body:JSON.stringify(bbox)
})

.then(res=>res.json())

.then(data=>{
status.innerText=data.error || data.status;

if(!data.error){
loadLeafletPoints();
}

});

}


/* =============================
LEAFLET MAP
============================= */

let leafletMap=L.map('leaflet-map').setView([31.5,77.8],8);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
attribution:'© OpenStreetMap contributors'
}).addTo(leafletMap);

let markerLayer=L.layerGroup().addTo(leafletMap);


/* =============================
LOAD MAP POINTS
============================= */

function loadLeafletPoints(){

fetch('/get_points')

.then(res=>res.json())

.then(data=>{

markerLayer.clearLayers();

if(data.length===0){
alert("No data available");
return;
}

data.forEach(point=>{

let marker=L.circleMarker(
[point.lat,point.lon],
{
radius:5,
color:"green",
fillOpacity:0.7
}
).bindPopup(
`<b>Genus:</b> ${point.genus || "NA"}<br>
<b>Species:</b> ${point.species || "NA"}<br>
<b>Source:</b> ${point.source || "NA"}`
);

markerLayer.addLayer(marker);

});

let group=new L.featureGroup(markerLayer.getLayers());
leafletMap.fitBounds(group.getBounds());

});

}


/* =============================
CLIMATE CALCULATION
============================= */

function calculateClimate(){

fetch('/calculate_climate')

.then(res => res.json())

.then(data => {

let tableBody=document.querySelector("#climate-table tbody");

tableBody.innerHTML="";

if(data.length===0){
alert("No climate data returned");
return;
}

data.forEach(row => {

console.log("Climate result:",row.result);

let tr=document.createElement("tr");

tr.innerHTML=`
<td>${row.lat}</td>
<td>${row.lon}</td>
<td>${row.species || "NA"}</td>
<td><pre>${row.result}</pre></td>
`;

tableBody.appendChild(tr);

});

});

}