const express = require("express");
const router = express.Router();
const {
  createSubmission,
  getAllSubmissions,
  getSubmissionsByHackathon
} = require("../controllers/submissionController");

// Submission routes
router.post("/", createSubmission);
router.get("/", getAllSubmissions);
router.get("/:hackathonId", getSubmissionsByHackathon);

module.exports = router;
