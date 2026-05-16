// File refactored on 04/07/26 @ 6:58 PM by Andre Nunes da Silva
// This is the icon if the truck is open
const openIcon = L.icon({ 
  iconUrl: '/static/images/unsaturated.png',   
  iconSize: [40, 40],                        
  iconAnchor: [20, 40],                   
  popupAnchor: [0, -40],                      
});

// This is the icon if the truck is closed
// It is the gray version of the opened one
const closedIcon = L.icon({
  iconUrl: '/static/images/saturated.png',
  iconSize: [40, 40],
  iconAnchor: [20, 40],
  popupAnchor: [0, -40],
});

//Swaps between light and dark mode by changing the map url the tiles pull from
//Alex Troeschel, 4/11/2026 @ 10:19pm
const modeBtn = document.getElementById("mode-swap");
var isLight = false;

function swapModes() {
  if (isLight == false){
    isLight = true;
    tiles.setUrl('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png').redraw();
    modeBtn.innerHTML = `<i class="fas fa-moon"></i>`;
    document.body.classList.add("light");
    if (document.getElementById("sidePanel").classList.contains("open") == false){
        document.getElementById("togglePanel").classList.add("light");
    }
  }
  else{
    isLight = false;
    tiles.setUrl('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').redraw();
    modeBtn.innerHTML = `<i class="fas fa-sun"></i>`;
    document.body.classList.remove("light");
    if (document.getElementById("sidePanel").classList.contains("open") == false){
        document.getElementById("togglePanel").classList.remove("light");
    }
  }
}
modeBtn.addEventListener('click', swapModes);

window.map = L.map('map', {
  zoomControl: false, // gets rid of zoom buttons (+ -)
  attributionControl: false, // gets rid of the copyright thing on the bottom (leaflet.something)
  zoomAnimation: true, // anim for zoom
  fadeAnimation: true, // anim for to fade zooms
  minZoom: 16,
  maxZoom: 19,
  bounceAtZoomLimits: false
}).setView([39.9566, -75.1899], 16.5);

var tiles = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { // new map distro
    maxZoom: 19,
    // KEEP AT 8 IT IS A LOT HARDER TO USE ON WEAKER DEVICES
    // I SWEAR DO NOT CHANGE IT
    keepBuffer: 8
}).addTo(window.map);

map.locate({
  watch: true, // user's location
  enableHighAccuracy: true, // use's devices max ram or cpu usage (not max but more usage) to grab the most accurate positioning
});

// This is going to be used as a simple lookup table
// It is in this order bc 0 = Monday and 6 = Saturday
const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

// This function basically gets around Monday being 0 and Saturday being the last day
// It allows the hours to be listed from Sunday to Saturday now
// datetime.weekday() returns 0 as Monday, JS returns Monday as 1
// So this converts it when you use it in JS
function jsDayFromPython(pythonDay) {
    return (pythonDay + 1) % 7;
}

//hours is an array of the days of the week and the open / closing times
function buildHoursList(hours) {
    // This gets today's day according to JS
    const today = new Date().getDay(); // JS: Sun=0

    // Sorts it so today appears first
    // Creates a copy of hours so we don't mutate the original
    // a and b are being compared
    // It returns a negative number if a comes before b
    // It returns a positive number if a comes after b
    const sorted = [...hours].sort((a, b) => {
        // If a is today, return -1 and move a up
        // Otherwise return 1 and move a down
        // This allows today to be the top day
        return jsDayFromPython(a.day_of_week) === today ? -1 : 1;
    });
    // Sorted is an array of the days sorted from today onward
    return sorted
        .map(h => {
            // Converts the python weekday into JS weekday
            const jsDay = jsDayFromPython(h.day_of_week);
            // This just returns if today is the day that it says it is
            // Marks the day to bold in the return statement
            const isToday = jsDay === today;

            return `
                <!-- Bolds Today -->
                <li ${isToday ? 'style="font-weight: bold;"' : ""}>
                ${isToday ? "" : ""}
                <span class='day-label'>${days[jsDay]}:</span>
                <span class='open-time'>${h.open_time} – ${h.close_time}</span>
                </li>
            `;
        })
        .join("");
}

