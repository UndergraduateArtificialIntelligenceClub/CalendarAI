import { useEffect, useState } from "react";
import { API } from "../lib/config";

// Month calendar with mock data: issue #27
function Calendar() {
  const [status, setStatus] = useState("Checking backend...");

  useEffect(() => {
    fetch(`${API}/`)
      .then((res) => res.json())
      .then((data) => setStatus(data.message))
      .catch(() => setStatus("Can't reach the backend. Is it running?"));
  }, []);

  return (
    <main className="flex flex-col items-center gap-2 p-8">
      <h1 className="text-2xl font-bold">Calendar</h1>
      <p>{status}</p>
    </main>
  );
}

export default Calendar;
