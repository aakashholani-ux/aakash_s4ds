import React, { useEffect, useState } from "react";
import {
  getHackathons,
  createHackathon,
  updateHackathon,
  deleteHackathon
} from "../services/api";

const OrganizerDashboard = () => {
  const [hackathons, setHackathons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Edit modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingHackathon, setEditingHackathon] = useState(null);

  // Create modal state
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [createFormData, setCreateFormData] = useState({
    title: "",
    description: "",
    date: "",
    submissionDeadline: "",
    location: "",
    prizePool: ""
  });

  // Edit form state
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    date: "",
    submissionDeadline: "",
    rules: "",
    timeline: "",
    location: "",
    prizePool: ""
  });

  useEffect(() => {
    fetchData();
  }, []);

  // Fetch all hackathons
  const fetchData = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getHackathons();
      setHackathons(data);
    } catch (err) {
      setError("Failed to fetch hackathons.");
    } finally {
      setLoading(false);
    }
  };

  // -------------------------
  // Create Hackathon
  // -------------------------

  const handleOpenCreateModal = () => {
    setCreateFormData({
      title: "",
      description: "",
      date: "",
      submissionDeadline: "",
      location: "",
      prizePool: ""
    });

    setIsCreateModalOpen(true);
  };

  const handleCloseCreateModal = () => {
    setIsCreateModalOpen(false);
  };

  const handleCreateInputChange = (e) => {
    const { name, value } = e.target;

    setCreateFormData((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();

    if (!createFormData.submissionDeadline) {
      alert("Please select a submission deadline.");
      return;
    }

    const deadline = new Date(createFormData.submissionDeadline);

    if (isNaN(deadline.getTime())) {
      alert("Please enter a valid submission deadline.");
      return;
    }

    if (deadline <= new Date()) {
      alert("Submission deadline must be in the future.");
      return;
    }

    try {
      await createHackathon(createFormData);

      alert("Hackathon created successfully!");

      handleCloseCreateModal();

      await fetchData();
    } catch (err) {
      alert(
        "Error creating hackathon: " +
          (err.response?.data?.message || err.message)
      );
    }
  };

  // -------------------------
  // Edit Hackathon
  // -------------------------

  const handleOpenEditModal = (hackathon) => {
    setEditingHackathon(hackathon);

    let deadline = "";

    if (hackathon.submissionDeadline) {
      const date = new Date(hackathon.submissionDeadline);

      if (!isNaN(date.getTime())) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        const hours = String(date.getHours()).padStart(2, "0");
        const minutes = String(date.getMinutes()).padStart(2, "0");

        deadline = `${year}-${month}-${day}T${hours}:${minutes}`;
      }
    }

    setFormData({
      title: hackathon.title || "",
      description: hackathon.description || "",
      date: hackathon.date || "",
      submissionDeadline: deadline,
      rules: hackathon.rules || "",
      timeline: hackathon.timeline || "",
      location: hackathon.location || "",
      prizePool: hackathon.prizePool || ""
    });

    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingHackathon(null);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!editingHackathon) return;

    if (!formData.submissionDeadline) {
      alert("Please select a submission deadline.");
      return;
    }

    const deadline = new Date(formData.submissionDeadline);

    if (isNaN(deadline.getTime())) {
      alert("Please enter a valid submission deadline.");
      return;
    }

    if (deadline <= new Date()) {
      alert("Submission deadline must be in the future.");
      return;
    }

    try {
      await updateHackathon(editingHackathon.id, formData);

      alert("Hackathon updated successfully!");

      handleCloseModal();

      await fetchData();
    } catch (err) {
      alert(
        "Error updating hackathon: " +
          (err.response?.data?.message || err.message)
      );
    }
  };

  // -------------------------
  // Delete Hackathon
  // -------------------------

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this hackathon?")) {
      return;
    }

    try {
      await deleteHackathon(id);

      await fetchData();
    } catch (err) {
      alert(
        "Failed to delete hackathon: " +
          (err.response?.data?.message || err.message)
      );
    }
  };

  // Format deadline for display
  const formatDeadline = (deadline) => {
    if (!deadline) return "Not set";

    const date = new Date(deadline);

    if (isNaN(date.getTime())) return "Invalid date";

    return date.toLocaleString();
  };

  if (loading) {
    return <div>Loading dashboard...</div>;
  }

  return (
    <div>
      {/* Dashboard Header */}
      <div
        style={{
          marginBottom: "20px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center"
        }}
      >
        <div>
          <h2>Organizer Dashboard</h2>

          <p className="text-muted">
            Manage existing hackathons (Edit details or Delete).
          </p>
        </div>

        <button
          onClick={handleOpenCreateModal}
          className="btn btn-primary"
        >
          + Create Hackathon
        </button>
      </div>

      {error && <div className="alert-error">{error}</div>}

      {/* Hackathon Table */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Date</th>
              <th>Submission Deadline</th>
              <th>Location</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {hackathons.length === 0 ? (
              <tr>
                <td
                  colSpan="6"
                  style={{
                    textAlign: "center",
                    color: "#64748b"
                  }}
                >
                  No hackathons found.
                </td>
              </tr>
            ) : (
              hackathons.map((h) => (
                <tr key={h.id}>
                  <td>#{h.id}</td>

                  <td>
                    <strong>{h.title}</strong>
                  </td>

                  <td>{h.date}</td>

                  <td>{formatDeadline(h.submissionDeadline)}</td>

                  <td>{h.location}</td>

                  <td>
                    <div className="btn-group">
                      <button
                        onClick={() => handleOpenEditModal(h)}
                        className="btn btn-secondary"
                      >
                        Edit
                      </button>

                      <button
                        onClick={() => handleDelete(h.id)}
                        className="btn btn-danger"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Create Hackathon Modal */}
      {isCreateModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>Create Hackathon</h3>

            <form
              onSubmit={handleCreateSubmit}
              style={{ marginTop: "15px" }}
            >
              <div className="form-group">
                <label>Title *</label>

                <input
                  type="text"
                  name="title"
                  value={createFormData.title}
                  onChange={handleCreateInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Description *</label>

                <textarea
                  name="description"
                  value={createFormData.description}
                  onChange={handleCreateInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Date *</label>

                <input
                  type="date"
                  name="date"
                  value={createFormData.date}
                  onChange={handleCreateInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Submission Deadline *</label>

                <input
                  type="datetime-local"
                  name="submissionDeadline"
                  value={createFormData.submissionDeadline}
                  onChange={handleCreateInputChange}
                  required
                />

                <small className="text-muted">
                  Participants will not be able to submit after this time.
                </small>
              </div>

              <div className="form-group">
                <label>Location</label>

                <input
                  type="text"
                  name="location"
                  value={createFormData.location}
                  onChange={handleCreateInputChange}
                  placeholder="e.g. Online or Tech Hub"
                />
              </div>

              <div className="form-group">
                <label>Prize Pool</label>

                <input
                  type="text"
                  name="prizePool"
                  value={createFormData.prizePool}
                  onChange={handleCreateInputChange}
                  placeholder="e.g. ₹50,000"
                />
              </div>

              <div
                className="btn-group"
                style={{
                  justifyContent: "flex-end",
                  marginTop: "20px"
                }}
              >
                <button
                  type="button"
                  onClick={handleCloseCreateModal}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="btn btn-primary"
                >
                  Create Hackathon
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Hackathon Modal */}
      {isModalOpen && editingHackathon && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>Edit Hackathon #{editingHackathon.id}</h3>

            <form
              onSubmit={handleSubmit}
              style={{ marginTop: "15px" }}
            >
              <div className="form-group">
                <label>Title *</label>

                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Description *</label>

                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Date *</label>

                <input
                  type="date"
                  name="date"
                  value={formData.date}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Submission Deadline *</label>

                <input
                  type="datetime-local"
                  name="submissionDeadline"
                  value={formData.submissionDeadline}
                  onChange={handleInputChange}
                  required
                />

                <small className="text-muted">
                  Participants will not be able to submit after this time.
                </small>
              </div>

              <div className="form-group">
                <label>Location</label>

                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  placeholder="e.g. Online or Tech Hub"
                />
              </div>

              <div className="form-group">
                <label>Prize Pool</label>

                <input
                  type="text"
                  name="prizePool"
                  value={formData.prizePool}
                  onChange={handleInputChange}
                  placeholder="e.g. ₹50,000"
                />
              </div>

              <div
                className="btn-group"
                style={{
                  justifyContent: "flex-end",
                  marginTop: "20px"
                }}
              >
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="btn btn-primary"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrganizerDashboard;