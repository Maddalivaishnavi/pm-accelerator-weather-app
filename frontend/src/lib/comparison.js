/**
 * Pure logic for comparing two already-fetched WeatherLookupResponse
 * objects. No network calls here — this just turns two data sets into
 * plain-language, decision-useful differences.
 */
export function buildComparisonTips(home, dest, homeName, destName) {
  const tips = [];

  const homeTemp = home.current?.temperature_c;
  const destTemp = dest.current?.temperature_c;
  if (homeTemp != null && destTemp != null) {
    const diff = destTemp - homeTemp;
    if (Math.abs(diff) >= 5) {
      tips.push(
        `${destName} is about ${Math.abs(Math.round(diff))}°C ${diff > 0 ? "warmer" : "colder"} than ${homeName} — ` +
          `${diff > 0 ? "pack lighter clothing" : "bring an extra layer"}.`
      );
    }
  }

  const homeRain = home.forecast?.[0]?.precipitation_probability ?? 0;
  const destRain = dest.forecast?.[0]?.precipitation_probability ?? 0;
  if (destRain - homeRain >= 20) {
    tips.push(
      `Rain is notably more likely at ${destName} today (${Math.round(destRain)}% vs ${Math.round(homeRain)}%) — pack a rain jacket.`
    );
  } else if (homeRain - destRain >= 20) {
    tips.push(`${destName} looks drier than ${homeName} today (${Math.round(destRain)}% vs ${Math.round(homeRain)}% rain chance).`);
  }

  const homeAqi = home.air_quality?.us_aqi;
  const destAqi = dest.air_quality?.us_aqi;
  if (homeAqi != null && destAqi != null && Math.abs(destAqi - homeAqi) >= 30) {
    tips.push(
      `Air quality is noticeably ${destAqi > homeAqi ? "worse" : "better"} at ${destName} ` +
        `(AQI ${Math.round(destAqi)} vs ${Math.round(homeAqi)}).`
    );
  }

  const homeWind = home.current?.wind_speed_kmh;
  const destWind = dest.current?.wind_speed_kmh;
  if (homeWind != null && destWind != null && destWind - homeWind >= 15) {
    tips.push(`${destName} is windier right now — secure or skip anything that doesn't travel well in wind.`);
  }

  if (tips.length === 0) {
    tips.push(`Conditions are fairly similar between ${homeName} and ${destName} right now.`);
  }

  return tips;
}