window.markers = {};

// Fetch trucks from backend
fetch('/api/food_trucks')
    // Fetch returns something called a promise
    // This basically converts the raw HTTP response into usable JS data
    .then(response => response.json())
    // This then returns actual data
    .then(data => {
        // This loops through every truck
        data.forEach(truck => {

            const truckId = truck.id;

            // This sets the icon to either opened or closed
            const customIcon = truck.is_open ? openIcon : closedIcon;

            // Creates the leaflet marker
            const marker = L.marker([truck.latitude, truck.longitude], {icon: customIcon })
                // This actually adds it to the map
                .addTo(window.map)
                // Creates the popup of the marker
                .bindPopup(`
                     <div class="popup-header">
                        <button class='favorite-button' onclick="toggleFavorite(${truck.id}, this)"> 
                            <i class="${isFavorite(truck.id) ? 'fas' : 'far'} fa-bookmark"></i>
                        </button>
                        <h3>${truck.name}</h3>
                    </div>
                    <p>
                        <strong></strong>
                        <!--If it is opened, do the first option
                        If it is closed, do the second option-->
                        <div class="status-info">
                        ${truck.is_open 
                        ? `<span><span class="status-bulb open"></span> <strong>Open now!</strong> </span>`
                        : `<span><span class="status-bulb closed"></span> <strong>Closed</strong> </span>`
                        }
                        </div>
                    </p>
                    <p><strong></strong></p>
                    <ul class='hours-list'>
                        ${buildHoursList(truck.hours)}
                    </ul>
                    <!--
                    Calls showMenu(), and passes the truck's db
                    -->
                    <div id="rating-anchor-${truck.id}">
                        <div class="rating-section" style="opacity:0.5;font-size:11px;padding:8px 12px;">Loading rating…</div>
                    </div>
                    <div class="popup-button-row">
                    <button class='menu-button' onclick="showMenu(${truck.id})">
                        <i class="fas fa-bars"></i> MENU
                    </button>
                    <button class='track-button' onclick="startTracking(${truck.id}, ${truck.latitude}, ${truck.longitude})">
                        <i class="fas fa-location-arrow"></i> TRACK
                    </button>
                    </div>
                `, {
                    className: 'pin-popup', // class name to customize the pin's contents
                    maxWidth: 250,
                    maxHeight: 450,
                    autoPan: true
                })
                //Added next line by Alex Troeschel on 4/8/2026 @ 8:40PM
                .bindTooltip(`<h3>${truck.name}</h3>`, {direction: 'top', offset: [0, -47], className: 'pin-popup'});
            // Stores the marker in global object
            window.markers[truckId] = marker;
        });
        // Signals sidebar can access markers
        window.trucksLoaded = true;
    });

// Tells the map that whenever someone opens a popup, run this function
map.on('popupopen', function(e) {
    let px = map.project(e.target._popup._latlng);
    px.y -= e.target._popup._container.clientHeight / 2 + 80;
    map.panTo(map.unproject(px), { animate: true });

    const content = e.target._popup._content;
    const match = typeof content === 'string' ? content.match(/rating-anchor-(\d+)/) : null;
    if (match) loadRatingIntoPopup(parseInt(match[1]));
});

function onMapClick(e) {
    //Shows the longitude and latitude when you click somewhere on the map
    //Used to find trucks longitude and latitude on the map easily
    L.popup()
        .setLatLng(e.latlng)
        .setContent("Coordinates: " + e.latlng.toString())
        .openOn(map);
}
//Runs the onMapClick function when you click on the map and not a button or pin
map.on('click', onMapClick);

//Gives an alert when there's an error in location
function onLocationError(e) {
    alert(e.message);
}

map.on('locationerror', onLocationError);

