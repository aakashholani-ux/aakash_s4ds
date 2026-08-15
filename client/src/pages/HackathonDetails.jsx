import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getHackathonById } from "../services/api";

const HackathonDetails = () => {
  const { id } = useParams();

  const [hackathon, setHackathon] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [timeLeft, setTimeLeft] = useState(null);
  const [deadlinePassed, setDeadlinePassed] = useState(false);

  useEffect(() => {
    fetchDetails();
  }, [id]);

  const fetchDetails = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getHackathonById(id);

      setHackathon(data);
      setLoading(false);
    } catch (err) {
      setError("Failed to fetch hackathon details.");
      setLoading(false);
    }
  };

  // Countdown timer
  useEffect(() => {
    if (!hackathon?.submissionDeadline) {
      return;
    }

    const deadline = new Date(hackathon.submissionDeadline);

    if (isNaN(deadline.getTime())) {
      return;
    }

    const updateCountdown = () => {
      const now = new Date();
      const difference = deadline.getTime() - now.getTime();

      if (difference <= 0) {
        setTimeLeft({
          days: 0,
          hours: 0,
          minutes: 0,
          seconds: 0
        });

        setDeadlinePassed(true);
        return;
      }

      const days = Math.floor(
        difference / (1000 * 60 * 60 * 24)
      );

      const hours = Math.floor(
        (difference / (1000 * 60 * 60)) % 24
      );

      const minutes = Math.floor(
        (difference / (1000 * 60)) % 60
      );

      const seconds = Math.floor(
        (difference / 1000) % 60
      );

      setTimeLeft({
        days,
        hours,
        minutes,
        seconds
      });

      setDeadlinePassed(false);
    };

    updateCountdown();

    const interval = setInterval(updateCountdown, 1000);

    return () => clearInterval(interval);
  }, [hackathon]);

  const formatNumber = (number) => {
    return String(number).padStart(2, "0");
  };

  const formatDeadline = (deadline) => {
    if (!deadline) return "Not specified";

    const date = new Date(deadline);

    if (isNaN(date.getTime())) {
      return "Invalid deadline";
    }

    return date.toLocaleString();
  };

  if (loading) {
    return <div>Loading hackathon details...</div>;
  }

  if (error) {
    return <div className="alert-error">{error}</div>;
  }

  if (!hackathon) {
    return <div>Hackathon not found.</div>;
  }

  return (
    <div className="detail-container">
      <h1 style={{ marginBottom: "10px" }}>
        {hackathon.title}
      </h1>

      <p
        className="text-muted"
        style={{ marginBottom: "20px" }}
      >
        📅 Date: {hackathon.date} | 📍 Venue:{" "}
        {hackathon.location} | 🏆 Prize Pool:{" "}
        {hackathon.prizePool}
      </p>

      <div className="detail-section">
        <h3>Description</h3>
        <p>{hackathon.description}</p>
      </div>

      <div className="detail-section">
        <h3>Rules</h3>
        <p style={{ whiteSpace: "pre-line" }}>
          {hackathon.rules}
        </p>
      </div>

      <div className="detail-section">
        <h3>Timeline</h3>
        <p>{hackathon.timeline}</p>
      </div>

      <div className="detail-section">
        <h3>Prize</h3>
        <p>{hackathon.prizePool}</p>
      </div>

      <div className="detail-section">
        <h3>Venue</h3>
        <p>{hackathon.location}</p>
      </div>

      {/* Submission Deadline */}
      <div
        className="detail-section"
        style={{
          marginTop: "25px",
          padding: "25px",
          borderRadius: "10px",
          textAlign: "center",
          background: deadlinePassed
            ? "#fef2f2"
            : "#eff6ff",
          border: deadlinePassed
            ? "1px solid #fecaca"
            : "1px solid #bfdbfe"
        }}
      >
        {deadlinePassed ? (
          <>
            <h3 style={{ marginBottom: "10px" }}>
              🔒 Submission Deadline Passed
            </h3>

            <p
              style={{
                margin: 0,
                color: "#b91c1c",
                fontWeight: "600"
              }}
            >
              Submissions are now closed.
            </p>

            <p
              className="text-muted"
              style={{ marginTop: "8px" }}
            >
              Deadline:{" "}
              {formatDeadline(hackathon.submissionDeadline)}
            </p>
          </>
        ) : (
          <>
            <h3 style={{ marginBottom: "5px" }}>
              ⏳ Submission Deadline
            </h3>

            <p
              className="text-muted"
              style={{ marginBottom: "20px" }}
            >
              {formatDeadline(hackathon.submissionDeadline)}
            </p>

            {timeLeft && (
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  gap: "12px",
                  flexWrap: "wrap"
                }}
              >
                <div className="countdown-box">
                  <strong>{timeLeft.days}</strong>
                  <span>Days</span>
                </div>

                <div className="countdown-box">
                  <strong>
                    {formatNumber(timeLeft.hours)}
                  </strong>
                  <span>Hours</span>
                </div>

                <div className="countdown-box">
                  <strong>
                    {formatNumber(timeLeft.minutes)}
                  </strong>
                  <span>Minutes</span>
                </div>

                <div className="countdown-box">
                  <strong>
                    {formatNumber(timeLeft.seconds)}
                  </strong>
                  <span>Seconds</span>
                </div>
              </div>
            )}

            <p
              style={{
                marginTop: "20px",
                marginBottom: 0,
                color: "#166534",
                fontWeight: "600"
              }}
            >
              ✓ Submissions are open
            </p>
          </>
        )}
      </div>

      {/* Submit Button */}
      <div
        style={{
          marginTop: "30px",
          borderTop: "1px solid #e2e8f0",
          paddingTop: "20px"
        }}
      >
        {deadlinePassed ? (
          <button
            className="btn btn-secondary"
            disabled
            style={{
              fontSize: "1rem",
              padding: "10px 20px",
              opacity: 0.6,
              cursor: "not-allowed"
            }}
          >
            🔒 Submissions Closed
          </button>
        ) : (
          <Link
            to={`/submit/${hackathon.id}`}
            className="btn btn-primary"
            style={{
              fontSize: "1rem",
              padding: "10px 20px"
            }}
          >
            Submit Project
          </Link>
        )}
      </div>
    </div>
  );
};

export default HackathonDetails;