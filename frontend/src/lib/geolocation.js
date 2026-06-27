/**
 * Wraps the browser Geolocation API in a Promise, with clear, specific
 * error messages instead of one generic "couldn't access location" string.
 */
export function getCurrentPosition(
  options = { enableHighAccuracy: false, timeout: 10000, maximumAge: 5 * 60 * 1000 }
) {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Your browser doesn't support location lookup. Try entering a place name instead."));
      return;
    }
    if (!window.isSecureContext && window.location.hostname !== "localhost") {
      reject(
        new Error(
          "Browsers only allow location access over HTTPS (or on localhost). " +
            "Search by name instead, or open this app via https:// / localhost."
        )
      );
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve(pos),
      (geoErr) => reject(new Error(geolocationErrorMessage(geoErr))),
      options
    );
  });
}

export function geolocationErrorMessage(geoErr) {
  switch (geoErr.code) {
    case geoErr.PERMISSION_DENIED:
      return "Location access was denied. Allow it in your browser's site settings (look for a location icon in the address bar), or search by name instead.";
    case geoErr.POSITION_UNAVAILABLE:
      return "Your device couldn't determine its location right now. Try again, or search by name instead.";
    case geoErr.TIMEOUT:
      return "Location lookup took too long. Try again, or search by name instead.";
    default:
      return "Couldn't access your location. Check your browser's location permission, or search by name instead.";
  }
}
