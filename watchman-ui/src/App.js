import { useState, useEffect } from "react";

function App() {
  const [name, setName] = useState("");
  const [flat, setFlat] = useState("");
  const [vehicle, setVehicle] = useState("");
  const [residents, setResidents] = useState([]);

  // 🔄 Fetch residents
  const fetchResidents = () => {
    fetch("http://localhost:8000/residents")
      .then(res => res.json())
      .then(data => setResidents(data));
  };

  useEffect(() => {
    fetchResidents();
  }, []);

  // ➕ Add resident
  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append("name", name);
    formData.append("flat_number", flat);
    formData.append("vehicle_number", vehicle);

    await fetch("http://localhost:8000/add-resident", {
      method: "POST",
      body: formData,
    });

    setName("");
    setFlat("");
    setVehicle("");

    fetchResidents();
  };

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h1>🚪 Smart Watchman Admin</h1>

      {/* FORM */}
      <h2>Add Resident</h2>
      <form onSubmit={handleSubmit} style={{ marginBottom: "20px" }}>
        <input
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          placeholder="Flat Number"
          value={flat}
          onChange={(e) => setFlat(e.target.value)}
        />
        <input
          placeholder="Vehicle Number"
          value={vehicle}
          onChange={(e) => setVehicle(e.target.value)}
        />
        <button type="submit">Add</button>
      </form>

      {/* LIST */}
      <h2>Residents</h2>
      <ul>
        {residents.map((r) => (
          <li key={r.id}>
            {r.name} | {r.flat_number} | {r.vehicle_number}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;