import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { getHackathonById } from "../services/api";
import SubmissionForm from "../components/SubmissionForm";

const SubmitProject = () => {
  const { id } = useParams();
  const [hackathon, setHackathon] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHackathon();
  }, [id]);

  const fetchHackathon = async () => {
    try {
      setLoading(true);
      const data = await getHackathonById(id);
      setHackathon(data);
      setLoading(false);
    } catch (err) {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2 style={{ textAlign: "center", marginBottom: "5px" }}>
        Submit Project for {hackathon ? hackathon.title : `Hackathon #${id}`}
      </h2>
      <p className="text-muted" style={{ textAlign: "center", marginBottom: "25px" }}>
        Enter your team details and repository link below.
      </p>

      {submitted ? (
        <div style={{ textAlign: "center", marginTop: "30px" }}>
          <div className="alert-success" style={{ fontSize: "1.2rem", fontWeight: "bold", padding: "20px" }}>
            Submission Successful
          </div>
          <div style={{ marginTop: "20px" }}>
            <Link to="/" className="btn btn-primary" style={{ marginRight: "10px" }}>
              Back to Hackathons
            </Link>
            <Link to={`/hackathon/${id}`} className="btn btn-secondary">
              View Hackathon Details
            </Link>
          </div>
        </div>
      ) : (
        <SubmissionForm hackathonId={id} onSubmitSuccess={() => setSubmitted(true)} />
      )}
    </div>
  );
};

export default SubmitProject;
