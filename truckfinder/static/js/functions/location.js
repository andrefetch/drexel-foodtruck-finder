// File refactored on 04/07/26 @ 6:58 PM by Andre Nunes da Silva
var slider = document.getElementById("distance");
var lastDist = 100;
let userMarker, accuracyCircle;

window.SLIDER_METERS_PER_UNIT = 5.3645;

window.sliderRadiusMeters = function () {
    return Number(slider.value) * window.SLIDER_METERS_PER_UNIT;
};

window.sliderShowsAll = function () {
    return Number(slider.value) === 100;
};

function updateSliderFill() {
    const min = Number(slider.min) || 0;
    const max = Number(slider.max) || 100;
    const pct = ((Number(slider.value) - min) / (max - min)) * 100;
    slider.style.setProperty("--slider-fill", pct + "%");
}

function updateDistanceLabel() {
    const label = document.getElementById("distance-label");
    if (!label) return;
    if (window.sliderShowsAll()) {
        label.textContent = "All trucks";
        return;
    }
    const feet = Math.round(window.sliderRadiusMeters() * 3.28084);
    label.textContent = feet < 1000
        ? `Within ${feet} ft`
        : `Within ${(feet / 5280).toFixed(2)} mi`;
}

function setMarkerInRange(marker, inRange) {
    marker.setOpacity(inRange ? 1 : 0);

    const markerElement = marker.getElement && marker.getElement();
    if (markerElement) markerElement.style.pointerEvents = inRange ? "" : "none";
    if (!inRange && marker.isPopupOpen()) marker.closePopup();
}

function applyDistanceToMarkers() {
    if (!window.trucksLoaded || !window.userPos) return;

    const trucks = window.trucks || [];
    trucks.forEach(truck => {
        const marker = window.markers && window.markers[truck.id];
        if (!marker) return;

        const inRange = window.sliderShowsAll() ||
            L.latLng(window.userPos).distanceTo([truck.latitude, truck.longitude]) < window.sliderRadiusMeters();
        setMarkerInRange(marker, inRange);
    });
}

updateSliderFill();
updateDistanceLabel();

//Runs when the users location is checked
map.on('locationfound', (e) => {
    const radius = e.accuracy / 2;
    //Creates a pin for the user if not already there
    window.userPos = [e.latitude, e.longitude];
    if (!userMarker) {
        userMarker = L.marker(e.latlng).addTo(map);
        accuracyCircle = L.circle(e.latlng, radius).addTo(map);
    } else {
        //Updates the user's location if already found
        userMarker.setLatLng(e.latlng);
        accuracyCircle.setLatLng(e.latlng);
        accuracyCircle.setRadius(radius);
        //If routing, check waypoints again and remove unnecessary ones
        if (routingControl) {
            const currentWaypoints = routingControl.getWaypoints();
            routingControl.setWaypoints([
                e.latlng,
                currentWaypoints[1].latLng
            ]);
        }
        lastDist = Number(slider.value);
    }

    applyDistanceToMarkers();

    //If routing to a truck, check waypoints again only if
    //far from your last position
    if (routingControl && trackedTruckId !== null) {
        const currentWaypoints = routingControl.getWaypoints();
        const oldPos = currentWaypoints[0].latLng;
        if (oldPos.distanceTo(e.latlng) > 5) {
            routingControl.setWaypoints([
                e.latlng,
                currentWaypoints[1].latLng
            ]);
        }
    }
});

slider.oninput = function() {
    updateSliderFill();
    updateDistanceLabel();
    if (typeof window.applyFilters === "function") window.applyFilters();
    applyDistanceToMarkers();
};
