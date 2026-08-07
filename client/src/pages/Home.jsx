import React, { useEffect, useState } from "react";
import { getHackathons } from "../services/api";
import HackathonCard from "../components/HackathonCard";

const Home = () => {
  const [hackathons, setHackathons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchHackathons();
  }, []);

  const fetchHackathons = async () => {
    try {
      setLoading(true);
      const data = await getHackathons();
      setHackathons(data);
      setLoading(false);
    } catch (err) {
      setError("Failed to load hackathons.");
      setLoading(false);
    }
  };

  if (loading) return <div>Loading hackathons...</div>;
  if (error) return <div className="alert-error">{error}</div>;

  return (
    <div>
      <h2>Explore Hackathons</h2>
      <p className="text-muted">Browse active events and submit your project solutions.</p>

      {hackathons.length === 0 ? (
        <p style={{ marginTop: "20px" }}>No hackathons currently available.</p>
      ) : (
        <div className="card-grid">
          {hackathons.map((hackathon) => (
            <HackathonCard key={hackathon.id} hackathon={hackathon} />
          ))}
        </div>
      )}
    </div>
  );
};

export default Home;
