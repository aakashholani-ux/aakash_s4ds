import React, { useState } from "react";
import { submitProject } from "../services/api";

const SubmissionForm = ({ hackathonId, onSubmitSuccess }) => {
  const [formData, setFormData] = useState({
    teamName: "",
    projectName: "",
    githubUrl: "",
    demoUrl: "",
    description: ""
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!formData.teamName || !formData.projectName || !formData.githubUrl || !formData.description) {
      setError("Please fill in all required fields.");
      return;
    }

    try {
      setLoading(true);
      await submitProject({
        hackathonId,
        ...formData
      });
      setLoading(false);
      if (onSubmitSuccess) {
        onSubmitSuccess();
      }
    } catch (err) {
      setLoading(false);
      setError(err.response?.data?.message || "Failed to submit project. Please try again.");
    }
  };

  return (
    <form className="form-container" onSubmit={handleSubmit}>
      {error && <div className="alert-error">{error}</div>}

      <div className="form-group">
        <label htmlFor="teamName">Team Name *</label>
        <input
          type="text"
          id="teamName"
          name="teamName"
          value={formData.teamName}
          onChange={handleChange}
          placeholder="e.g. Code Ninjas"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="projectName">Project Name *</label>
        <input
          type="text"
          id="projectName"
          name="projectName"
          value={formData.projectName}
          onChange={handleChange}
          placeholder="e.g. Smart Energy Dashboard"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="githubUrl">GitHub Repository Link *</label>
        <input
          type="url"
          id="githubUrl"
          name="githubUrl"
          value={formData.githubUrl}
          onChange={handleChange}
          placeholder="https://github.com/username/project"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="demoUrl">Demo Video Link</label>
        <input
          type="url"
          id="demoUrl"
          name="demoUrl"
          value={formData.demoUrl}
          onChange={handleChange}
          placeholder="https://youtube.com/watch?v=..."
        />
      </div>

      <div className="form-group">
        <label htmlFor="description">Project Description *</label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Briefly describe what your project does and technologies used..."
          required
        />
      </div>

      <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: "100%" }}>
        {loading ? "Submitting..." : "Submit Project"}
      </button>
    </form>
  );
};

export default SubmissionForm;
