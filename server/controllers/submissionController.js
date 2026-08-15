const submissionsInMemory = require("../data/submissions");
const hackathonsInMemory = require("../data/hackathons");
const SubmissionModel = require("../models/Submission");
const HackathonModel = require("../models/Hackathon");
const { getIsConnected } = require("../config/db");

// Create a project submission
const createSubmission = async (req, res) => {
  try {
    const {
      hackathonId,
      teamName,
      projectName,
      githubUrl,
      demoUrl,
      description
    } = req.body;

    // Validate required fields
    if (
      !hackathonId ||
      !teamName ||
      !projectName ||
      !githubUrl ||
      !description
    ) {
      return res.status(400).json({
        message:
          "hackathonId, teamName, projectName, githubUrl, and description are required."
      });
    }

    const parsedHackathonId = parseInt(hackathonId, 10);

    if (isNaN(parsedHackathonId)) {
      return res.status(400).json({
        message: "Invalid hackathon ID."
      });
    }

    // MongoDB path
    if (getIsConnected()) {
      const hackathonExists = await HackathonModel.findOne({
        id: parsedHackathonId
      });

      if (!hackathonExists) {
        return res.status(404).json({
          message: "Associated hackathon does not exist."
        });
      }

      // Check submission deadline
      if (!hackathonExists.submissionDeadline) {
        return res.status(400).json({
          message: "Submission deadline has not been configured."
        });
      }

      const deadline = new Date(hackathonExists.submissionDeadline);

      if (isNaN(deadline.getTime())) {
        return res.status(400).json({
          message: "Invalid submission deadline."
        });
      }

      if (new Date() > deadline) {
        return res.status(400).json({
          message:
            "Submissions are closed. The submission deadline has passed."
        });
      }

      const totalCount = await SubmissionModel.countDocuments();

      const newSubmission = await SubmissionModel.create({
        id: totalCount + 1,
        hackathonId: parsedHackathonId,
        teamName,
        projectName,
        githubUrl,
        demoUrl: demoUrl || "",
        description
      });

      return res.status(201).json({
        message: "Submission Successful",
        submission: newSubmission
      });
    }

    // Fallback to in-memory store
    const hackathonExists = hackathonsInMemory.find(
      (h) => h.id === parsedHackathonId
    );

    if (!hackathonExists) {
      return res.status(404).json({
        message: "Associated hackathon does not exist."
      });
    }

    // Check submission deadline
    if (!hackathonExists.submissionDeadline) {
      return res.status(400).json({
        message: "Submission deadline has not been configured."
      });
    }

    const deadline = new Date(hackathonExists.submissionDeadline);

    if (isNaN(deadline.getTime())) {
      return res.status(400).json({
        message: "Invalid submission deadline."
      });
    }

    if (new Date() > deadline) {
      return res.status(400).json({
        message:
          "Submissions are closed. The submission deadline has passed."
      });
    }

    const newId =
      submissionsInMemory.length > 0
        ? Math.max(...submissionsInMemory.map((s) => s.id)) + 1
        : 1;

    const newSubmission = {
      id: newId,
      hackathonId: parsedHackathonId,
      teamName,
      projectName,
      githubUrl,
      demoUrl: demoUrl || "",
      description,
      submittedAt: new Date().toISOString()
    };

    submissionsInMemory.push(newSubmission);

    return res.status(201).json({
      message: "Submission Successful",
      submission: newSubmission
    });
  } catch (error) {
    console.error("Submission error:", error);

    return res.status(500).json({
      message: "Server error while processing submission."
    });
  }
};

// Read all submissions
const getAllSubmissions = async (req, res) => {
  try {
    if (getIsConnected()) {
      const dbSubmissions = await SubmissionModel.find();
      return res.status(200).json(dbSubmissions);
    }

    return res.status(200).json(submissionsInMemory);
  } catch (error) {
    return res.status(500).json({
      message: "Server error while fetching submissions."
    });
  }
};

// Read submissions belonging to a specific hackathon
const getSubmissionsByHackathon = async (req, res) => {
  try {
    const hackathonId = parseInt(req.params.hackathonId, 10);

    if (getIsConnected()) {
      const dbSubmissions = await SubmissionModel.find({
        hackathonId
      });

      return res.status(200).json(dbSubmissions);
    }

    const filtered = submissionsInMemory.filter(
      (s) => s.hackathonId === hackathonId
    );

    return res.status(200).json(filtered);
  } catch (error) {
    return res.status(500).json({
      message: "Server error while fetching hackathon submissions."
    });
  }
};

module.exports = {
  createSubmission,
  getAllSubmissions,
  getSubmissionsByHackathon
};