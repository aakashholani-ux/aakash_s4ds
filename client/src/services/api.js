import axios from "axios";

const API_BASE_URL = "/api";

// Fetch all hackathons
export const getHackathons = async () => {
  const response = await axios.get(`${API_BASE_URL}/hackathons`);
  return response.data;
};

// Create a new hackathon
export const createHackathon = async (hackathonData) => {
  const response = await axios.post(`${API_BASE_URL}/hackathons`, hackathonData);
  return response.data;
};

// Fetch single hackathon by ID
export const getHackathonById = async (id) => {
  const response = await axios.get(`${API_BASE_URL}/hackathons/${id}`);
  return response.data;
};

// Update existing hackathon
export const updateHackathon = async (id, hackathonData) => {
  const response = await axios.put(
    `${API_BASE_URL}/hackathons/${id}`,
    hackathonData
  );
  return response.data;
};

// Delete hackathon
export const deleteHackathon = async (id) => {
  const response = await axios.delete(`${API_BASE_URL}/hackathons/${id}`);
  return response.data;
};

// Submit a project
export const submitProject = async (submissionData) => {
  const response = await axios.post(
    `${API_BASE_URL}/submissions`,
    submissionData
  );
  return response.data;
};

// Get all submissions
export const getSubmissions = async () => {
  const response = await axios.get(`${API_BASE_URL}/submissions`);
  return response.data;
};

// Get submissions by hackathon ID
export const getSubmissionsByHackathon = async (hackathonId) => {
  const response = await axios.get(
    `${API_BASE_URL}/submissions/${hackathonId}`
  );
  return response.data;
};