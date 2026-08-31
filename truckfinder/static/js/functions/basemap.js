// Author: Andre Nunes da Silva, 08/30/26
// Feature: Shared CARTO basemap tile URLs — one place for the API key

// The key is injected by the page (see layout.html) from the CARTO_API_KEY env
// var, so it never lands in this file or in git. When it is missing the tiles
// still load, just with CARTO's watermark on them.
const CARTO_KEY = window.CARTO_KEY || "";

// Builds a CARTO raster tile URL for a style, e.g. "rastertiles/voyager" or "dark_all"
function cartoTileUrl(style) {
    const url = `https://{s}.basemaps.cartocdn.com/${style}/{z}/{x}/{y}{r}.png`;
    return CARTO_KEY ? `${url}?key=${CARTO_KEY}` : url;
}
