function parseTimeToMinutes(value) {
  if (!value || !value.includes(":")) return 0;
  const [hours, minutes] = value.split(":").map(Number);
  return hours * 60 + minutes;
}

function formatMinutes(total) {
  const minutesInDay = 24 * 60;
  const normalized = ((total % minutesInDay) + minutesInDay) % minutesInDay;
  const hours24 = Math.floor(normalized / 60);
  const minutes = normalized % 60;
  const suffix = hours24 >= 12 ? "pm" : "am";
  const hours12 = hours24 % 12 || 12;
  return `${hours12}:${String(minutes).padStart(2, "0")} ${suffix}`;
}

function formatDuration(min, max = min) {
  const formatOne = (value) => {
    const hours = Math.floor(value / 60);
    const minutes = value % 60;
    if (!hours) return `${minutes} min`;
    if (!minutes) return `${hours}h`;
    return `${hours}h ${minutes}`;
  };
  return min === max ? formatOne(min) : `${formatOne(min)}–${formatOne(max)}`;
}

function initRoutePlanner(planner) {
  const departureInput = planner.querySelector("[data-planner-departure]");
  const selectedOutput = planner.querySelector("[data-planner-selected]");
  const finishOutput = planner.querySelector("[data-planner-finish]");
  const durationOutput = planner.querySelector("[data-planner-duration]");
  const warningOutput = planner.querySelector("[data-planner-warning]");
  const statusOutput = planner.querySelector("[data-planner-status]");
  const baseMin = Number(planner.dataset.baseMin || 0);
  const baseMax = Number(planner.dataset.baseMax || baseMin);
  const warningAfter = Number(planner.dataset.warningAfter || 0);
  const warningText = planner.dataset.warningText || "";

  function selectedItems() {
    return Array.from(planner.querySelectorAll("[data-planner-option]:checked"));
  }

  function calculate() {
    const departure = parseTimeToMinutes(departureInput.value);
    let extraMin = 0;
    let extraMax = 0;
    for (const item of selectedItems()) {
      extraMin += Number(item.dataset.min || 0);
      extraMax += Number(item.dataset.max || item.dataset.min || 0);
    }

    const totalMin = baseMin + extraMin;
    const totalMax = baseMax + extraMax;
    const finishMin = departure + totalMin;
    const finishMax = departure + totalMax;

    selectedOutput.textContent = formatDuration(extraMin, extraMax);
    durationOutput.textContent = formatDuration(totalMin, totalMax);
    finishOutput.textContent = finishMin === finishMax
      ? formatMinutes(finishMin)
      : `${formatMinutes(finishMin)}–${formatMinutes(finishMax)}`;

    if (warningOutput) {
      const shouldWarn = warningAfter && finishMax > warningAfter;
      warningOutput.hidden = !shouldWarn;
      warningOutput.textContent = shouldWarn ? warningText : "";
    }

    if (statusOutput) {
      if (totalMax < 8 * 60) {
        statusOutput.textContent = "Comfortable day";
        statusOutput.className = "planner-status status-comfortable";
      } else if (totalMax <= 10 * 60) {
        statusOutput.textContent = "Long day";
        statusOutput.className = "planner-status status-long";
      } else {
        statusOutput.textContent = "Very long day — consider dropping an option";
        statusOutput.className = "planner-status status-very-long";
      }
    }
  }

  planner.addEventListener("input", calculate);
  calculate();
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-route-planner]").forEach(initRoutePlanner);
});
