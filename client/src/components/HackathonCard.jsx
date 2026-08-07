import React from "react";
import { Link } from "react-router-dom";

const HackathonCard = ({ hackathon }) => {
  return (
    <div className="card">
      <div>
        <h3 className="card-title">{hackathon.title}</h3>
        <p className="card-description">{hackathon.description}</p>
        <p className="card-meta">
          <strong>Date:</strong> {hackathon.date}
        </p>
        <p className="card-meta">
          <strong>Location:</strong> {hackathon.location}
        </p>
        <p className="card-meta">
          <strong>Prize Pool:</strong> {hackathon.prizePool}
        </p>
      </div>
      <div style={{ marginTop: "15px" }}>
        <Link to={`/hackathon/${hackathon.id}`} className="btn btn-primary">
          View Details
        </Link>
      </div>
    </div>
  );
};

export default HackathonCard;
