import { useEffect, useState } from "react";
import { API, APP_NAME } from "./lib/config";

function App() {
  const [status, setStatus] = useState("Checking backend...");

  useEffect(() => {
    fetch(`${API}/`)
      .then((res) => res.json())
      .then((data) => setStatus(data.message))
      .catch(() => setStatus("Can't reach the backend. Is it running?"));
  }, []);

  return (
    <main>
      <h1>{APP_NAME}</h1>
      <p>{status}</p>
    </main>
  );
}

export default App;