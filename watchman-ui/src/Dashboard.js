import { useEffect, useState } from "react";

function Dashboard() {
  // 🔹 Resident state
  const [name, setName] = useState("");
  const [flat, setFlat] = useState("");
  const [vehicle, setVehicle] = useState("");
  const [residents, setResidents] = useState([]);

  // 🔹 Guest state
  const [guests, setGuests] = useState([]);

  // =========================
  // FETCH DATA
  // =========================

  const fetchResidents = () => {
    fetch("http://localhost:8000/residents")
      .then(res => res.json())
      .then(data => setResidents(data));
  };

  const fetchGuests = () => {
    fetch("http://localhost:8000/guest?approved=false")
      .then(res => res.json())
      .then(data => setGuests(data));
  };

  useEffect(() => {
    fetchResidents();
    fetchGuests();
  }, []);

  // =========================
  // ADD RESIDENT
  // =========================

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

  // =========================
  // GUEST ACTIONS
  // =========================

  const approve = async (id) => {
    await fetch(`http://localhost:8000/guest/approve/${id}`, {
      method: "POST",
    });
    fetchGuests();
  };

  const deny = async (id) => {
    await fetch(`http://localhost:8000/guest/deny/${id}`, {
      method: "POST",
    });
    fetchGuests();
  };

  // =========================
  // UI
  // =========================

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h1>🏠 Smart Watchman Dashboard</h1>

      {/* ================= ADD RESIDENT ================= */}
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

      {/* ================= RESIDENT LIST ================= */}
      <h2>Residents</h2>
      <ul>
        {residents.map((r) => (
          <li key={r.id}>
            {r.name} | {r.flat_number} | {r.vehicle_number}
          </li>
        ))}
      </ul>

      {/* ================= GUEST REQUESTS ================= */}
      <h2>Pending Guest Requests</h2>

      {guests.length === 0 && <p>No pending requests</p>}

      {guests.map((g) => (
        <div
          key={g.id}
          style={{
            border: "1px solid black",
            margin: "10px",
            padding: "10px",
          }}
        >
          <p><b>Name:</b> {g.guest_name}</p>
          <p><b>Vehicle:</b> {g.vehicle_plate}</p>
          <p><b>Flat:</b> {g.flat_no}</p>
          <p><b>Purpose:</b> {g.purpose}</p>

          <button onClick={() => approve(g.id)}>✅ Approve</button>
          <button onClick={() => deny(g.id)}>❌ Deny</button>
        </div>
      ))}
    </div>
  );
}

export default Dashboard;