import { useState } from "react";

function GuestForm() {
  const [name, setName] = useState("");
  const [plate, setPlate] = useState("");
  const [flat, setFlat] = useState("");
  const [purpose, setPurpose] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    await fetch("http://localhost:8000/guest/request", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name,
        vehicle_plate: plate,
        flat_no: flat,
        purpose,
      }),
    });

    alert("Request Sent!");
  };

  return (
    <div style={{ padding: "30px" }}>
      <h2>🚗 Guest Entry Request</h2>

      <form onSubmit={handleSubmit}>
        <input placeholder="Your Name" onChange={e => setName(e.target.value)} />
        <input placeholder="Vehicle Number" onChange={e => setPlate(e.target.value)} />
        <input placeholder="Flat Number" onChange={e => setFlat(e.target.value)} />
        <input placeholder="Purpose" onChange={e => setPurpose(e.target.value)} />

        <button type="submit">Submit Request</button>
      </form>
    </div>
  );
}

export default GuestForm;